"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, BookOpen, Brain, Rocket, Shield, ArrowLeft, Loader2, GraduationCap, Target, Lightbulb } from "lucide-react";

const CLUSTER_CONFIG = {
  excelling: {
    label: "Excelling",
    subtitle: "Advanced Cognitive Tier",
    icon: <Rocket style={{ width: 20, height: 20 }} />,
    color: "#4f634b",
    lightBg: "rgba(79, 99, 75, 0.06)",
    border: "rgba(79, 99, 75, 0.18)",
    tag: "ADVANCED",
    description: "Designed for students demonstrating sustained high engagement and strong academic performance. Content pushes critical thinking, independent research, and higher-order reasoning.",
  },
  developing: {
    label: "Developing",
    subtitle: "Standard Learning Tier",
    icon: <Target style={{ width: 20, height: 20 }} />,
    color: "#545c47",
    lightBg: "rgba(84, 92, 71, 0.06)",
    border: "rgba(84, 92, 71, 0.18)",
    tag: "STANDARD",
    description: "Tailored for students with moderate engagement and average scores. Bridges the gap between recall and application using real-world examples and guided practice.",
  },
  struggling: {
    label: "Struggling",
    subtitle: "Foundation Recovery Tier",
    icon: <Shield style={{ width: 20, height: 20 }} />,
    color: "#8c534d",
    lightBg: "rgba(140, 83, 77, 0.06)",
    border: "rgba(140, 83, 77, 0.18)",
    tag: "FOUNDATION",
    description: "Built for students showing disengagement signals and academic gaps. Content is simplified, confidence-building, and uses micro-steps with everyday analogies.",
  },
};

function MarkdownRenderer({ content, accent }) {
  if (!content) return null;
  const lines = content.split("\n");

  return (
    <div style={{ fontSize: "0.9rem", lineHeight: 1.85, color: "#2e3328", fontFamily: "'Space Mono', monospace" }}>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} style={{ height: "0.5rem" }} />;

        if (trimmed.startsWith("# "))
          return (
            <h1 key={i} style={{ fontSize: "1.5rem", fontWeight: 700, color: "#2e3328", marginTop: "1.5rem", marginBottom: "0.75rem", fontFamily: "'Playfair Display', serif", fontStyle: "italic" }}>
              {trimmed.slice(2)}
            </h1>
          );
        if (trimmed.startsWith("## "))
          return (
            <h2 key={i} style={{ fontSize: "1.15rem", fontWeight: 600, color: accent || "#2e3328", marginTop: "1.5rem", marginBottom: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem", borderBottom: `1px solid rgba(0,0,0,0.06)`, paddingBottom: "0.5rem", fontFamily: "'Playfair Display', serif" }}>
              <span style={{ width: "3px", height: "18px", background: accent, borderRadius: "2px", display: "inline-block" }} />
              {trimmed.slice(3)}
            </h2>
          );
        if (trimmed.startsWith("### "))
          return (
            <h3 key={i} style={{ fontSize: "1rem", fontWeight: 600, color: "#3d4233", marginTop: "1rem", marginBottom: "0.4rem", fontFamily: "'Playfair Display', serif" }}>
              {trimmed.slice(4)}
            </h3>
          );

        if (trimmed.startsWith("---"))
          return <hr key={i} style={{ border: "none", borderTop: "1px solid rgba(0,0,0,0.06)", margin: "1.5rem 0" }} />;

        if (trimmed.startsWith("> "))
          return (
            <blockquote key={i} style={{ borderLeft: `2px solid ${accent || "#7c8065"}`, paddingLeft: "1rem", margin: "0.75rem 0", color: "#6e7361", fontStyle: "italic", background: "rgba(0,0,0,0.015)", padding: "0.75rem 1rem", borderRadius: "0 6px 6px 0" }}>
              {processInline(trimmed.slice(2))}
            </blockquote>
          );

        if (/^\d+\.\s/.test(trimmed)) {
          const match = trimmed.match(/^(\d+)\.\s(.*)/);
          return (
            <div key={i} style={{ display: "flex", gap: "0.75rem", marginBottom: "0.5rem", paddingLeft: "0.25rem" }}>
              <span style={{ minWidth: "22px", height: "22px", background: accent || "#7c8065", color: "#fdfbf7", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", fontWeight: 700, flexShrink: 0, marginTop: "3px" }}>
                {match[1]}
              </span>
              <span>{processInline(match[2])}</span>
            </div>
          );
        }

        if (trimmed.startsWith("- ") || trimmed.startsWith("* ") || trimmed.startsWith("• "))
          return (
            <div key={i} style={{ display: "flex", gap: "0.6rem", marginBottom: "0.4rem", paddingLeft: "0.5rem" }}>
              <span style={{ color: accent || "#7c8065", fontWeight: 700, fontSize: "1rem", lineHeight: "1.7" }}>→</span>
              <span>{processInline(trimmed.slice(2))}</span>
            </div>
          );

        return (
          <p key={i} style={{ marginBottom: "0.5rem" }} dangerouslySetInnerHTML={{ __html: processInlineHTML(trimmed) }} />
        );
      })}
    </div>
  );
}

