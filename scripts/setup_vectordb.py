"""
Script to set up ChromaDB vector database with roadmap content
"""

import json
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDBSetup:
    """Setup ChromaDB vector database"""
    
    def __init__(self, persist_directory: str = "chroma_db"):
        """Initialize vector database setup"""
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
    def load_roadmap_chunks(self, chunks_file: str = "backend/data/roadmap_cache/roadmap_chunks.json") -> List[Dict[str, Any]]:
        """Load roadmap chunks from JSON file"""
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
            return chunks
        except FileNotFoundError:
            logger.error(f"Chunks file not found: {chunks_file}")
            logger.info("Please run scrape_roadmap.py first to create the chunks file")
            return []
        except Exception as e:
            logger.error(f"Error loading chunks: {e}")
            return []
    
    def create_collection(self, collection_name: str = "roadmap_content") -> chromadb.Collection:
        """Create or get ChromaDB collection"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Found existing collection: {collection_name}")
            return collection
        except:
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Roadmap.sh content for IT skills development"}
            )
            logger.info(f"Created new collection: {collection_name}")
            return collection
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using SentenceTransformer"""
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts).tolist()
        logger.info("Embeddings generated successfully")
        return embeddings
    
    def populate_collection(self, chunks: List[Dict[str, Any]], collection_name: str = "roadmap_content"):
        """Populate ChromaDB collection with roadmap chunks"""
        if not chunks:
            logger.error("No chunks to populate collection")
            return
        
        # Create or get collection
        collection = self.create_collection(collection_name)
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])
            ids.append(f"chunk_{i}")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(documents)
        
        # Add to collection
        logger.info(f"Adding {len(documents)} documents to collection...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        logger.info(f"Successfully populated collection with {len(documents)} documents")
    
    def test_collection(self, collection_name: str = "roadmap_content", query: str = "Python OOP"):
        """Test the collection with a sample query"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            logger.info(f"Test query: '{query}'")
            logger.info("Top 3 results:")
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                logger.info(f"\n{i+1}. Distance: {distance:.4f}")
                logger.info(f"   Metadata: {metadata}")
                logger.info(f"   Content: {doc[:200]}...")
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing collection: {e}")
            return None
    
    def get_collection_stats(self, collection_name: str = "roadmap_content"):
        """Get statistics about the collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            logger.info(f"Collection '{collection_name}' statistics:")
            logger.info(f"  - Total documents: {count}")
            
            # Get sample metadata to understand structure
            sample = collection.get(limit=1)
            if sample['metadatas']:
                logger.info(f"  - Sample metadata keys: {list(sample['metadatas'][0].keys())}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return 0
    
    def reset_collection(self, collection_name: str = "roadmap_content"):
        """Reset the collection (delete all data)"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")


def main():
    """Main function to set up vector database"""
    logger.info("Setting up ChromaDB vector database...")
    
    # Initialize setup
    setup = VectorDBSetup()
    
    # Load roadmap chunks
    chunks = setup.load_roadmap_chunks()
    
    if not chunks:
        logger.error("No chunks found. Please run scrape_roadmap.py first.")
        return
    
    # Reset collection if it exists (for fresh setup)
    setup.reset_collection()
    
    # Populate collection
    setup.populate_collection(chunks)
    
    # Get collection statistics
    count = setup.get_collection_stats()
    
    # Test the collection
    logger.info("\nTesting collection with sample queries...")
    setup.test_collection(query="Python object-oriented programming")
    setup.test_collection(query="sorting algorithms")
    setup.test_collection(query="backend development")
    
    print("\n" + "="*50)
    print("VECTOR DATABASE SETUP COMPLETE")
    print("="*50)
    print(f"Collection created with {count} documents")
    print("Ready for RAG queries!")
    
    # Create a simple test script
    test_script = """
# Test script for vector database
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("roadmap_content")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test query
query = "Python OOP concepts"
query_embedding = model.encode([query]).tolist()[0]

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("Query:", query)
for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"\\n{i+1}. {metadata['title']}")
    print(f"   {doc[:200]}...")
"""
    
    with open("test_vectordb.py", "w") as f:
        f.write(test_script)
    
    logger.info("Created test_vectordb.py for testing the vector database")


if __name__ == "__main__":
    main()
