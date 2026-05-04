import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import TEST_SCORES_PATH, TEST1_MAX_MARKS, TEST2_MAX_MARKS, TOTAL_MAX_MARKS


class TestScoreLoader:
    def __init__(self, path=None):
        self.path = Path(path) if path else TEST_SCORES_PATH

    def load_scores(self):
        if not self.path.exists():
            print(f"Error: {self.path} not found.")
            return None

        df = pd.read_excel(self.path)
        df = df.rename(columns={
            "Student ID": "sap_id",
            "First Name": "first_name",
            "Last Name": "last_name",
            "Test 1 Marks": "test1_score",
            "Test 2 Marks": "test2_score",
            "Total": "total_score",
        })

        df["student_name"] = df["first_name"].fillna("") + " " + df["last_name"].fillna("")
        df["student_name"] = df["student_name"].str.strip()

        df["test1_score"] = df["test1_score"].fillna(0)
        df["test2_score"] = df["test2_score"].fillna(0)
        df["total_score"] = df["test1_score"] + df["test2_score"]

        df["test1_normalized"] = df["test1_score"] / TEST1_MAX_MARKS
        df["test2_normalized"] = df["test2_score"] / TEST2_MAX_MARKS
        df["academic_score"] = df["total_score"] / TOTAL_MAX_MARKS

        df["test1_normalized"] = df["test1_normalized"].clip(0, 1)
        df["test2_normalized"] = df["test2_normalized"].clip(0, 1)
        df["academic_score"] = df["academic_score"].clip(0, 1)

        return df[["sap_id", "student_name", "first_name", "last_name",
                    "test1_score", "test2_score", "total_score",
                    "test1_normalized", "test2_normalized", "academic_score"]]

    def get_roster(self):
        df = self.load_scores()
        if df is None:
            return None
        return df[["sap_id", "student_name"]].copy()


if __name__ == "__main__":
    loader = TestScoreLoader()
    scores = loader.load_scores()
    if scores is not None:
        print(scores.to_string())
        print(f"\nLoaded {len(scores)} students")
