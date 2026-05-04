import os
import time
from openai import OpenAI
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DEEPSEEK_API_KEY, OUTPUT_DIR


class CurriculumGenerator:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            self.client = None
        else:
            self.client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )

    def generate_module(self, student_profile, topic="General Knowledge", max_retries=3):
        if not self.client:
            return "# Error: No API Key Configured"

        status = student_profile.get("status", "Active")
        name = student_profile.get("student_name", "Student")
        learning_level = student_profile.get("learning_level", "Standard")
        class_eng = student_profile.get("class_engagement", student_profile.get("engagement_score", 0.5))
        test_eng = student_profile.get("test_engagement", 0.5)
        academic = student_profile.get("academic_score", 0.5)
        test1 = student_profile.get("test1_score", 0)
        test2 = student_profile.get("test2_score", 0)

        if status in ["Excelling", "Highly Engaged"]:
            strategy = "Provide deep insights, complex examples, and challenge questions. Skip basics. Push for higher-order thinking."
        elif status in ["Struggling", "Needs Support"]:
            strategy = "Use simple analogies, break down concepts into small steps, use encouraging tone. Build from fundamentals."
        else:
            strategy = "Standard explanation with real-world examples. Balance theory with application."

        if learning_level == "Conceptual Gap":
            strategy += " This student is engaged but struggles academically — focus on concept clarity and structured explanations."
        elif learning_level == "Self-Learner":
            strategy += " This student learns independently but is disengaged in class — make content interesting and motivating."

        prompt = f"""
        Create a short personalized learning module.
        
        Student Profile:
        - Name: {name}
        - Status: {status}
        - Learning Level: {learning_level}
        - Class Engagement: {class_eng:.0%}
        - Test Focus: {test_eng:.0%}
        - Test Scores: {test1}/20 (Easy) + {test2}/20 (Medium) = {test1+test2}/40
        - Academic Score: {academic:.0%}
        
        Topic: {topic}
        Strategy: {strategy}
        
        Structure:
        1. Personalized greeting using the student's name
        2. Concept Explanation (adapted to their level)
        3. Real-world Analogy
        4. Practice Question (matched to their difficulty level)
        5. Key Takeaway
        
        Output in Markdown format.
        """

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek/deepseek-chat-v3-0324",
                    messages=[
                        {"role": "system", "content": "You are an expert educational content creator. Generate personalized learning modules in Markdown format."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                if "429" in error_str and attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"  [Rate Limited] Waiting {wait_time}s before retry ({attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    return f"Error generating content: {e}"


if __name__ == "__main__":
    gen = CurriculumGenerator()
    profile = {"status": "Excelling", "student_name": "Aryan Tyagi",
               "learning_level": "Analytical Thinker", "class_engagement": 0.82,
               "test_engagement": 0.75, "academic_score": 0.85,
               "test1_score": 17, "test2_score": 12}
    print(gen.generate_module(profile, "Quantum Physics"))
