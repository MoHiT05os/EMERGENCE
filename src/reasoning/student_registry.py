import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import PROFILES_DIR, STUDENT_MAPPING_PATH
from reasoning.test_scores import TestScoreLoader


class StudentRegistry:
    def __init__(self, mapping_path=None):
        self.mapping_path = Path(mapping_path) if mapping_path else STUDENT_MAPPING_PATH
        self.roster = None
        self.mapping = None

    def load_roster(self, scores_path=None):
        loader = TestScoreLoader(scores_path)
        self.roster = loader.get_roster()
        return self.roster

    def create_mapping_template(self):
        if self.roster is None:
            self.load_roster()

        if self.roster is None:
            print("Error: Could not load student roster.")
            return None

        template = self.roster.copy()
        template["class_tracker_id"] = np.nan
        template["test_tracker_id"] = np.nan

        template.to_csv(self.mapping_path, index=False)
        print(f"Mapping template saved to {self.mapping_path}")
        return template

    def load_mapping(self):
        if not self.mapping_path.exists():
            print(f"Mapping file not found at {self.mapping_path}")
            return None

        self.mapping = pd.read_csv(self.mapping_path)
        return self.mapping

    def save_mapping(self, mapping_df):
        mapping_df.to_csv(self.mapping_path, index=False)
        self.mapping = mapping_df
        print(f"Mapping saved to {self.mapping_path}")

    def apply_mapping_to_engagement(self, engagement_df, video_type="class"):
        if self.mapping is None:
            self.load_mapping()

        if self.mapping is None:
            print("No mapping available. Cannot apply.")
            return engagement_df

        id_col = f"{video_type}_tracker_id"

        valid_mapping = self.mapping.dropna(subset=[id_col])
        if valid_mapping.empty:
            print(f"No {video_type} tracker IDs mapped yet.")
            return engagement_df

        id_map = dict(zip(
            valid_mapping[id_col].astype(int),
            valid_mapping["sap_id"].astype(int)
        ))
        name_map = dict(zip(
            valid_mapping["sap_id"].astype(int),
            valid_mapping["student_name"]
        ))

        mapped_df = engagement_df.copy()
        mapped_df["sap_id"] = mapped_df["student_id"].map(id_map)
        mapped_df["student_name"] = mapped_df["sap_id"].map(name_map)

        unmapped = mapped_df["sap_id"].isna().sum()
        total = len(mapped_df)
        mapped_count = total - unmapped
        print(f"Mapped {mapped_count}/{total} entries ({unmapped} unmapped)")

        mapped_df = mapped_df.dropna(subset=["sap_id"])
        mapped_df["sap_id"] = mapped_df["sap_id"].astype(int)

        return mapped_df

    def get_student_name(self, sap_id):
        if self.mapping is None:
            self.load_mapping()
        if self.mapping is None:
            return str(sap_id)

        match = self.mapping[self.mapping["sap_id"] == sap_id]
        if not match.empty:
            return match.iloc[0]["student_name"]
        return str(sap_id)

    def merge_all_data(self, class_engagement_df, test_engagement_df, test_scores_df):
        class_profiles = class_engagement_df.groupby("sap_id").agg({
            "gaze_score": "mean",
            "posture_score": "mean",
            "motion_score": "mean",
            "engagement_score": "mean",
            "student_name": "first"
        }).rename(columns={"engagement_score": "class_engagement"})

        if test_engagement_df is not None and not test_engagement_df.empty:
            test_profiles = test_engagement_df.groupby("sap_id").agg({
                "gaze_score": "mean",
                "posture_score": "mean",
                "motion_score": "mean",
                "engagement_score": "mean",
            }).rename(columns={
                "engagement_score": "test_engagement",
                "gaze_score": "test_gaze_score",
                "posture_score": "test_posture_score",
                "motion_score": "test_motion_score",
            })

            merged = class_profiles.join(test_profiles, how="outer")
        else:
            merged = class_profiles.copy()
            merged["test_engagement"] = np.nan
            merged["test_gaze_score"] = np.nan
            merged["test_posture_score"] = np.nan
            merged["test_motion_score"] = np.nan

        scores_indexed = test_scores_df.set_index("sap_id")
        score_cols = ["test1_score", "test2_score", "total_score",
                      "test1_normalized", "test2_normalized", "academic_score"]
        available_cols = [c for c in score_cols if c in scores_indexed.columns]
        merged = merged.join(scores_indexed[available_cols], how="outer")

        if "student_name" not in merged.columns or merged["student_name"].isna().all():
            name_map = dict(zip(test_scores_df["sap_id"], test_scores_df["student_name"]))
            merged["student_name"] = merged.index.map(name_map)

        merged["student_name"] = merged["student_name"].fillna("Unknown")

        for col in ["class_engagement", "test_engagement", "academic_score"]:
            if col in merged.columns:
                merged[col] = merged[col].fillna(merged[col].median() if merged[col].notna().any() else 0.5)

        return merged


if __name__ == "__main__":
    registry = StudentRegistry()
    roster = registry.load_roster()
    if roster is not None:
        print("Student Roster:")
        print(roster.to_string())
        print(f"\nCreating mapping template...")
        registry.create_mapping_template()
