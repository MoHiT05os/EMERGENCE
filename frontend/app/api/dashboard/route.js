import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

// Simple CSV parser — no external deps needed
function parseCSV(raw) {
  const lines = raw.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n').filter(l => l.trim());
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const vals = line.split(',');
    const obj = {};
    headers.forEach((h, i) => { obj[h] = (vals[i] || '').trim(); });
    return obj;
  });
}

// Subject configuration
const SUBJECTS = {
  "Reasoning": {
    testScores: "Main_Test_Score_Final.csv",
    engagementPrefix: "engagement_log_Main_Test",
    columns: { easy: "Reasoning Test 1 (20)/20 March", medium: "Medium", hard: "Test 2 (tough) 20 Min (20 marks)" },
    video: "annotated_Main_Test.mp4",
    day: "Monday",
    faculty: "Dr. Mohit Yadav"
  },
  "Computer_Core": {
    testScores: "subjects/Computer_Core_Scores.csv",
    engagementPrefix: "engagement_log_Computer_Core",
    columns: { easy: "Test 1 (20)", medium: "Test 2 (20)", hard: "Test 3 (20)" },
    video: "annotated_Computer_Core.mp4",
    day: "Wednesday",
    faculty: "Prof. Sharma"
  },
  "Data_Structures": {
    testScores: "subjects/Data_Structures_Scores.csv",
    engagementPrefix: "engagement_log_Data_Structures",
    columns: { easy: "Test 1 (20)", medium: "Test 2 (20)", hard: "Test 3 (20)" },
    video: "annotated_Data_Structures.mp4",
    day: "Friday",
    faculty: "Prof. Gupta"
  }
};

// Deterministic synthetic engagement for subjects without vision logs
function syntheticEngagement(gid, subjectKey) {
  let h = 0;
  const s = `${gid}-${subjectKey}`;
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  h = Math.abs(h);
  return {
    engagement: Math.min(1.0, 0.45 + (h % 45) / 100),
    gaze: Math.min(1.0, 0.40 + ((h * 3) % 50) / 100),
    posture: Math.min(1.0, 0.35 + ((h * 7) % 55) / 100),
  };
}

export async function GET(req) {
  try {
    const { searchParams } = new URL(req.url);
    const subjectKey = searchParams.get("subject") || "Reasoning";

    const subjectConfig = SUBJECTS[subjectKey];
    if (!subjectConfig) {
      return NextResponse.json({ error: `Unknown subject: ${subjectKey}`, subjects: Object.keys(SUBJECTS) }, { status: 400 });
    }

    const dataDir = path.resolve(process.cwd(), "data");
    const testScoresPath = path.join(dataDir, "input", subjectConfig.testScores);
    const outputDir = path.join(dataDir, "output");

    // Read Test Scores
    if (!fs.existsSync(testScoresPath)) {
      return NextResponse.json({ error: `Missing test scores: ${subjectConfig.testScores}` }, { status: 404 });
    }
    const testScoresRaw = fs.readFileSync(testScoresPath, "utf-8");
    const testScores = parseCSV(testScoresRaw);

    // Try to read engagement log
    let studentAggregates = {};
    let hasRealVision = false;

    try {
      const files = fs.readdirSync(outputDir).filter(fn =>
        fn.startsWith(subjectConfig.engagementPrefix) && fn.endsWith(".csv")
      );

      if (files.length > 0) {
        files.sort((a, b) =>
          fs.statSync(path.join(outputDir, b)).mtime.getTime() -
          fs.statSync(path.join(outputDir, a)).mtime.getTime()
        );
        const visionRaw = fs.readFileSync(path.join(outputDir, files[0]), "utf-8");
        const visionLogs = parseCSV(visionRaw);

        for (const row of visionLogs) {
          const gid = row.global_student_id || row.student_id;
          if (!gid) continue;
          if (!studentAggregates[gid]) {
            studentAggregates[gid] = { count: 0, engagement_score: 0, gaze_score: 0, posture_score: 0 };
          }
          studentAggregates[gid].engagement_score += parseFloat(row.engagement_score || 0);
          studentAggregates[gid].gaze_score += parseFloat(row.gaze_score || 0);
          studentAggregates[gid].posture_score += parseFloat(row.posture_score || 0);
          studentAggregates[gid].count += 1;
        }
        hasRealVision = true;
      }
    } catch (e) {
      console.warn("Vision log read failed, using synthetic:", e.message);
    }

    // Build final roster
    const finalRoster = [];
    const maxTestScore = 60;
    const cols = subjectConfig.columns;

    for (const testRow of testScores) {
      const gid = testRow["GID"] ? testRow["GID"].trim() : null;
      const fullName = testRow["Name"] ? testRow["Name"].trim() : "Unknown Student";

      let easy = parseFloat(String(testRow[cols.easy] || "0").replace(/\*/g, "")) || 0;
      let med = parseFloat(String(testRow[cols.medium] || "0").replace(/\*/g, "")) || 0;
      let hard = parseFloat(String(testRow[cols.hard] || "0").replace(/\*/g, "")) || 0;

      const academicScore = Math.min(1.0, (easy + med + hard) / maxTestScore);

      let visionScore = 0, gazeScore = 0, postureScore = 0;
      let isAbsent = false;

      if (gid && hasRealVision && studentAggregates[gid]) {
        const agg = studentAggregates[gid];
        visionScore = agg.engagement_score / agg.count;
        gazeScore = agg.gaze_score / agg.count;
        postureScore = agg.posture_score / agg.count;
      } else if (gid && !hasRealVision) {
        // Use synthetic engagement
        const syn = syntheticEngagement(gid, subjectKey);
        visionScore = syn.engagement;
        gazeScore = syn.gaze;
        postureScore = syn.posture;
      } else {
        isAbsent = true;
      }

      let fusedScore = isAbsent ? academicScore * 0.5 : (academicScore * 0.5) + (visionScore * 0.5);
      let cluster = isAbsent ? "Absent" : fusedScore >= 0.70 ? "Excelling" : fusedScore <= 0.50 ? "Struggling" : "Developing";

      finalRoster.push({
        sap_id: testRow["Student Id"] || "Unknown",
        name: fullName,
        test_score: Number((academicScore * 100).toFixed(1)),
        vision_score: isAbsent ? 0 : Number((visionScore * 100).toFixed(1)),
        gaze_score: isAbsent ? 0 : Number((gazeScore * 100).toFixed(1)),
        posture_score: isAbsent ? 0 : Number((postureScore * 100).toFixed(1)),
        test1: easy, test2: med, test3: hard,
        combined_score: Number((fusedScore * 100).toFixed(1)),
        cluster,
        module: cluster === "Absent"
          ? `### Catch-up Module for ${fullName}\nYou missed the recent physical session. Please review the baseline recording.`
          : "Awaiting Generative AI Deployment... Click 'Deploy AI' above."
      });
    }

    finalRoster.sort((a, b) => b.combined_score - a.combined_score);
    const visionDetected = hasRealVision ? Object.keys(studentAggregates).length : 0;

    return NextResponse.json({
      status: "success",
      subject: subjectKey,
      subjectConfig: { day: subjectConfig.day, faculty: subjectConfig.faculty, video: subjectConfig.video, hasRealVision },
      total_students: finalRoster.length,
      vision_detected: visionDetected,
      subjects: Object.entries(SUBJECTS).map(([key, cfg]) => ({ key, day: cfg.day, faculty: cfg.faculty })),
      data: finalRoster
    });

  } catch (error) {
    console.error("Dashboard API Error:", error);
    return NextResponse.json({ error: error.toString(), stack: error.stack }, { status: 500 });
  }
}
