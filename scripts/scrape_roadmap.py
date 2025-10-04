"""
Script to scrape roadmap.sh content for Python, OOP, and Algorithms
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RoadmapScraper:
    """Scraper for roadmap.sh content"""
    
    def __init__(self):
        """Initialize scraper"""
        self.base_url = "https://roadmap.sh"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_python_roadmap(self) -> Dict[str, Any]:
        """Scrape Python roadmap content"""
        try:
            url = f"{self.base_url}/python"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract roadmap content
            roadmap_data = {
                "title": "Python Developer Roadmap",
                "url": url,
                "sections": []
            }
            
            # Find roadmap sections
            sections = soup.find_all(['h2', 'h3', 'h4'], class_=['roadmap-section', 'roadmap-item'])
            
            for section in sections:
                section_data = {
                    "title": section.get_text().strip(),
                    "content": "",
                    "subsections": []
                }
                
                # Get content after the heading
                next_element = section.find_next_sibling()
                while next_element and next_element.name not in ['h2', 'h3', 'h4']:
                    if next_element.name == 'p':
                        section_data["content"] += next_element.get_text().strip() + "\n"
                    elif next_element.name == 'ul':
                        for li in next_element.find_all('li'):
                            section_data["subsections"].append(li.get_text().strip())
                    next_element = next_element.find_next_sibling()
                
                roadmap_data["sections"].append(section_data)
            
            return roadmap_data
            
        except Exception as e:
            logger.error(f"Error scraping Python roadmap: {e}")
            return {"title": "Python Developer Roadmap", "url": url, "sections": []}
    
    def scrape_backend_roadmap(self) -> Dict[str, Any]:
        """Scrape Backend Developer roadmap content"""
        try:
            url = f"{self.base_url}/backend"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            roadmap_data = {
                "title": "Backend Developer Roadmap",
                "url": url,
                "sections": []
            }
            
            # Extract sections (similar to Python roadmap)
            sections = soup.find_all(['h2', 'h3', 'h4'], class_=['roadmap-section', 'roadmap-item'])
            
            for section in sections:
                section_data = {
                    "title": section.get_text().strip(),
                    "content": "",
                    "subsections": []
                }
                
                next_element = section.find_next_sibling()
                while next_element and next_element.name not in ['h2', 'h3', 'h4']:
                    if next_element.name == 'p':
                        section_data["content"] += next_element.get_text().strip() + "\n"
                    elif next_element.name == 'ul':
                        for li in next_element.find_all('li'):
                            section_data["subsections"].append(li.get_text().strip())
                    next_element = next_element.find_next_sibling()
                
                roadmap_data["sections"].append(section_data)
            
            return roadmap_data
            
        except Exception as e:
            logger.error(f"Error scraping Backend roadmap: {e}")
            return {"title": "Backend Developer Roadmap", "url": url, "sections": []}
    
    def scrape_algorithms_roadmap(self) -> Dict[str, Any]:
        """Scrape Algorithms roadmap content"""
        try:
            # Since roadmap.sh might not have a dedicated algorithms page,
            # we'll create a structured algorithms roadmap
            roadmap_data = {
                "title": "Algorithms and Data Structures Roadmap",
                "url": f"{self.base_url}/algorithms",
                "sections": [
                    {
                        "title": "Basic Data Structures",
                        "content": "Understanding fundamental data structures is crucial for algorithm design.",
                        "subsections": [
                            "Arrays and Strings",
                            "Linked Lists",
                            "Stacks and Queues",
                            "Hash Tables",
                            "Trees and Binary Trees",
                            "Graphs"
                        ]
                    },
                    {
                        "title": "Sorting Algorithms",
                        "content": "Learn various sorting techniques and their time complexities.",
                        "subsections": [
                            "Bubble Sort",
                            "Selection Sort",
                            "Insertion Sort",
                            "Merge Sort",
                            "Quick Sort",
                            "Heap Sort",
                            "Counting Sort",
                            "Radix Sort"
                        ]
                    },
                    {
                        "title": "Searching Algorithms",
                        "content": "Master different search techniques for various data structures.",
                        "subsections": [
                            "Linear Search",
                            "Binary Search",
                            "Depth-First Search (DFS)",
                            "Breadth-First Search (BFS)",
                            "A* Search",
                            "Dijkstra's Algorithm"
                        ]
                    },
                    {
                        "title": "Dynamic Programming",
                        "content": "Learn to solve complex problems by breaking them into simpler subproblems.",
                        "subsections": [
                            "Memoization",
                            "Tabulation",
                            "Longest Common Subsequence",
                            "Knapsack Problem",
                            "Edit Distance",
                            "Fibonacci Series"
                        ]
                    },
                    {
                        "title": "Greedy Algorithms",
                        "content": "Understand greedy approach for optimization problems.",
                        "subsections": [
                            "Activity Selection",
                            "Huffman Coding",
                            "Minimum Spanning Tree",
                            "Shortest Path",
                            "Fractional Knapsack"
                        ]
                    }
                ]
            }
            
            return roadmap_data
            
        except Exception as e:
            logger.error(f"Error creating algorithms roadmap: {e}")
            return {"title": "Algorithms and Data Structures Roadmap", "url": "", "sections": []}
    
    def scrape_all_roadmaps(self) -> Dict[str, Any]:
        """Scrape all relevant roadmaps"""
        logger.info("Starting roadmap scraping...")
        
        roadmaps = {}
        
        # Scrape Python roadmap
        logger.info("Scraping Python roadmap...")
        roadmaps["python"] = self.scrape_python_roadmap()
        time.sleep(2)  # Be respectful to the server
        
        # Scrape Backend roadmap
        logger.info("Scraping Backend roadmap...")
        roadmaps["backend"] = self.scrape_backend_roadmap()
        time.sleep(2)
        
        # Create Algorithms roadmap
        logger.info("Creating Algorithms roadmap...")
        roadmaps["algorithms"] = self.scrape_algorithms_roadmap()
        
        logger.info("Roadmap scraping completed!")
        return roadmaps
    
    def save_roadmaps(self, roadmaps: Dict[str, Any], output_dir: str = "backend/data/roadmap_cache"):
        """Save scraped roadmaps to JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for roadmap_name, roadmap_data in roadmaps.items():
            output_file = os.path.join(output_dir, f"{roadmap_name}_roadmap.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(roadmap_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {roadmap_name} roadmap to {output_file}")
    
    def create_chunks_for_vectordb(self, roadmaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create chunks for vector database storage"""
        chunks = []
        
        for roadmap_name, roadmap_data in roadmaps.items():
            # Add main roadmap info
            chunks.append({
                "content": f"Roadmap: {roadmap_data['title']}\nURL: {roadmap_data.get('url', '')}",
                "metadata": {
                    "roadmap": roadmap_name,
                    "type": "roadmap_overview",
                    "title": roadmap_data['title']
                }
            })
            
            # Add section chunks
            for section in roadmap_data.get("sections", []):
                # Main section content
                section_content = f"Section: {section['title']}\n{section.get('content', '')}"
                chunks.append({
                    "content": section_content,
                    "metadata": {
                        "roadmap": roadmap_name,
                        "type": "section",
                        "title": section['title'],
                        "section_title": section['title']
                    }
                })
                
                # Subsections as separate chunks
                for subsection in section.get("subsections", []):
                    chunks.append({
                        "content": f"Topic: {subsection}\nPart of: {section['title']}",
                        "metadata": {
                            "roadmap": roadmap_name,
                            "type": "subsection",
                            "title": subsection,
                            "section_title": section['title']
                        }
                    })
        
        return chunks


def main():
    """Main function to run the scraper"""
    scraper = RoadmapScraper()
    
    # Scrape all roadmaps
    roadmaps = scraper.scrape_all_roadmaps()
    
    # Save to files
    scraper.save_roadmaps(roadmaps)
    
    # Create chunks for vector database
    chunks = scraper.create_chunks_for_vectordb(roadmaps)
    
    # Save chunks
    chunks_file = "backend/data/roadmap_cache/roadmap_chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(chunks)} chunks to {chunks_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("ROADMAP SCRAPING SUMMARY")
    print("="*50)
    
    for roadmap_name, roadmap_data in roadmaps.items():
        print(f"\n{roadmap_data['title']}:")
        print(f"  - {len(roadmap_data.get('sections', []))} sections")
        total_subsections = sum(len(section.get('subsections', [])) for section in roadmap_data.get('sections', []))
        print(f"  - {total_subsections} subsections")
    
    print(f"\nTotal chunks created: {len(chunks)}")
    print("\nNext step: Run setup_vectordb.py to create the vector database")


if __name__ == "__main__":
    main()
