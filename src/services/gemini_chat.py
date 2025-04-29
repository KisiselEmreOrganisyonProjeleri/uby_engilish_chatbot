import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL, LEVELS
from src.helpers.word_loader import load_words_for_level
from src.helpers.logger import get_logger
import random

logger = get_logger("GeminiChatService")

class GeminiChatService:
    def __init__(self, level):
        try:
            if level not in LEVELS:
                logger.error(f"Invalid level: {level}")
                raise ValueError("Invalid level")
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.level = level
            self.words = load_words_for_level(level)
            self.chat = None
            self.history = []
            logger.info(f"GeminiChatService initialized for level {level}")
        except Exception as e:
            logger.exception("Failed to initialize GeminiChatService")
            raise

    def start_conversation(self):
        try:
            word = random.choice(self.words)
            system_prompt = (
                f"You are an English teacher engaging in a natural conversation with a student at the {self.level} level. "
                f"Focus on the conversation flow. Do NOT automatically correct the student's mistakes unless they explicitly ask for feedback or evaluation. "
                f"Keep your responses concise, friendly, and appropriate for the {self.level} level. "
                f"Today's focus word is: '{word}'. Initiate the conversation about this word."
            )
            self.chat = self.model.start_chat(history=[
                {"role": "user", "parts": [system_prompt]}
            ])
            initial_response = self.chat.send_message(f"Let's talk about the word '{word}'. Can you use it in a sentence?")
            self.history = [("focus_word", word), ("ai", initial_response.text.strip())]
            logger.info(f"Conversation started with focus word: {word}")
            return word
        except Exception as e:
            logger.exception("Failed to start conversation")
            raise

    def send_student_message(self, message):
        try:
            response = self.chat.send_message(message)
            self.history.append(("student", message))
            self.history.append(("ai", response.text.strip()))
            logger.info(f"Student: {message} | AI: {response.text.strip()}")
            return response.text.strip()
        except Exception as e:
            logger.exception("Error during chat message exchange")
            raise

    def get_history(self):
        return self.history

    def evaluate_message(self, message):
        try:
            eval_prompt = (
                f"Evaluate the student's sentence in Turkish, briefly and encouragingly. "
                f"If there are errors, correct them and briefly explain why in Turkish. "
                f"Keep the explanation short. Do not be overly critical. "
                f"Student's sentence: '{message}'"
            )
            response = self.model.generate_content(eval_prompt)
            logger.info(f"Evaluation for: {message} | {response.text.strip()}")
            return response.text.strip()
        except Exception as e:
            logger.exception("Error during evaluation")
            return "Değerlendirme sırasında bir hata oluştu."