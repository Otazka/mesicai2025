
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
    print(f"\n{i+1}. {metadata['title']}")
    print(f"   {doc[:200]}...")
