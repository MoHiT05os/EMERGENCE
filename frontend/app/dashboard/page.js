"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Sparkles, Trophy, BrainCircuit, Users, Target, Activity, Flame, ShieldAlert, BadgeCheck, X, Eye, SquareUser, ClipboardCheck, BookOpen, Calendar, LogOut } from "lucide-react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from "recharts";

const SCHEDULE = [
  { key: "Reasoning", label: "Reasoning", day: "Monday", color: "#22d3ee" },
  { key: "Computer_Core", label: "Computer Core", day: "Wednesday", color: "#8b5cf6" },
  { key: "Data_Structures", label: "Data Structures", day: "Friday", color: "#f59e0b" },
];

export default function PremiumDashboard() {
  const router = useRouter();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authUser, setAuthUser] = useState(null);
  const [activeSubject, setActiveSubject] = useState("Reasoning");
  const [subjectMeta, setSubjectMeta] = useState(null);
  const [pipelineInfo, setPipelineInfo] = useState("");
  const [visionCount, setVisionCount] = useState(0);

  // Interactive Search & UI State
  const [searchTerm, setSearchTerm] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showAbout, setShowAbout] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const [authChecked, setAuthChecked] = useState(false);

  // Auth guard — block render until verified, 24h expiry
  useEffect(() => {
    const auth = localStorage.getItem("emergence_auth");
    if (!auth) { router.push("/login"); return; }
    try {
      const parsed = JSON.parse(auth);
      // Expire sessions after 24 hours
      if (parsed.loginTime && Date.now() - parsed.loginTime > 24 * 60 * 60 * 1000) {
        localStorage.removeItem("emergence_auth");
        router.push("/login");
        return;
      }
      setAuthUser(parsed);
      setAuthChecked(true);
    } catch {
      localStorage.removeItem("emergence_auth");
      router.push("/login");
    }
  }, [router]);

  // Prevent background scrolling when modals are open
  useEffect(() => {
    if (selectedStudent || showAbout) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [selectedStudent, showAbout]);

  // Fetch data for active subject
  useEffect(() => {
    if (!authUser) return;
    setLoading(true);
    fetch(`/api/dashboard?subject=${activeSubject}`)
      .then((res) => res.json())
      .then((json) => {
        if (json.status === "success") {
          setData(json.data);
          setSubjectMeta(json.subjectConfig);
          setVisionCount(json.vision_detected || 0);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [activeSubject, authUser]);

  // Block rendering until auth is confirmed (MUST be after all hooks)
  if (!authChecked) {
    return (
      <div style={{ minHeight: '100vh', background: '#f5f2eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Playfair Display', serif" }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '2.5rem', fontStyle: 'italic', color: '#2e3328', letterSpacing: '-0.3px' }}>EMERGENCE</h1>
          <p style={{ color: '#6e7361', fontFamily: "'Space Mono', monospace", fontSize: '0.75rem', letterSpacing: '1px', marginTop: '0.5rem' }}>LOADING...</p>
        </div>
      </div>
    );
  }

  const handleLogout = () => {
    localStorage.removeItem("emergence_auth");
    router.push("/");
  };

  // Isolate demographics
  const excelling = data.filter((s) => s.cluster === "Excelling");
  const developing = data.filter((s) => s.cluster === "Developing");
  const struggling = data.filter((s) => s.cluster === "Struggling");
  const absent = data.filter((s) => s.cluster === "Absent");

  const topPerformers = [...data].sort((a, b) => b.combined_score - a.combined_score).slice(0, 5);

  const filteredSearch = data.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()) && searchTerm.trim() !== "");

  const handleStudentSelect = (student) => {
    setSelectedStudent(student);
    setSearchTerm("");
    setIsDropdownOpen(false);
  };

  const deployAI = async () => {
    if (data.length === 0) return;
    setIsGenerating(true);
    setPipelineInfo("");
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ students: data })
      });
      const json = await res.json();
      if (json.status === "success" && json.data) {
        setPipelineInfo(json.pipeline || "");
        const updatedData = data.map(s => {
          let aiText = "Awaiting Generation...";
          if (s.cluster === "Excelling" && json.data.Excelling) aiText = json.data.Excelling;
          if (s.cluster === "Developing" && json.data.Developing) aiText = json.data.Developing;
          if (s.cluster === "Struggling" && json.data.Struggling) aiText = json.data.Struggling;
          aiText = aiText.replace(/\[Student Name\]/g, s.name);
          return { ...s, module: aiText };
        });
        setData(updatedData);
      } else {
        throw new Error(json.message || "Failed to generate AI logic.");
      }
    } catch (err) {
      console.error("AI Generation Error", err);
      const errorData = data.map(s => ({
        ...s,
        module: `⚠️ AI Engine Offline\n\nError: ${err.message}\n\nPlease check your DeepSeek API key and OpenRouter billing.`
      }));
      setData(errorData);
    }
    setIsGenerating(false);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-dark)' }}>
        <div style={{ width: '64px', height: '64px', borderTop: '2px solid #22d3ee', borderBottom: '2px solid #22d3ee', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const renderModule = (text) => {
    if (!text) return <p style={{ color: '#94a3b8', fontStyle: 'italic' }}>Awaiting AI generation...</p>;
    const lines = text.split('\n');
    return lines.map((line, i) => {
      const trimmed = line.trim();
      if (!trimmed) return <br key={i} />;
      if (trimmed.startsWith('### ')) return <h4 key={i} style={{ fontSize: '1.05rem', fontWeight: 700, color: '#7c3aed', marginTop: '0.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Sparkles style={{ width: '14px', height: '14px' }} />{trimmed.slice(4)}</h4>;
      if (trimmed.startsWith('## ')) return <h3 key={i} style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0284c7', marginTop: '0.75rem', marginBottom: '0.25rem' }}>{trimmed.slice(3)}</h3>;
      if (trimmed.startsWith('# ')) return <h2 key={i} style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '0.5rem', marginBottom: '0.25rem' }}>{trimmed.slice(2)}</h2>;
      if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) return <div key={i} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.3rem', paddingLeft: '0.5rem' }}><span style={{ color: '#7c3aed', fontWeight: 700 }}>→</span><span>{trimmed.slice(2)}</span></div>;
      if (trimmed.startsWith('⚠️')) return <div key={i} style={{ padding: '0.75rem 1rem', background: 'rgba(251, 146, 60, 0.08)', border: '1px solid rgba(251, 146, 60, 0.2)', borderRadius: '8px', color: '#ea580c', fontWeight: 500, marginBottom: '0.5rem' }}>{trimmed}</div>;
      if (trimmed.startsWith('✅') || trimmed.startsWith('🎯') || trimmed.startsWith('📊') || trimmed.startsWith('🧠') || trimmed.startsWith('📌') || trimmed.startsWith('🚀')) return <div key={i} style={{ padding: '0.5rem 0', fontWeight: 500 }}>{trimmed}</div>;
      const formatted = trimmed.replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-main); font-weight: 600;">$1</strong>');
      return <p key={i} style={{ marginBottom: '0.4rem', lineHeight: 1.7 }} dangerouslySetInnerHTML={{ __html: formatted }} />;
    });
  };

  const StudentRow = ({ s }) => (
    <div className="student-row" onClick={() => setSelectedStudent(s)} style={{ cursor: 'pointer' }} title="Click for Detailed Intel">
      <div className="student-row-left">
        <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${s.name}&backgroundColor=0f172a`} style={{ width: '32px', height: '32px', borderRadius: '50%', border: '1px solid #334155' }} alt="" />
        <div>
          <h4 className="student-name">{s.name}</h4>
          <span className="student-id">ID: {s.sap_id}</span>
        </div>
      </div>
      <div className="score-pills">
        <div className="score-pill"><span>Ac:</span>{s.test_score}%</div>
        {s.cluster !== "Absent" && <div className="score-pill"><span>Vis:</span>{s.vision_score}%</div>}
      </div>
    </div>
  );

  const currentSchedule = SCHEDULE.find(s => s.key === activeSubject);

  return (
    <div className="dashboard-wrapper">

      {/* 1. Header (Title + Search + Auth) */}
      <div className="title-bar">
        <div>
          <h1 className="gradient-text">EMERGENCE</h1>
          <p>An Intelligent Classroom Learning System</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>

          {/* INTERACTIVE SEARCH UI */}
          <div className="glass-panel" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.75rem', width: '260px', position: 'relative' }}>
            <Search style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
            <input
              type="text"
              placeholder="Locate student..."
              value={searchTerm}
              onChange={(e) => { setSearchTerm(e.target.value); setIsDropdownOpen(true); }}
              onFocus={() => setIsDropdownOpen(true)}
              style={{ background: 'transparent', border: 'none', outline: 'none', color: 'white', width: '100%', fontFamily: 'inherit' }}
            />
            {isDropdownOpen && filteredSearch.length > 0 && (
              <div className="glass-panel" style={{ position: 'absolute', top: '50px', left: 0, width: '100%', background: 'rgba(255,255,255,0.95)', border: '1px solid rgba(0,0,0,0.1)', zIndex: 50, maxHeight: '300px', overflowY: 'auto', padding: '0.5rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {filteredSearch.map((fs, idx) => (
                  <div key={idx} onClick={() => handleStudentSelect(fs)} style={{ padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer', borderRadius: '8px', background: 'rgba(0,0,0,0.02)' }}>
                    <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${fs.name}&backgroundColor=0f172a`} style={{ width: '28px', height: '28px', borderRadius: '50%' }} alt="" />
                    <div>
                      <h4 style={{ fontSize: '0.9rem', color: 'var(--text-main)', fontWeight: 500 }}>{fs.name}</h4>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Cluster: {fs.cluster}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {isDropdownOpen && searchTerm !== "" && filteredSearch.length === 0 && (
              <div className="glass-panel" style={{ position: 'absolute', top: '50px', left: 0, width: '100%', background: 'rgba(255,255,255,0.95)', zIndex: 50, padding: '1rem', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                No tracker matching this alias.
              </div>
            )}
          </div>

          <a href="/modules" style={{ background: 'rgba(124, 58, 237, 0.1)', border: '1px solid rgba(124, 58, 237, 0.3)', color: '#7c3aed', padding: '0.65rem 1.2rem', borderRadius: '50px', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontFamily: 'inherit', textDecoration: 'none', transition: 'all 0.2s ease' }}>
            <BookOpen style={{ width: '16px', height: '16px' }} /> Modules
          </a>

          <button className="btn-glow" onClick={deployAI} disabled={isGenerating}>
            {isGenerating ? (
              <><span style={{ width: '18px', height: '18px', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 1s linear infinite', display: 'inline-block' }}></span> Generating...</>
            ) : (
              <><Sparkles style={{ width: '18px', height: '18px' }} /> Deploy AI</>
            )}
          </button>

          {authUser && (
            <button onClick={handleLogout} style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', color: '#ef4444', padding: '0.6rem 1rem', borderRadius: '50px', cursor: 'pointer', fontWeight: 600, fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'inherit' }}>
              <LogOut style={{ width: '14px', height: '14px' }} /> Logout
            </button>
          )}
        </div>
      </div>

      {/* SUBJECT NAVIGATION BAR */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginRight: '0.5rem' }}>
          <Calendar style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
          <span style={{ color: '#94a3b8', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Weekly Schedule</span>
        </div>
        {SCHEDULE.map(subj => (
          <button
            key={subj.key}
            onClick={() => setActiveSubject(subj.key)}
            style={{
              padding: '0.6rem 1.25rem', borderRadius: '50px', cursor: 'pointer', fontFamily: 'inherit',
              fontWeight: 600, fontSize: '0.85rem', transition: 'all 0.2s ease', display: 'flex', alignItems: 'center', gap: '0.5rem',
              background: activeSubject === subj.key ? subj.color + '18' : 'rgba(0,0,0,0.03)',
              border: activeSubject === subj.key ? `2px solid ${subj.color}` : '2px solid rgba(0,0,0,0.06)',
              color: activeSubject === subj.key ? subj.color : '#64748b',
              boxShadow: activeSubject === subj.key ? `0 4px 16px ${subj.color}20` : 'none',
            }}
          >
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: subj.color, opacity: activeSubject === subj.key ? 1 : 0.4 }} />
            {subj.day} — {subj.label}
          </button>
        ))}
        {pipelineInfo && (
          <span style={{ marginLeft: 'auto', fontSize: '0.7rem', padding: '0.35rem 0.75rem', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', color: '#059669', borderRadius: '50px', fontWeight: 600 }}>
            ✓ {pipelineInfo}
          </span>
        )}
      </div>

      {/* OVERLAY MODAL FOR ABOUT EMERGENCE */}
      {showAbout && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(10px)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setShowAbout(false)}>
          <div className="glass-panel" style={{ width: '700px', maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto', padding: '2.5rem', background: 'rgba(255,255,255,0.95)', border: '1px solid rgba(139, 92, 246, 0.4)', boxShadow: '0 0 60px rgba(139, 92, 246, 0.15)' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-main)', background: '-webkit-linear-gradient(right, #22d3ee, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>EMERGENCE</h2>
                <h3 style={{ fontSize: '1rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>An Intelligent Classroom Learning System</h3>
              </div>
              <button onClick={() => setShowAbout(false)} style={{ background: 'rgba(0,0,0,0.05)', border: 'none', color: 'var(--text-main)', padding: '0.5rem', borderRadius: '50%', cursor: 'pointer' }}>
                <X style={{ width: '20px', height: '20px' }} />
              </button>
            </div>

            <div style={{ color: 'var(--text-main)', fontSize: '0.95rem', lineHeight: '1.7', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <p>
                <strong style={{ color: '#0284c7' }}>EMERGENCE</strong> is a state-of-the-art cognitive behavioral pipeline engineered to fuse continuous spatial reasoning and academic records into predictive pedagogical outcomes.
              </p>
              <p>
                By employing a multi-view <strong>Re-Identification (ReID) Pipeline</strong> running on OSNet and dynamic YOLO tracking, the system continuously analyzes student gaze, posture, and attention. This data is intelligently aligned with academic scoring matrices.
              </p>
              <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.03)', borderRadius: '8px', borderLeft: '4px solid #8b5cf6' }}>
                The core innovation resides in its <strong>Generative Curriculum Feedback Loop</strong>. By distilling complex behavioral and academic logs, EMERGENCE triggers Gemini LLMs to autonomously formulate tailored stabilizing and excelling modules dynamically personalized for every student.
              </div>
              <p style={{ marginTop: '1rem', color: '#94a3b8', fontStyle: 'italic', fontSize: '0.9rem' }}>
                Engineered for edge-deployment in active classroom environments.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* OVERLAY MODAL FOR SELECTED STUDENT DETAIL */}
      {selectedStudent && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setSelectedStudent(null)}>
          <div className="glass-panel" style={{ width: '800px', maxWidth: '90vw', maxHeight: '90vh', padding: '0', overflowY: 'auto', border: '1px solid rgba(34, 211, 238, 0.3)', boxShadow: '0 0 50px rgba(34,211,238,0.1)', background: 'rgba(255,255,255,0.95)' }} onClick={(e) => e.stopPropagation()}>

            {/* Modal Header */}
            <div style={{ background: 'linear-gradient(135deg, rgba(248,250,252,0.9), rgba(241,245,249,0.9))', padding: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid rgba(0,0,0,0.05)' }}>
              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${selectedStudent.name}&backgroundColor=0f172a`} style={{ width: '80px', height: '80px', borderRadius: '16px', border: '2px solid rgba(0,0,0,0.1)' }} alt="" />
                <div>
                  <h2 style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--text-main)', lineHeight: 1.1 }}>{selectedStudent.name}</h2>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.5rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                    <span>ID: {selectedStudent.sap_id}</span>
                    <span style={{ padding: '0.2rem 0.6rem', borderRadius: '50px', background: 'rgba(0,0,0,0.05)', color: 'var(--text-main)', fontWeight: 600, fontSize: '0.75rem', letterSpacing: '1px', textTransform: 'uppercase' }}>{selectedStudent.cluster} Verdict</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setSelectedStudent(null)} style={{ background: 'rgba(0,0,0,0.05)', border: 'none', color: 'var(--text-main)', padding: '0.5rem', borderRadius: '50%', cursor: 'pointer' }}>
                <X style={{ width: '20px', height: '20px' }} />
              </button>
            </div>

            {/* Modal Body / Metrics */}
            <div style={{ padding: '2rem', display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 1fr', gap: '2rem' }}>

              {/* Vision Core Breakdown */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#0284c7', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Eye style={{ width: '18px', height: '18px' }} /> Vision Engagement Breakdown</h3>
                <div style={{ background: 'rgba(0,0,0,0.03)', borderRadius: '12px', padding: '1rem', border: '1px solid rgba(0,0,0,0.05)' }}>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Overall Aggregated Attention</span>
                    <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{selectedStudent.vision_score}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: 'rgba(0,0,0,0.1)', borderRadius: '10px', marginBottom: '1.5rem' }}>
                    <div style={{ width: `${selectedStudent.vision_score}%`, height: '100%', background: '#0284c7', borderRadius: '10px' }}></div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Gaze Target Precision</span>
                    <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{selectedStudent.gaze_score}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: 'rgba(0,0,0,0.1)', borderRadius: '10px', marginBottom: '1.5rem' }}>
                    <div style={{ width: `${selectedStudent.gaze_score}%`, height: '100%', background: '#7c3aed', borderRadius: '10px' }}></div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Physiological Posture</span>
                    <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{selectedStudent.posture_score}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: 'rgba(0,0,0,0.1)', borderRadius: '10px' }}>
                    <div style={{ width: `${selectedStudent.posture_score}%`, height: '100%', background: '#059669', borderRadius: '10px' }}></div>
                  </div>

                </div>
              </div>

              {/* Academic Core Breakdown (Bar Chart) */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <h3 style={{ fontSize: '1.1rem', color: '#d97706', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><ClipboardCheck style={{ width: '18px', height: '18px' }} /> Academic Performance Logs</h3>
                <div style={{ background: 'rgba(0,0,0,0.03)', borderRadius: '12px', padding: '1rem', border: '1px solid rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', gap: '1rem', height: '260px' }}>
                  <div style={{ flexGrow: 1, position: 'relative' }}>
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
                      <ResponsiveContainer width="99%" height="100%">
                        <BarChart data={[
                        { name: 'Test 1', score: selectedStudent.test1 },
                        { name: 'Test 2', score: selectedStudent.test2 },
                        { name: 'Test 3', score: selectedStudent.test3 }
                      ]} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.1)" />
                        <XAxis dataKey="name" tick={{fill: '#475569', fontSize: 12}} axisLine={false} tickLine={false} />
                        <YAxis domain={[0, 20]} tick={{fill: '#475569', fontSize: 12}} axisLine={false} tickLine={false} />
                        <RechartsTooltip cursor={{fill: 'rgba(0,0,0,0.05)'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}} />
                        <Bar dataKey="score" fill="#f59e0b" radius={[4, 4, 0, 0]} barSize={40} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.5rem', borderTop: '1px dashed rgba(0,0,0,0.1)' }}>
                    <span style={{ color: '#d97706', fontSize: '0.95rem', fontWeight: 600 }}>Aggregated Matrix Score</span>
                    <span style={{ color: '#d97706', fontWeight: 700, fontSize: '1.2rem' }}>{selectedStudent.test_score}%</span>
                  </div>
                </div>
              </div>

              {/* Generative AI Assessment (Full Width) */}
              <div style={{ gridColumn: '1 / -1', background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.95))', borderRadius: '16px', padding: '2rem', border: '1px solid rgba(139, 92, 246, 0.25)', boxShadow: '0 4px 24px rgba(139, 92, 246, 0.08)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(139, 92, 246, 0.15)' }}>
                  <h3 style={{ fontSize: '1rem', color: '#7c3aed', display: 'flex', alignItems: 'center', gap: '0.5rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}><BookOpen style={{ width: '16px', height: '16px' }} /> AI Generative Action Plan</h3>
                  <span style={{ fontSize: '0.7rem', padding: '0.25rem 0.6rem', background: 'rgba(139,92,246,0.1)', color: '#7c3aed', borderRadius: '50px', fontWeight: 600, letterSpacing: '0.5px' }}>{pipelineInfo || 'DEEPSEEK V3 → MINIMAX M2.5'}</span>
                </div>
                <div style={{ color: 'var(--text-main)', lineHeight: 1.7, fontSize: '0.95rem' }}>
                  {renderModule(selectedStudent.module)}
                </div>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* 2. Top Metric HUD */}
      <div className="metrics-grid">
        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="m-title">Total Processed</span>
            <div className="icon-wrap"><Users style={{ width: '16px', height: '16px', color: '#22d3ee' }} /></div>
          </div>
          <div className="m-value">{data.length}</div>
          <div className="m-subtitle">
            <span className="badge cyan">{visionCount > 0 ? `${visionCount} Tracked` : 'Synthetic'}</span> {subjectMeta?.hasRealVision ? 'Vision + Academic Fused' : 'Academic Mapped'}
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="m-title">Excelling Demographics</span>
            <div className="icon-wrap"><BadgeCheck style={{ width: '16px', height: '16px', color: '#10b981' }} /></div>
          </div>
          <div className="m-value">{excelling.length}</div>
          <div className="m-subtitle">
            <span className="badge emerald">Optimized</span> Ready for Advanced Logic
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="m-title">Developing Demographics</span>
            <div className="icon-wrap"><Activity style={{ width: '16px', height: '16px', color: '#3b82f6' }} /></div>
          </div>
          <div className="m-value">{developing.length}</div>
          <div className="m-subtitle">
            <span className="badge muted">Stable</span> Maintaining baseline retention
          </div>
        </div>

        <div className="glass-panel metric-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span className="m-title">Struggling / Unfocused</span>
            <div className="icon-wrap"><ShieldAlert style={{ width: '16px', height: '16px', color: '#f43f5e' }} /></div>
          </div>
          <div className="m-value">{struggling.length}</div>
          <div className="m-subtitle">
            {struggling.length > 0 ? <><span className="badge rose">Urgent</span> Requires manual intervention</> : <><span className="badge emerald">Zero</span> No struggling students found!</>}
          </div>
        </div>
      </div>

      {/* AUTHORITY VIDEO & CLASS DISTRIBUTION */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1rem', marginBottom: '1rem' }}>
        
        {/* Authority View Video */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div className="section-head" style={{ marginBottom: '1rem', borderBottom: 'none', paddingBottom: 0 }}>
            <ShieldAlert style={{ width: '20px', height: '20px', color: '#e11d48' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#e11d48' }}>Authority View: {currentSchedule?.label || 'Class'} Recording</h2>
          </div>
          <div style={{ flexGrow: 1, borderRadius: '12px', overflow: 'hidden', border: '2px solid rgba(225, 29, 72, 0.3)', boxShadow: '0 4px 20px rgba(225, 29, 72, 0.1)', background: '#000' }}>
            <video src={`/${subjectMeta?.video || 'annotated_Main_Test.mp4'}`} controls muted style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}></video>
          </div>
        </div>

        {/* Bell Curve Distribution */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div className="section-head" style={{ marginBottom: '1rem', borderBottom: 'none', paddingBottom: 0 }}>
            <Activity style={{ width: '20px', height: '20px', color: '#2563eb' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Class Overall Engagement Density</h2>
          </div>
          <div style={{ height: '250px', width: '100%', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}>
              <ResponsiveContainer width="99%" height="100%">
                <AreaChart data={
                Array.from({length: 10}, (_, i) => {
                  const min = i * 10;
                  const max = (i + 1) * 10;
                  const count = data.filter(s => s.combined_score >= min && (i===9 ? s.combined_score <= max : s.combined_score < max)).length;
                  return { range: `${min}-${max}%`, density: count };
                })
              } margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDensity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#7c3aed" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                <XAxis dataKey="range" tick={{fill: '#475569', fontSize: 11}} axisLine={false} tickLine={false} />
                <YAxis tick={{fill: '#475569', fontSize: 11}} axisLine={false} tickLine={false} allowDecimals={false} />
                <RechartsTooltip cursor={{stroke: 'rgba(124,58,237,0.3)', strokeWidth: 2}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)'}} />
                <Area type="monotone" dataKey="density" stroke="#7c3aed" strokeWidth={3} fillOpacity={1} fill="url(#colorDensity)" />
              </AreaChart>
            </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>

      {/* 3. Main Data Layer (Left: Leaderboard, Right: Clusters) */}
      <div className="main-grid">

        {/* LEADERBOARD PANEL */}
        <div className="glass-panel leaderboard-panel">
          <div className="section-head">
            <Trophy style={{ width: '20px', height: '20px', color: '#fbbf24' }} />
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Top Performers</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {topPerformers.map((s, i) => (
              <div key={i} className="lb-item" onClick={() => setSelectedStudent(s)} style={{ cursor: 'pointer' }}>
                <div className="lb-rank">#{i + 1}</div>
                <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${s.name}&backgroundColor=0f172a`} className="lb-avatar" alt="" />
                <div style={{ flexGrow: 1 }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 500 }}>{s.name}</h4>
                  <p style={{ fontSize: '0.8rem', color: '#22d3ee', fontWeight: 600, marginTop: '0.1rem' }}>Overall Engine Score: {s.combined_score}%</p>
                </div>
              </div>
            ))}
          </div>

          {absent.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className="section-head" style={{ marginBottom: '1rem', borderBottom: '1px solid rgba(0,0,0,0.05)', paddingBottom: '1rem' }}>
                <h2 style={{ color: 'var(--text-muted)', fontSize: '1.25rem', fontWeight: 600 }}>Absent Log</h2>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {absent.map((s, i) => (
                  <div key={i} onClick={() => setSelectedStudent(s)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', padding: '0.5rem 0.75rem', borderRadius: '8px', background: 'rgba(0,0,0,0.03)', border: '1px solid rgba(0,0,0,0.05)', cursor: 'pointer' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>{s.name}</span>
                    <span style={{ color: '#e11d48', fontWeight: 600 }}>Offline</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* CLUSTERS & AI GENERATION PANEL */}
        <div className="clusters-wrapper">

          {/* STRUGGLING BLOCK (Moved to TOP to highlight them!) */}
          {struggling.length > 0 ? (
            <div className="glass-panel cluster-block struggling">
              <div>
                <h3 style={{ color: '#f43f5e', fontWeight: 600, marginBottom: '1rem', fontSize: '1.125rem' }}>Struggling Threshold ( &le; 50% )</h3>
                <div className="roster-list">
                  {struggling.map((s, i) => <StudentRow key={i} s={s} />)}
                </div>
              </div>
              <div className="ai-module-box">
                <div className="ai-badge">DeepSeek V3 Generated</div>
                <div className="ai-header"><BrainCircuit style={{ width: '16px', height: '16px' }} /> Adaptive Curriculum Protocol</div>
                <div className="ai-content" style={{ color: '#fecdd3' }}>{renderModule(struggling[0]?.module)}</div>
              </div>
            </div>
          ) : (
            <div className="glass-panel" style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 1.5rem', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
              <ShieldAlert style={{ width: '24px', height: '24px', color: '#10b981' }} />
              <div>
                <h3 style={{ color: '#10b981', fontWeight: 600, fontSize: '1.1rem' }}>Zero Struggling Students</h3>
                <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>No student dropped below the 50% critical baseline threshold.</p>
              </div>
            </div>
          )}

          {/* EXCELLING BLOCK */}
          {excelling.length > 0 && (
            <div className="glass-panel cluster-block excelling">
              <div>
                <h3 style={{ color: '#34d399', fontWeight: 600, marginBottom: '1rem', fontSize: '1.125rem' }}>Excelling Threshold ( &ge; 70% )</h3>
                <div className="roster-list">
                  {excelling.map((s, i) => <StudentRow key={i} s={s} />)}
                </div>
              </div>
              <div className="ai-module-box">
                <div className="ai-badge">DeepSeek V3 Generated</div>
                <div className="ai-header"><BrainCircuit style={{ width: '16px', height: '16px' }} /> Adaptive Curriculum Protocol</div>
                <div className="ai-content">{renderModule(excelling[0]?.module)}</div>
              </div>
            </div>
          )}

          {/* DEVELOPING BLOCK */}
          {developing.length > 0 && (
            <div className="glass-panel cluster-block developing">
              <div>
                <h3 style={{ color: '#22d3ee', fontWeight: 600, marginBottom: '1rem', fontSize: '1.125rem' }}>Developing Threshold ( 51 - 69% )</h3>
                <div className="roster-list">
                  {developing.map((s, i) => <StudentRow key={i} s={s} />)}
                </div>
              </div>
              <div className="ai-module-box">
                <div className="ai-badge">DeepSeek V3 Generated</div>
                <div className="ai-header"><BrainCircuit style={{ width: '16px', height: '16px' }} /> Adaptive Curriculum Protocol</div>
                <div className="ai-content">{renderModule(developing[0]?.module)}</div>
              </div>
            </div>
          )}

        </div>

      </div>

      {/* Premium Footer */}
      <div style={{ marginTop: '3.5rem', paddingTop: '2rem', borderTop: '1px solid rgba(0,0,0,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '2rem' }}>
        <div>
          <h4 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>Engineered & Architected By</h4>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', background: '-webkit-linear-gradient(right, #0284c7, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', lineHeight: 1.2 }}>Mohit Yadav</h2>
          <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '0.25rem' }}>Pushing the boundaries of cognitive vision and spatial reasoning.</p>
        </div>
        <button onClick={() => setShowAbout(true)} style={{ background: 'rgba(0,0,0,0.03)', border: '1px solid rgba(0,0,0,0.1)', color: 'var(--text-main)', padding: '0.8rem 1.5rem', borderRadius: '8px', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'all 0.2s ease', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }} onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(0,0,0,0.05)'; e.currentTarget.style.borderColor = '#7c3aed'; }} onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(0,0,0,0.03)'; e.currentTarget.style.borderColor = 'rgba(0,0,0,0.1)'; }}>
          <Sparkles style={{ width: '18px', height: '18px', color: '#7c3aed' }} /> About EMERGENCE
        </button>
      </div>

    </div>
  );
}
