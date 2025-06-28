# worksheet_generator/services/ai_services.py
import os
import json
import logging
from typing import Dict, List, Tuple
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)

class MoodAnalyzer:
    """Analyzes user mood using HuggingFace transformers"""
    
    def __init__(self):
        try:
            # Use a pre-trained emotion classification model
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # Use CPU
            )
        except Exception as e:
            logger.error(f"Failed to initialize emotion classifier: {e}")
            self.emotion_classifier = None
    
    def analyze_mood(self, mood_text: str) -> Dict:
        """
        Analyze mood from text input
        Returns emotion classification with confidence scores
        """
        if not self.emotion_classifier:
            return self._fallback_mood_analysis(mood_text)
        
        try:
            results = self.emotion_classifier(mood_text)
            
            # Map emotions to learning states
            emotion_mapping = {
                'joy': 'excited',
                'optimism': 'confident', 
                'surprise': 'curious',
                'love': 'happy',
                'approval': 'focused',
                'realization': 'curious',
                'admiration': 'confident',
                'excitement': 'excited',
                'caring': 'calm',
                'desire': 'motivated',
                'neutral': 'calm',
                'disappointment': 'tired',
                'disapproval': 'confused',
                'sadness': 'tired',
                'fear': 'confused',
                'nervousness': 'anxious',
                'embarrassment': 'shy',
                'anger': 'frustrated',
                'annoyance': 'frustrated',
                'grief': 'sad'
            }
            
            primary_emotion = results[0]['label'].lower()
            confidence = results[0]['score']
            
            learning_mood = emotion_mapping.get(primary_emotion, 'neutral')
            
            return {
                'detected_emotion': primary_emotion,
                'learning_mood': learning_mood,
                'confidence': confidence,
                'raw_results': results
            }
            
        except Exception as e:
            logger.error(f"Error in mood analysis: {e}")
            return self._fallback_mood_analysis(mood_text)
    
    def _fallback_mood_analysis(self, mood_text: str) -> Dict:
        """Fallback mood analysis using keyword matching"""
        mood_keywords = {
            'excited': ['excited', 'energetic', 'enthusiastic', 'thrilled'],
            'happy': ['happy', 'good', 'great', 'wonderful', 'cheerful'],
            'calm': ['calm', 'peaceful', 'relaxed', 'zen', 'serene'],
            'focused': ['focused', 'concentrated', 'determined', 'ready'],
            'tired': ['tired', 'exhausted', 'sleepy', 'weary', 'drained'],
            'confused': ['confused', 'lost', 'uncertain', 'puzzled'],
            'curious': ['curious', 'interested', 'wondering', 'inquisitive'],
            'confident': ['confident', 'sure', 'certain', 'capable']
        }
        
        mood_text_lower = mood_text.lower()
        for mood, keywords in mood_keywords.items():
            if any(keyword in mood_text_lower for keyword in keywords):
                return {
                    'detected_emotion': mood,
                    'learning_mood': mood,
                    'confidence': 0.8,
                    'method': 'keyword_matching'
                }
        
        return {
            'detected_emotion': 'neutral',
            'learning_mood': 'calm',
            'confidence': 0.5,
            'method': 'default'
        }

