import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import OUTPUT_DIR, PROFILES_DIR


class EngagementAnalytics:
    def __init__(self, csv_path=None):
        self.csv_path = csv_path if csv_path else OUTPUT_DIR / "engagement_log.csv"

    def load_data(self):
        if not Path(self.csv_path).exists():
            print(f"Error: {self.csv_path} not found.")
            return None
        return pd.read_csv(self.csv_path)

    def analyze_clusters(self, n_clusters=3):
        df = self.load_data()
        if df is None or df.empty:
            return None

        id_col = "sap_id" if "sap_id" in df.columns else "student_id"

        agg_cols = ["gaze_score", "posture_score", "motion_score", "engagement_score"]
        available = [c for c in agg_cols if c in df.columns]

        agg_dict = {c: "mean" for c in available}
        if "student_name" in df.columns:
            agg_dict["student_name"] = "first"

        student_profile = df.groupby(id_col).agg(agg_dict)

        if len(student_profile) < n_clusters:
            print("Not enough students for clustering.")
            return student_profile

        X = student_profile[["engagement_score", "gaze_score"]]

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        student_profile["cluster"] = kmeans.fit_predict(X)

        centroids = kmeans.cluster_centers_[:, 0]
        sorted_idx = np.argsort(centroids)

        label_map = {
            sorted_idx[0]: "Needs Support",
            sorted_idx[1]: "Active",
            sorted_idx[2]: "Highly Engaged"
        }

        student_profile["status"] = student_profile["cluster"].map(label_map)

        profile_path = PROFILES_DIR / "student_profiles.csv"
        student_profile.to_csv(profile_path)
        print(f"Saved student profiles to {profile_path}")

        return student_profile

    def analyze_enhanced_clusters(self, merged_profiles, n_clusters=3):
        if merged_profiles is None or merged_profiles.empty:
            return None

        df = merged_profiles.copy()

        feature_cols = []
        for col in ["class_engagement", "test_engagement", "academic_score"]:
            if col in df.columns and df[col].notna().any():
                feature_cols.append(col)

        if len(feature_cols) < 2:
            print("Not enough features for enhanced clustering. Falling back to basic.")
            return self.analyze_clusters()

        for col in feature_cols:
            df[col] = df[col].fillna(df[col].median())

        X = df[feature_cols].values

        actual_clusters = min(n_clusters, len(df))
        if actual_clusters < 2:
            df["cluster"] = 0
            df["status"] = "Developing"
            df["learning_level"] = "Standard"
            return df

        kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
        df["cluster"] = kmeans.fit_predict(X)

        if "academic_score" in feature_cols:
            score_col = "academic_score"
        else:
            score_col = feature_cols[0]

        cluster_means = df.groupby("cluster")[score_col].mean()
        sorted_clusters = cluster_means.sort_values().index.tolist()

        if actual_clusters == 3:
            label_map = {
                sorted_clusters[0]: "Struggling",
                sorted_clusters[1]: "Developing",
                sorted_clusters[2]: "Excelling",
            }
        elif actual_clusters == 2:
            label_map = {
                sorted_clusters[0]: "Struggling",
                sorted_clusters[1]: "Excelling",
            }
        else:
            label_map = {sorted_clusters[0]: "Developing"}

        df["status"] = df["cluster"].map(label_map)

        df["learning_level"] = df.apply(self._compute_learning_level, axis=1)

        profile_path = PROFILES_DIR / "student_profiles_v2.csv"
        df.to_csv(profile_path)
        print(f"Saved enhanced profiles to {profile_path}")

        return df

    def _compute_learning_level(self, row):
        class_eng = row.get("class_engagement", 0.5)
        academic = row.get("academic_score", 0.5)
        test_eng = row.get("test_engagement", 0.5)

        eng_threshold = 0.55
        score_threshold = 0.5

        high_engagement = class_eng >= eng_threshold
        high_score = academic >= score_threshold
        high_test_focus = test_eng >= eng_threshold if pd.notna(test_eng) else True

        if high_engagement and high_score:
            if high_test_focus:
                return "Analytical Thinker"
            return "Conceptual Learner"
        elif high_engagement and not high_score:
            return "Conceptual Gap"
        elif not high_engagement and high_score:
            return "Self-Learner"
        else:
            return "Foundational Need"

    def compute_thinking_pattern(self, row):
        test1 = row.get("test1_normalized", 0)
        test2 = row.get("test2_normalized", 0)

        if test1 >= 0.7 and test2 >= 0.7:
            return "Strong Application"
        elif test1 >= 0.7 and test2 < 0.5:
            return "Recall-Oriented"
        elif test1 < 0.5 and test2 >= 0.5:
            return "Intuitive Thinker"
        elif test1 >= 0.5 and test2 >= 0.5:
            return "Balanced"
        else:
            return "Needs Scaffolding"


if __name__ == "__main__":
    analytics = EngagementAnalytics()
    print(analytics.analyze_clusters())
