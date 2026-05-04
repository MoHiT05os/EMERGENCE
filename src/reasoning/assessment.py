import os
import time
from openai import OpenAI
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DEEPSEEK_API_KEY, OUTPUT_DIR


class MicroTestGenerator:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            print("Warning: DEEPSEEK_API_KEY not found in environment.")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )

    def generate_test(self, student_profile, topic="General Knowledge", max_retries=3):
        if not self.client:
            return {"error": "No API Key"}

        status = student_profile.get("status", "Active")
        learning_level = student_profile.get("learning_level", "Standard")
        academic_score = student_profile.get("academic_score", 0.5)
        test1_norm = student_profile.get("test1_normalized", 0.5)
        test2_norm = student_profile.get("test2_normalized", 0.5)

        if status == "Excelling" or status == "Highly Engaged":
            difficulty = "hard (application and analysis based)"
        elif status == "Struggling" or status == "Needs Support":
            difficulty = "easy (recall and recognition based)"
        else:
            difficulty = "medium (understanding and application based)"

        if test1_norm > 0.7 and test2_norm < 0.4:
            focus = "The student grasps basics well but struggles with medium-difficulty application questions. Focus on bridging recall to application."
        elif test1_norm < 0.5:
            focus = "The student needs help with fundamentals. Use simple, direct questions to build confidence."
        elif academic_score > 0.7:
            focus = "The student performs well overall. Challenge them with higher-order thinking questions."
        else:
            focus = "Balanced question testing both understanding and basic application."

        prompt = f"""
        Generate a single multiple-choice question for a student.
        Student Status: {status}
        Learning Level: {learning_level}
        Academic Performance: {academic_score:.0%}
        Topic: {topic}
        Difficulty: {difficulty}
        Focus: {focus}

        Return ONLY a JSON object with fields: 
        - question
        - options (list of 4)
        - correct_answer
        - reasoning
        """

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324",
                    messages=[
                        {"role": "system", "content": "You are an educational content generator. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                text = response.choices[0].message.content
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"  [Rate Limited] Waiting {wait_time}s before retry ({attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"Error generating test: {e}")
                    return None


if __name__ == "__main__":
    generator = MicroTestGenerator()
    profile = {"status": "Excelling", "learning_level": "Analytical Thinker",
               "academic_score": 0.85, "test1_normalized": 0.9, "test2_normalized": 0.6}
    print(generator.generate_test(profile, topic="Photosynthesis"))
