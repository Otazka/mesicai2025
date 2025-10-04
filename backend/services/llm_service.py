"""
LangChain service for LLM interactions
"""

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from typing import List, Dict, Any, Optional
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for handling LLM interactions"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.llm = ChatOpenAI(
            model_name=settings.model_name,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def create_assessment_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for skill assessment"""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert IT skills assessor conducting a conversational assessment. 
            Your role is to:
            1. Ask targeted questions about Python, OOP, and Algorithms
            2. Evaluate responses and provide constructive feedback
            3. Assign proficiency scores (0-100) based on technical accuracy
            4. Maintain a supportive and encouraging tone
            
            Guidelines:
            - Ask one question at a time
            - Provide immediate feedback on answers
            - Score based on technical correctness, depth of understanding, and practical knowledge
            - Be encouraging while being honest about skill levels
            - Focus on learning and improvement"""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}")
        ])
    
    def create_gap_analysis_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for gap analysis"""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert career advisor analyzing skill gaps for IT professionals.
            Your role is to:
            1. Compare current skills against target role requirements
            2. Identify priority areas for improvement
            3. Provide detailed explanations of why skills matter
            4. Generate actionable insights
            
            Guidelines:
            - Be specific about skill gaps
            - Prioritize skills by importance and dependencies
            - Explain the business impact of each skill
            - Provide realistic timelines for improvement
            - Consider the user's current experience level"""),
            HumanMessage(content="{input}")
        ])
    
    def create_learning_path_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for learning path generation"""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert learning path designer creating personalized roadmaps for IT professionals.
            Your role is to:
            1. Create structured learning objectives based on skill gaps
            2. Sequence skills by dependencies and importance
            3. Provide time estimates and resource recommendations
            4. Include practical projects and exercises
            
            Guidelines:
            - Break down complex skills into manageable chunks
            - Include hands-on practice opportunities
            - Provide realistic time estimates
            - Suggest relevant resources and tools
            - Create a logical progression from basic to advanced"""),
            HumanMessage(content="{input}")
        ])
    
    def create_concept_explainer_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for explaining concepts"""
        return ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert technical educator explaining IT concepts clearly and comprehensively.
            Your role is to:
            1. Explain concepts in simple, understandable terms
            2. Provide practical examples and code snippets
            3. Connect concepts to real-world applications
            4. Answer follow-up questions thoroughly
            
            Guidelines:
            - Start with simple explanations and build complexity
            - Use analogies when helpful
            - Provide code examples when relevant
            - Explain the 'why' behind concepts
            - Encourage questions and deeper exploration"""),
            HumanMessage(content="{input}")
        ])
    
    async def assess_skill_response(self, question: str, user_answer: str, criteria: List[str]) -> Dict[str, Any]:
        """Assess a user's response to a skill question"""
        prompt = f"""
        Question: {question}
        User Answer: {user_answer}
        Evaluation Criteria: {', '.join(criteria)}
        
        Please evaluate this response and provide:
        1. A score from 0-100 based on technical accuracy and depth
        2. Specific feedback on what was good and what could be improved
        3. Suggestions for further learning
        
        Respond in JSON format:
        {{
            "score": <integer 0-100>,
            "feedback": "<detailed feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "improvements": ["<improvement1>", "<improvement2>"],
            "suggestions": ["<suggestion1>", "<suggestion2>"]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            result = json.loads(response.content)
            return result
        except Exception as e:
            logger.error(f"Error assessing skill response: {e}")
            return {
                "score": 50,
                "feedback": "Unable to assess response at this time.",
                "strengths": [],
                "improvements": ["Please try again"],
                "suggestions": []
            }
    
    async def generate_follow_up_question(self, topic: str, subtopic: str, previous_answers: List[str]) -> str:
        """Generate a follow-up question based on previous answers"""
        prompt = f"""
        Topic: {topic}
        Subtopic: {subtopic}
        Previous answers: {previous_answers}
        
        Generate a follow-up question that:
        1. Builds on the previous answers
        2. Tests deeper understanding
        3. Is appropriate for the user's apparent skill level
        4. Is clear and specific
        
        Return only the question text.
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error generating follow-up question: {e}")
            return "Can you provide more details about your experience with this topic?"
    
    async def analyze_skill_gaps(self, current_skills: Dict[str, int], target_role: str) -> Dict[str, Any]:
        """Analyze skill gaps for a target role"""
        prompt = f"""
        Current Skills: {json.dumps(current_skills, indent=2)}
        Target Role: {target_role}
        
        Analyze the skill gaps and provide:
        1. Priority areas for improvement (ranked by importance)
        2. Specific skill gaps with explanations
        3. Recommended learning sequence
        4. Time estimates for improvement
        
        Respond in JSON format:
        {{
            "priority_areas": ["<area1>", "<area2>", "<area3>"],
            "skill_gaps": {{
                "<skill>": {{
                    "current_level": <current_score>,
                    "target_level": <target_score>,
                    "gap": <gap_size>,
                    "importance": "<high/medium/low>",
                    "explanation": "<why this skill matters>"
                }}
            }},
            "learning_sequence": ["<skill1>", "<skill2>", "<skill3>"],
            "time_estimates": {{
                "<skill>": "<time_estimate>"
            }}
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error analyzing skill gaps: {e}")
            return {
                "priority_areas": [],
                "skill_gaps": {},
                "learning_sequence": [],
                "time_estimates": {}
            }
    
    async def generate_learning_path(self, gaps: Dict[str, Any], user_goals: List[str]) -> Dict[str, Any]:
        """Generate a personalized learning path"""
        prompt = f"""
        Skill Gaps: {json.dumps(gaps, indent=2)}
        User Goals: {user_goals}
        
        Generate a comprehensive learning path that includes:
        1. Structured learning objectives
        2. Weekly breakdown with specific tasks
        3. Resource recommendations
        4. Practice projects
        5. Milestone checkpoints
        
        Respond in JSON format:
        {{
            "total_duration": "<total_time_estimate>",
            "objectives": [
                {{
                    "id": "<objective_id>",
                    "title": "<objective_title>",
                    "description": "<detailed_description>",
                    "topic": "<topic>",
                    "subtopic": "<subtopic>",
                    "estimated_time": <hours>,
                    "difficulty": "<beginner/intermediate/advanced>",
                    "prerequisites": ["<prereq1>", "<prereq2>"],
                    "resources": [
                        {{
                            "type": "<type>",
                            "title": "<title>",
                            "url": "<url>",
                            "description": "<description>"
                        }}
                    ]
                }}
            ],
            "weekly_breakdown": [
                {{
                    "week": 1,
                    "focus": "<weekly_focus>",
                    "objectives": ["<obj1>", "<obj2>"],
                    "tasks": ["<task1>", "<task2>"],
                    "estimated_hours": <hours>
                }}
            ]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return {
                "total_duration": "8 weeks",
                "objectives": [],
                "weekly_breakdown": []
            }
    
    async def explain_concept(self, topic: str, subtopic: str, user_level: str) -> Dict[str, Any]:
        """Explain a technical concept in detail"""
        prompt = f"""
        Topic: {topic}
        Subtopic: {subtopic}
        User Level: {user_level}
        
        Provide a comprehensive explanation that includes:
        1. Clear definition and overview
        2. Practical examples with code (if applicable)
        3. Real-world applications
        4. Common pitfalls and best practices
        5. Related concepts to explore
        
        Respond in JSON format:
        {{
            "explanation": "<detailed_explanation>",
            "examples": ["<example1>", "<example2>"],
            "code_snippets": ["<code1>", "<code2>"],
            "applications": ["<app1>", "<app2>"],
            "best_practices": ["<practice1>", "<practice2>"],
            "related_concepts": ["<concept1>", "<concept2>"]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Error explaining concept: {e}")
            return {
                "explanation": "Unable to provide explanation at this time.",
                "examples": [],
                "code_snippets": [],
                "applications": [],
                "best_practices": [],
                "related_concepts": []
            }