function processInline(text) {
  const parts = [];
  const regex = /\*\*(.*?)\*\*/g;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index));
    parts.push(<strong key={match.index} style={{ fontWeight: 600, color: "#2e3328" }}>{match[1]}</strong>);
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) parts.push(text.slice(lastIndex));
  return parts;
}

function processInlineHTML(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight:600;color:#2e3328">$1</strong>')
    .replace(/`(.*?)`/g, '<code style="background:rgba(0,0,0,0.04);padding:2px 6px;border-radius:4px;font-size:0.88em;font-family:\'Space Mono\',monospace;color:#545c47">$1</code>');
}

export default function ModulesPage() {
  const router = useRouter();
  const [modules, setModules] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeCluster, setActiveCluster] = useState("excelling");
  const [subject, setSubject] = useState("Reasoning and Cognitive Learning");
  const [clusterStats, setClusterStats] = useState(null);
  const [generated, setGenerated] = useState(false);
  const [pipelineInfo, setPipelineInfo] = useState("DeepSeek V3");
  const [authChecked, setAuthChecked] = useState(false);

  // Auth guard — block render until verified, 24h expiry
  useEffect(() => {
    const auth = localStorage.getItem("emergence_auth");
    if (!auth) { router.push("/login"); return; }
    try {
      const parsed = JSON.parse(auth);
      if (parsed.loginTime && Date.now() - parsed.loginTime > 24 * 60 * 60 * 1000) {
        localStorage.removeItem("emergence_auth");
        router.push("/login");
        return;
      }
      setAuthChecked(true);
    } catch {
      localStorage.removeItem("emergence_auth");
      router.push("/login");
    }
  }, [router]);

  useEffect(() => {
    if (!authChecked) return;
    fetch("/api/dashboard")
      .then((r) => r.json())
      .then((json) => {
        if (json.status === "success" && json.data) {
          const d = json.data;
          const exc = d.filter((s) => s.cluster === "Excelling");
          const dev = d.filter((s) => s.cluster === "Developing");
          const str = d.filter((s) => s.cluster === "Struggling");
          setClusterStats({
            excelling: exc.length,
            excellingAvg: exc.length > 0 ? (exc.reduce((a, s) => a + s.combined_score, 0) / exc.length).toFixed(1) : 0,
            developing: dev.length,
            developingAvg: dev.length > 0 ? (dev.reduce((a, s) => a + s.combined_score, 0) / dev.length).toFixed(1) : 0,
            struggling: str.length,
            strugglingAvg: str.length > 0 ? (str.reduce((a, s) => a + s.combined_score, 0) / str.length).toFixed(1) : 0,
            total: d.length,
          });
        }
      })
      .catch(() => {});
  }, [authChecked]);

  // Block rendering until auth is confirmed (MUST be after all hooks)
  if (!authChecked) return null;

  const generateModules = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/modules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, clusterStats }),
      });
      const json = await res.json();
      if (json.status === "success") {
        setModules(json.modules);
        if (json.pipeline) setPipelineInfo(json.pipeline);
        setGenerated(true);
      } else {
        throw new Error(json.message || "Generation failed");
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const cfg = CLUSTER_CONFIG[activeCluster];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f5f2eb",
      fontFamily: "'Space Mono', monospace",
      color: "#2e3328",
    }}>

      {/* ── Header ── */}
      <div style={{
        background: "#2e3328",
        padding: "2.5rem 3rem 2rem",
      }}>
        <div style={{ maxWidth: "90rem", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <a href="/dashboard" style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "rgba(253,251,247,0.5)", textDecoration: "none", fontSize: "0.75rem", marginBottom: "0.75rem", letterSpacing: "0.5px", textTransform: "uppercase" }}>
              <ArrowLeft style={{ width: 13, height: 13 }} /> Back to Dashboard
            </a>
            <h1 style={{
              fontFamily: "'Playfair Display', serif",
              fontSize: "2.5rem",
              fontWeight: 600,
              fontStyle: "italic",
              color: "#fdfbf7",
              letterSpacing: "-0.3px",
            }}>
              Adaptive Learning Modules
            </h1>
            <p style={{ color: "rgba(253,251,247,0.55)", fontSize: "0.8rem", marginTop: "0.35rem", letterSpacing: "0.5px" }}>
              AI-generated personalized curriculum for each performance cluster
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            {clusterStats && (
              <div style={{ display: "flex", gap: "0.6rem" }}>
                {[
                  { label: "Excelling", count: clusterStats.excelling, color: "#4f634b" },
                  { label: "Developing", count: clusterStats.developing, color: "#7c8065" },
                  { label: "Struggling", count: clusterStats.struggling, color: "#8c534d" },
                ].map((c) => (
                  <div key={c.label} style={{
                    background: "rgba(253,251,247,0.08)",
                    border: "1px solid rgba(253,251,247,0.1)",
                    borderRadius: "6px",
                    padding: "0.5rem 0.85rem",
                    textAlign: "center",
                  }}>
                    <div style={{ color: "#fdfbf7", fontSize: "1.2rem", fontWeight: 700 }}>{c.count}</div>
                    <div style={{ color: "rgba(253,251,247,0.4)", fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "1px" }}>{c.label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: "90rem", margin: "0 auto", padding: "2rem 3rem" }}>

        {/* ── Subject Input + Generate Bar ── */}
        <div style={{
          background: "rgba(253,251,247,0.75)",
          backdropFilter: "blur(12px)",
          borderRadius: "16px",
          padding: "1.25rem 1.75rem",
          border: "1px solid rgba(0,0,0,0.06)",
          marginBottom: "2rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          boxShadow: "0 4px 30px rgba(0,0,0,0.03)",
        }}>
          <GraduationCap style={{ width: 20, height: 20, color: "#7c8065", flexShrink: 0 }} />
          <div style={{ flexGrow: 1 }}>
            <label style={{ fontSize: "0.65rem", textTransform: "uppercase", letterSpacing: "1.5px", color: "#6e7361", fontWeight: 700 }}>Subject / Topic</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              style={{
                display: "block", width: "100%", border: "none", outline: "none",
                fontSize: "1rem", fontWeight: 600, color: "#2e3328",
                fontFamily: "'Playfair Display', serif", marginTop: "0.15rem",
                background: "transparent", fontStyle: "italic",
              }}
              placeholder="e.g. Reasoning and Cognitive Learning"
            />
          </div>
          <button
            onClick={generateModules}
            disabled={loading}
            style={{
              background: loading ? "#6e7361" : "#2e3328",
              color: "#fdfbf7",
              border: "1px solid #2e3328",
              padding: "0.7rem 1.4rem",
              borderRadius: "4px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: 600, fontSize: "0.8rem",
              display: "flex", alignItems: "center", gap: "0.5rem",
              fontFamily: "'Space Mono', monospace",
              letterSpacing: "0.5px",
              textTransform: "uppercase",
              transition: "all 0.2s ease",
              whiteSpace: "nowrap",
            }}
          >
            {loading ? (
              <><Loader2 style={{ width: 16, height: 16, animation: "spin 1s linear infinite" }} /> Generating...</>
            ) : (
              <><Sparkles style={{ width: 16, height: 16 }} /> {generated ? "Regenerate" : "Generate Modules"}</>
            )}
          </button>
        </div>

        {/* Error State */}
        {error && (
          <div style={{
            background: "rgba(140,83,77,0.06)", border: "1px solid rgba(140,83,77,0.15)",
            borderRadius: "8px", padding: "1rem 1.5rem", marginBottom: "1.5rem",
            color: "#8c534d", fontWeight: 500, fontSize: "0.85rem",
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Pre-Generation State */}
        {!modules && !loading && !error && (
          <div style={{ textAlign: "center", padding: "4rem 2rem" }}>
            <div style={{
              width: 72, height: 72, borderRadius: "50%",
              background: "rgba(0,0,0,0.03)", border: "1px solid rgba(0,0,0,0.06)",
              display: "flex", alignItems: "center", justifyContent: "center",
              margin: "0 auto 1.5rem",
            }}>
              <Brain style={{ width: 32, height: 32, color: "#7c8065" }} />
            </div>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 600, color: "#2e3328", marginBottom: "0.5rem", fontFamily: "'Playfair Display', serif", fontStyle: "italic" }}>
              Ready to Generate
            </h2>
            <p style={{ color: "#6e7361", fontSize: "0.85rem", maxWidth: "480px", margin: "0 auto", lineHeight: 1.7 }}>
              Click <strong>"Generate Modules"</strong> to create personalized teaching content for each student cluster using DeepSeek V3 AI.
            </p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: "center", padding: "4rem 2rem" }}>
            <div style={{
              width: 56, height: 56,
              borderTop: "2px solid #2e3328", borderRight: "2px solid transparent",
              borderRadius: "50%", animation: "spin 1s linear infinite",
              margin: "0 auto 1.5rem",
            }} />
            <h2 style={{ fontSize: "1.2rem", fontWeight: 600, color: "#2e3328", marginBottom: "0.4rem", fontFamily: "'Playfair Display', serif", fontStyle: "italic" }}>
              Generating modules...
            </h2>
            <p style={{ color: "#6e7361", fontSize: "0.85rem" }}>Creating 3 detailed teaching modules for "{subject}"</p>
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          </div>
        )}

        {/* ── Generated Modules View ── */}
        {modules && !loading && (
          <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: "2rem" }}>

            {/* Sidebar - Cluster Tabs */}
            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem", position: "sticky", top: "2rem", alignSelf: "start" }}>
              {Object.entries(CLUSTER_CONFIG).map(([key, c]) => (
                <button
                  key={key}
                  onClick={() => setActiveCluster(key)}
                  style={{
                    background: activeCluster === key ? "#2e3328" : "rgba(253,251,247,0.75)",
                    color: activeCluster === key ? "#fdfbf7" : "#2e3328",
                    border: activeCluster === key ? "1px solid #2e3328" : `1px solid rgba(0,0,0,0.06)`,
                    borderRadius: "10px",
                    padding: "1.1rem 1rem",
                    cursor: "pointer",
                    textAlign: "left",
                    fontFamily: "'Space Mono', monospace",
                    transition: "all 0.25s ease",
                    boxShadow: activeCluster === key ? "0 4px 20px rgba(0,0,0,0.12)" : "0 2px 8px rgba(0,0,0,0.03)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.3rem" }}>
                    {c.icon}
                    <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>{c.label}</span>
                  </div>
                  <div style={{ fontSize: "0.7rem", opacity: 0.55, lineHeight: 1.4 }}>
                    {c.subtitle}
                  </div>
                  <div style={{
                    marginTop: "0.5rem", fontSize: "0.6rem",
                    padding: "0.2rem 0.5rem", borderRadius: "3px",
                    display: "inline-block",
                    background: activeCluster === key ? "rgba(253,251,247,0.15)" : "rgba(0,0,0,0.03)",
                    fontWeight: 700, letterSpacing: "1px",
                    color: activeCluster === key ? "rgba(253,251,247,0.7)" : "#6e7361",
                    textTransform: "uppercase",
                  }}>
                    {c.tag} MODULE
                  </div>
                </button>
              ))}

              {/* Info Card */}
              <div style={{
                background: "rgba(253,251,247,0.75)",
                borderRadius: "10px", padding: "1.1rem",
                border: "1px solid rgba(0,0,0,0.06)", marginTop: "0.25rem",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.4rem" }}>
                  <Lightbulb style={{ width: 13, height: 13, color: "#b08a54" }} />
                  <span style={{ fontSize: "0.65rem", fontWeight: 700, color: "#b08a54", textTransform: "uppercase", letterSpacing: "1px" }}>How it works</span>
                </div>
                <p style={{ fontSize: "0.75rem", color: "#6e7361", lineHeight: 1.6 }}>
                  Each module is auto-generated based on the cluster's average engagement and academic metrics. Faculty can use these as teaching guides.
                </p>
              </div>
            </div>

            {/* Main Content Area */}
            <div>
              {/* Cluster Header Card */}
              <div style={{
                background: "#2e3328",
                borderRadius: "14px", padding: "1.75rem 2rem",
                marginBottom: "1.25rem", color: "#fdfbf7",
                border: "1px solid rgba(0,0,0,0.1)",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.5rem" }}>
                      {cfg.icon}
                      <h2 style={{ fontSize: "1.4rem", fontWeight: 600, fontFamily: "'Playfair Display', serif", fontStyle: "italic" }}>{cfg.label} Module</h2>
                      <span style={{ fontSize: "0.6rem", padding: "0.15rem 0.5rem", background: "rgba(253,251,247,0.12)", borderRadius: "3px", fontWeight: 700, letterSpacing: "1px", fontFamily: "'Space Mono', monospace" }}>{cfg.tag}</span>
                    </div>
                    <p style={{ opacity: 0.55, fontSize: "0.8rem", maxWidth: "550px", lineHeight: 1.6 }}>{cfg.description}</p>
                  </div>
                  <div style={{ textAlign: "right", opacity: 0.7 }}>
                    <div style={{ fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "1.5px", marginBottom: "0.2rem" }}>Subject</div>
                    <div style={{ fontSize: "0.9rem", fontWeight: 600, fontFamily: "'Playfair Display', serif", fontStyle: "italic" }}>{subject}</div>
                  </div>
                </div>
                {clusterStats && (
                  <div style={{ display: "flex", gap: "2.5rem", marginTop: "1.25rem", paddingTop: "1rem", borderTop: "1px solid rgba(253,251,247,0.1)" }}>
                    <div>
                      <div style={{ fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "1px", opacity: 0.4 }}>Students</div>
                      <div style={{ fontSize: "1.2rem", fontWeight: 700 }}>{clusterStats[activeCluster] || 0}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "1px", opacity: 0.4 }}>Avg Score</div>
                      <div style={{ fontSize: "1.2rem", fontWeight: 700 }}>{clusterStats[`${activeCluster}Avg`] || "N/A"}%</div>
                    </div>
                    <div>
                      <div style={{ fontSize: "0.6rem", textTransform: "uppercase", letterSpacing: "1px", opacity: 0.4 }}>Engine</div>
                      <div style={{ fontSize: "1rem", fontWeight: 700 }}>{pipelineInfo}</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Module Content Card */}
              <div style={{
                background: "rgba(253,251,247,0.75)",
                backdropFilter: "blur(12px)",
                borderRadius: "14px",
                padding: "2.5rem 3rem",
                border: "1px solid rgba(0,0,0,0.06)",
                boxShadow: "0 4px 30px rgba(0,0,0,0.03)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.5rem", paddingBottom: "1rem", borderBottom: "1px solid rgba(0,0,0,0.06)" }}>
                  <BookOpen style={{ width: 16, height: 16, color: cfg.color }} />
                  <span style={{ fontSize: "0.65rem", fontWeight: 700, color: cfg.color, textTransform: "uppercase", letterSpacing: "1.5px" }}>Teaching Module Content</span>
                  <span style={{
                    marginLeft: "auto", fontSize: "0.65rem", color: "#6e7361",
                    background: "rgba(0,0,0,0.03)", padding: "0.2rem 0.6rem",
                    borderRadius: "3px", border: "1px solid rgba(0,0,0,0.05)",
                  }}>
                    Powered by {pipelineInfo}
                  </span>
                </div>
                <MarkdownRenderer content={modules[activeCluster]} accent={cfg.color} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── Footer ── */}
      <div style={{ maxWidth: "90rem", margin: "3rem auto 0", padding: "1.5rem 3rem 2rem", borderTop: "1px solid rgba(0,0,0,0.05)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h4 style={{ color: "#6e7361", fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "2px", fontWeight: 700, fontFamily: "'Space Mono', monospace" }}>EMERGENCE</h4>
          <p style={{ color: "#6e7361", fontSize: "0.8rem", fontFamily: "'Playfair Display', serif", fontStyle: "italic", marginTop: "0.2rem" }}>Adaptive Classroom Intelligence System</p>
        </div>
        <div style={{ color: "#6e7361", fontSize: "0.75rem" }}>
          Engineered by <strong style={{ color: "#2e3328" }}>Mohit Yadav</strong>
        </div>
      </div>

      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