class GroqQuestionGenerator:
    """Generates educational questions using Groq AI"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        
    def generate_questions(self, mood: str, subject: str, grade_level: str = "5-10") -> Dict:
        """Generate questions based on mood, subject, and grade level"""
        
        if not self.client:
            logger.warning("Groq client not initialized, using fallback")
            return self._fallback_question_generation(mood, subject, grade_level)
        
        try:
            # Create mood-appropriate motivation
            motivation_prompt = self._create_motivation_prompt(mood)
            motivation = self._generate_motivation(motivation_prompt)
            
            # Generate questions for each difficulty level
            questions = {}
            for difficulty in ['easy', 'medium', 'hard']:
                question_prompt = self._create_question_prompt(
                    subject, difficulty, grade_level, mood
                )
                questions[difficulty] = self._generate_question(question_prompt)
            
            return {
                'motivation': motivation,
                'motivationEmoji': self._get_mood_emoji(mood),
                'questions': questions
            }
            
        except Exception as e:
            logger.error(f"Error generating questions with Groq: {e}")
            return self._fallback_question_generation(mood, subject, grade_level)
    
    def _create_motivation_prompt(self, mood: str) -> str:
        return f"""
        Create an encouraging and personalized motivation message for a student who is feeling {mood}.
        The message should:
        - Be warm and supportive
        - Acknowledge their current emotional state
        - Encourage them to learn
        - Be 1-2 sentences long
        - Use appropriate tone for grades 5-10
        
        Do not include emojis in the text response.
        """
    
    def _create_question_prompt(self, subject: str, difficulty: str, grade_level: str, mood: str) -> str:
        return f"""
        Generate ONE {difficulty} level {subject} question suitable for students in grades {grade_level}.
        
        Consider that the student is feeling {mood}, so:
        - If they're excited/confident: make it engaging and challenging
        - If they're tired/confused: make it clear and encouraging
        - If they're curious: make it thought-provoking
        
        Requirements:
        - Appropriate for {difficulty} difficulty level
        - Relevant to {subject} curriculum for grades {grade_level}
        - Clear and concise
        - Engaging for the student's mood
        - Return ONLY the question text, no additional formatting
        
        Subject focus areas:
        - Math: algebra, geometry, arithmetic, word problems, fractions
        - Science: physics basics, chemistry, biology, earth science, scientific method
        """
    
    def _generate_motivation(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=100
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating motivation: {e}")
            return "You're doing great! Every challenge is a chance to grow stronger. Let's learn together!"
    
    def _generate_question(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.8,
                max_tokens=150
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return "Generate a practice problem for this topic."
    
    def _get_mood_emoji(self, mood: str) -> str:
        emoji_map = {
            'excited': '🚀',
            'happy': '😊',
            'calm': '🧘‍♀️',
            'focused': '🎯',
            'tired': '💪',
            'confused': '🌱',
            'curious': '🔍',
            'confident': '💫',
            'motivated': '⭐',
            'anxious': '🌸',
            'frustrated': '🌈'
        }
        return emoji_map.get(mood, '🌟')
    
    def _fallback_question_generation(self, mood: str, subject: str, grade_level: str) -> Dict:
        """Fallback question generation when Groq is unavailable"""
        
        fallback_questions = {
            'math': {
                'easy': "If you have 24 stickers and want to share them equally among 6 friends, how many stickers will each friend get?",
                'medium': "A rectangular garden has a length of 12 meters and a width of 8 meters. What is the area of the garden?",
                'hard': "Solve for x: 2x + 15 = 3x - 7"
            },
            'science': {
                'easy': "What are the three main states of matter? Give an example of each.",
                'medium': "Explain why objects fall to the ground when dropped. What force is responsible for this?",
                'hard': "If a car travels 150 kilometers in 2.5 hours, what is its average speed in meters per second?"
            }
        }
        
        motivation_messages = {
            'excited': "Your enthusiasm is amazing! Let's channel that energy into some fantastic learning!",
            'tired': "Even when we're tired, small steps forward make a big difference. You've got this!",
            'confused': "It's completely normal to feel confused when learning something new. That's how growth happens!",
            'default': "Learning is a journey, and every step counts. You're doing wonderfully!"
        }
        
        questions = fallback_questions.get(subject, fallback_questions['math'])
        motivation = motivation_messages.get(mood, motivation_messages['default'])
        
        return {
            'motivation': motivation,
            'motivationEmoji': self._get_mood_emoji(mood),
            'questions': questions
        }

class AIWorksheetService:
    """Main service that coordinates mood analysis and question generation"""
    
    def __init__(self):
        self.mood_analyzer = MoodAnalyzer()
        self.question_generator = GroqQuestionGenerator()
    
    def create_personalized_worksheet(self, mood_input: str, subject: str, grade_level: str = "5-10") -> Dict:
        """
        Create a personalized worksheet based on user input
        """
        try:
            # Analyze mood
            mood_analysis = self.mood_analyzer.analyze_mood(mood_input)
            learning_mood = mood_analysis['learning_mood']
            
            # Generate questions
            worksheet_content = self.question_generator.generate_questions(
                learning_mood, subject, grade_level
            )
            
            # Add mood analysis to response
            worksheet_content['mood_analysis'] = mood_analysis
            worksheet_content['user_input'] = mood_input
            worksheet_content['subject'] = subject
            worksheet_content['grade_level'] = grade_level
            
            return worksheet_content
            
        except Exception as e:
            logger.error(f"Error creating personalized worksheet: {e}")
            raise Exception(f"Failed to create worksheet: {str(e)}")