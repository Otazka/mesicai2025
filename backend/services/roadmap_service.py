"""
Roadmap service for RAG integration with ChromaDB
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class RoadmapService:
    """Service for roadmap content retrieval using RAG"""
    
    def __init__(self):
        """Initialize roadmap service"""
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "roadmap_content"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception as e:
            logger.error(f"Error accessing collection: {e}")
            self.collection = None
    
    def search_roadmap_content(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search roadmap content using semantic search"""
        if not self.collection:
            logger.error("Collection not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": 1 - distance,  # Convert distance to relevance score
                    "rank": i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching roadmap content: {e}")
            return []
    
    def get_skill_explanation(self, skill: str, topic: str) -> Dict[str, Any]:
        """Get detailed explanation of a skill from roadmap content"""
        query = f"{topic} {skill} explanation guide tutorial"
        results = self.search_roadmap_content(query, n_results=3)
        
        if not results:
            return {
                "explanation": f"No specific information found about {skill} in {topic}.",
                "resources": [],
                "related_topics": []
            }
        
        # Combine top results
        explanation_parts = []
        resources = []
        related_topics = set()
        
        for result in results:
            explanation_parts.append(result["content"])
            
            # Extract resources from metadata
            if "roadmap" in result["metadata"]:
                roadmap = result["metadata"]["roadmap"]
                resources.append({
                    "type": "roadmap",
                    "title": f"{roadmap.title()} Roadmap",
                    "url": f"https://roadmap.sh/{roadmap}",
                    "description": f"Complete {roadmap} development roadmap"
                })
            
            # Extract related topics
            if "section_title" in result["metadata"]:
                related_topics.add(result["metadata"]["section_title"])
        
        return {
            "explanation": "\n\n".join(explanation_parts),
            "resources": resources,
            "related_topics": list(related_topics)
        }
    
    def get_learning_resources(self, topic: str, skill: str) -> List[Dict[str, str]]:
        """Get learning resources for a specific skill"""
        query = f"{topic} {skill} learn tutorial course practice"
        results = self.search_roadmap_content(query, n_results=5)
        
        resources = []
        seen_urls = set()
        
        for result in results:
            # Extract roadmap information
            if "roadmap" in result["metadata"]:
                roadmap = result["metadata"]["roadmap"]
                url = f"https://roadmap.sh/{roadmap}"
                
                if url not in seen_urls:
                    resources.append({
                        "type": "roadmap",
                        "title": f"{roadmap.title()} Roadmap",
                        "url": url,
                        "description": f"Complete {roadmap} development roadmap from roadmap.sh"
                    })
                    seen_urls.add(url)
            
            # Add content as a resource if it's substantial
            if len(result["content"]) > 100:
                resources.append({
                    "type": "guide",
                    "title": f"{skill} Guide",
                    "url": "#",  # Could be extracted from content if available
                    "description": result["content"][:200] + "..."
                })
        
        return resources[:5]  # Limit to 5 resources
    
    def get_roadmap_structure(self, roadmap_type: str) -> Dict[str, Any]:
        """Get the structure of a specific roadmap"""
        query = f"{roadmap_type} roadmap structure sections topics"
        results = self.search_roadmap_content(query, n_results=10)
        
        if not results:
            return {"sections": [], "description": f"No roadmap structure found for {roadmap_type}"}
        
        # Extract sections and topics
        sections = {}
        description_parts = []
        
        for result in results:
            if "section_title" in result["metadata"]:
                section_title = result["metadata"]["section_title"]
                if section_title not in sections:
                    sections[section_title] = {
                        "title": section_title,
                        "topics": [],
                        "description": ""
                    }
                
                # Add topics
                if "title" in result["metadata"] and result["metadata"]["title"] != section_title:
                    sections[section_title]["topics"].append(result["metadata"]["title"])
                
                # Add description
                if result["content"]:
                    sections[section_title]["description"] += result["content"][:200] + "..."
            
            # Collect description parts
            if result["content"] and len(result["content"]) > 50:
                description_parts.append(result["content"][:100])
        
        return {
            "sections": list(sections.values()),
            "description": " ".join(description_parts[:3])  # Combine first 3 parts
        }
    
    def get_related_skills(self, skill: str, topic: str) -> List[str]:
        """Get skills related to the given skill"""
        query = f"{topic} {skill} related skills prerequisites dependencies"
        results = self.search_roadmap_content(query, n_results=5)
        
        related_skills = set()
        
        for result in results:
            # Extract related skills from content
            content = result["content"].lower()
            
            # Look for common skill patterns
            skill_patterns = [
                "prerequisites", "before learning", "related to", "similar to",
                "also includes", "part of", "builds on"
            ]
            
            for pattern in skill_patterns:
                if pattern in content:
                    # Extract text after pattern
                    start_idx = content.find(pattern)
                    if start_idx != -1:
                        after_pattern = content[start_idx + len(pattern):start_idx + len(pattern) + 200]
                        # Simple extraction of potential skills (could be improved with NLP)
                        words = after_pattern.split()
                        for word in words:
                            if len(word) > 3 and word.isalpha():
                                related_skills.add(word.title())
        
        return list(related_skills)[:5]  # Limit to 5 related skills
    
    def get_skill_difficulty_level(self, skill: str, topic: str) -> str:
        """Determine the difficulty level of a skill based on roadmap content"""
        query = f"{topic} {skill} difficulty level beginner intermediate advanced"
        results = self.search_roadmap_content(query, n_results=3)
        
        if not results:
            return "intermediate"  # Default
        
        # Analyze content for difficulty indicators
        content = " ".join([result["content"].lower() for result in results])
        
        difficulty_indicators = {
            "beginner": ["basic", "fundamental", "introduction", "getting started", "first steps"],
            "intermediate": ["intermediate", "moderate", "some experience", "basic knowledge"],
            "advanced": ["advanced", "expert", "complex", "sophisticated", "mastery"]
        }
        
        scores = {"beginner": 0, "intermediate": 0, "advanced": 0}
        
        for level, indicators in difficulty_indicators.items():
            for indicator in indicators:
                scores[level] += content.count(indicator)
        
        # Return level with highest score
        return max(scores, key=scores.get)
    
    def search_by_roadmap_type(self, roadmap_type: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search within a specific roadmap type"""
        if not self.collection:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search with metadata filter
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"roadmap": roadmap_type}
            )
            
            # Format results
            formatted_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "relevance_score": 1 - distance,
                    "rank": i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching by roadmap type: {e}")
            return []
    
    def get_roadmap_statistics(self) -> Dict[str, Any]:
        """Get statistics about the roadmap content"""
        if not self.collection:
            return {"error": "Collection not available"}
        
        try:
            count = self.collection.count()
            
            # Get sample of all documents to analyze
            sample = self.collection.get(limit=100)
            
            roadmap_types = set()
            section_types = set()
            
            for metadata in sample['metadatas']:
                if 'roadmap' in metadata:
                    roadmap_types.add(metadata['roadmap'])
                if 'type' in metadata:
                    section_types.add(metadata['type'])
            
            return {
                "total_documents": count,
                "roadmap_types": list(roadmap_types),
                "content_types": list(section_types),
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Error getting roadmap statistics: {e}")
            return {"error": str(e)}
