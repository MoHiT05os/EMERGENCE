import argparse
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from src.vision.pipeline import VisionPipeline
from src.reasoning.analytics import EngagementAnalytics
from src.reasoning.assessment import MicroTestGenerator
from src.reasoning.test_scores import TestScoreLoader
from src.reasoning.student_registry import StudentRegistry
from src.generation.curriculum import CurriculumGenerator
from src.generation.renderer import ContentRenderer
from src.config import TEST_VIDEO_DIR, INPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="EMERGENCE: Intelligent Classroom Learning System")
    parser.add_argument("--source", type=str, default="0", help="Video source (0 for webcam or path to file)")
    parser.add_argument("--topic", type=str, default="General Science", help="Topic for curriculum generation")
    parser.add_argument("--skip-vision", action="store_true", help="Skip vision layer and use existing logs")
    parser.add_argument("--process-test-videos", action="store_true", help="Process test videos for test-time engagement")
    parser.add_argument("--test-scores", type=str, default=None, help="Path to test scores Excel file")
    parser.add_argument("--skip-generation", action="store_true", help="Skip content generation phase")

    args = parser.parse_args()

    if not args.skip_vision:
        print("\n=== PHASE 1a: Vision (Class Video) ===")
        print(f"Source: {args.source}")
        source = int(args.source) if args.source.isdigit() else args.source

        pipeline = VisionPipeline(source=source, output_csv="engagement_log.csv",
                                  save_frames=True, frame_save_tag="class")
        pipeline.process()
    else:
        print("\n=== PHASE 1a: Vision – Class (Skipped) ===")

    if args.process_test_videos:
        print("\n=== PHASE 1b: Vision (Test Videos) ===")
        test_videos = sorted(TEST_VIDEO_DIR.glob("*.mp4"))
        if test_videos:
            print(f"Found {len(test_videos)} test videos")
            pipeline = VisionPipeline(source=str(test_videos[0]),
                                      output_csv="test_engagement_log.csv",
                                      save_frames=True, frame_save_tag="test_0")
            pipeline.process_batch(test_videos, output_csv="test_engagement_log.csv", display=False)
        else:
            print("No test videos found in", TEST_VIDEO_DIR)
    else:
        print("\n=== PHASE 1b: Vision – Test (Skipped) ===")

    print("\n=== PHASE 2: Reasoning (Analysis) ===")

    registry = StudentRegistry()
    roster = registry.load_roster(args.test_scores)

    if roster is not None:
        print(f"Loaded {len(roster)} students from roster")
        if not registry.mapping_path.exists():
            registry.create_mapping_template()
            print("Created mapping template. Use Streamlit UI to map tracker IDs to SAP IDs.")

    analytics = EngagementAnalytics()

    if registry.mapping_path.exists():
        mapping = registry.load_mapping()
        if mapping is not None and mapping["class_tracker_id"].notna().any():
            print("Applying SAP ID mapping to engagement data...")
            import pandas as pd
            class_df = pd.read_csv("data/output/engagement_log.csv")
            class_mapped = registry.apply_mapping_to_engagement(class_df, "class")

            test_mapped = None
            test_log_path = Path("data/output/test_engagement_log.csv")
            if test_log_path.exists():
                test_df = pd.read_csv(test_log_path)
                test_mapped = registry.apply_mapping_to_engagement(test_df, "test")

            scores_loader = TestScoreLoader(args.test_scores)
            scores_df = scores_loader.load_scores()

            if scores_df is not None:
                merged = registry.merge_all_data(class_mapped, test_mapped, scores_df)
                student_profiles = analytics.analyze_enhanced_clusters(merged)

                if student_profiles is not None and not student_profiles.empty:
                    print("\nEnhanced Student Profiles:")
                    display_cols = [c for c in ["student_name", "status", "learning_level",
                                                "class_engagement", "academic_score"] if c in student_profiles.columns]
                    print(student_profiles[display_cols].to_string())
                else:
                    print("Enhanced clustering produced no results.")
            else:
                print("No test scores available. Running basic clustering.")
                student_profiles = analytics.analyze_clusters()
        else:
            print("Mapping not completed. Running basic clustering on tracker IDs.")
            student_profiles = analytics.analyze_clusters()
    else:
        print("No mapping file. Running basic clustering.")
        student_profiles = analytics.analyze_clusters()

    if student_profiles is None or student_profiles.empty:
        print("No student data found. Exiting.")
        return

    if not args.skip_generation:
        print("\n=== PHASE 3: Generative (Adaptation) ===")
        assessment_gen = MicroTestGenerator()
        curriculum_gen = CurriculumGenerator()
        renderer = ContentRenderer()

        consecutive_failures = 0
        for i, (student_id, profile) in enumerate(student_profiles.iterrows()):
            name = profile.get("student_name", f"Student {student_id}")
            status = profile.get("status", "Active")
            print(f"\nGenerating content for {name} ({status})...")

            test = assessment_gen.generate_test(profile, topic=args.topic)
            if test and 'error' not in str(test).lower():
                print(f"  [Micro-Test] Question: {test.get('question', 'N/A')}")
                consecutive_failures = 0
            else:
                print("  [Micro-Test] Skipped (No API Key or Error)")
                consecutive_failures += 1

            module_content = curriculum_gen.generate_module(profile, topic=args.topic)
            if 'Error' in module_content and '429' in module_content:
                consecutive_failures += 1
            else:
                consecutive_failures = 0
            renderer.save(module_content, student_id, args.topic)

            if consecutive_failures >= 3:
                print("\n[!] API quota appears exhausted. Stopping generation.")
                print("    Remaining students will be skipped.")
                print("    Re-run after quota resets (usually next day).")
                break

            if i < len(student_profiles) - 1:
                print("  [Waiting 5s before next student...]")
                time.sleep(5)
    else:
        print("\n=== PHASE 3: Generation (Skipped) ===")

    print("\n=== EMERGENCE Workflow Complete ===")


if __name__ == "__main__":
    main()
