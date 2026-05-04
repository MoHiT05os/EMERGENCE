import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import json
import sys
import cv2
import base64
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
PROFILES_DIR = DATA_DIR / "profiles"
INPUT_DIR = DATA_DIR / "input"
MAPPING_FRAMES_DIR = OUTPUT_DIR / "mapping_frames"

st.set_page_config(
    page_title="EMERGENCE – Intelligent Classroom Learning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --bg-glass: rgba(255, 255, 255, 0.9);
    --border-subtle: rgba(99, 102, 241, 0.2);
    --border-glow: rgba(99, 102, 241, 0.5);
    --accent-primary: #4f46e5;
    --accent-secondary: #7c3aed;
    --accent-gradient: linear-gradient(135deg, #4f46e5, #7c3aed, #8b5cf6);
    --text-primary: #0f172a;
    --text-secondary: #334155;
    --text-muted: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --info: #3b82f6;
}

html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background: var(--bg-primary) !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

.hero-section {
    position: relative;
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 35%, #a5b4fc 65%, #c7d2fe 100%);
    padding: 3rem 2.5rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    overflow: hidden;
    border: 1px solid rgba(99, 102, 241, 0.3);
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.15), 0 10px 30px rgba(0, 0, 0, 0.05);
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    position: relative;
    z-index: 1;
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #312e81 0%, #4338ca 50%, #4f46e5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin: 0;
    line-height: 1.1;
}
.hero-subtitle {
    position: relative;
    z-index: 1;
    color: #4338ca;
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}
.glass-card:hover {
    border-color: var(--border-glow);
    box-shadow: 0 8px 40px rgba(99, 102, 241, 0.12), 0 4px 24px rgba(0, 0, 0, 0.3);
    transform: translateY(-2px);
}

.metric-card-v2 {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    text-align: left;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card-v2::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--accent-gradient);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.metric-card-v2:hover::before { opacity: 1; }
.metric-card-v2:hover {
    border-color: var(--border-glow);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
}
.metric-label {
    color: var(--text-muted);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 0.4rem;
}
.metric-value {
    color: var(--text-primary);
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    font-family: 'JetBrains Mono', monospace;
}
.metric-sub {
    color: var(--text-secondary);
    font-size: 0.75rem;
    margin-top: 0.2rem;
}

.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.badge-struggling { background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.25); }
.badge-developing { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }
.badge-excelling { background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.25); }
.badge-needs { background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.25); }
.badge-active { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }
.badge-engaged { background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.25); }

.student-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 0.8rem;
    transition: all 0.3s ease;
}
.student-card:hover {
    border-color: var(--border-glow);
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.1);
}
.student-name {
    color: var(--text-primary);
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 2px;
}
.student-sap {
    color: var(--text-muted);
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.6rem;
}
.student-stat {
    color: var(--text-secondary);
    font-size: 0.8rem;
    margin: 3px 0;
    display: flex;
    justify-content: space-between;
}
.student-stat strong {
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}

.pipeline-step {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 1.3rem;
    text-align: center;
    transition: all 0.3s ease;
}
.pipeline-step:hover {
    border-color: var(--border-glow);
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.08);
}
.pipeline-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.pipeline-label {
    color: var(--accent-primary);
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.pipeline-desc {
    color: var(--text-secondary);
    font-size: 0.78rem;
    line-height: 1.4;
}

.video-container {
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    overflow: hidden;
    background: var(--bg-secondary);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}

.arch-flow {
    background: linear-gradient(135deg, #0c1020 0%, #0f172a 50%, #1e1b4b 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
}

div[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem !important;
}
</style>
"""
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.8)",
    font=dict(color="#334155", family="Inter", size=12),
    xaxis=dict(gridcolor="rgba(99,102,241,0.15)", zerolinecolor="rgba(99,102,241,0.2)"),
    yaxis=dict(gridcolor="rgba(99,102,241,0.15)", zerolinecolor="rgba(99,102,241,0.2)"),
    margin=dict(t=50, b=40, l=40, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)
COLOR_MAP = {
    "Needs Support": "#f87171", "Active": "#fbbf24", "Highly Engaged": "#34d399",
    "Struggling": "#f87171", "Developing": "#fbbf24", "Excelling": "#34d399",
}
BADGE_MAP = {
    "Struggling": "struggling", "Developing": "developing", "Excelling": "excelling",
    "Needs Support": "needs", "Active": "active", "Highly Engaged": "engaged",
}


@st.cache_data
def load_engagement_log():
    p = OUTPUT_DIR / "engagement_log.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def load_test_engagement_log():
    p = OUTPUT_DIR / "test_engagement_log.csv"
    return pd.read_csv(p) if p.exists() else None

@st.cache_data
def load_student_profiles():
    for name in ["student_profiles_v2.csv", "student_profiles.csv"]:
        p = PROFILES_DIR / name
        if p.exists():
            return pd.read_csv(p)
    return None

@st.cache_data
def load_test_scores():
    p = INPUT_DIR / "normalized_student_data.xlsx"
    if not p.exists():
        return None
    df = pd.read_excel(p)
    df = df.rename(columns={"Student ID": "sap_id", "First Name": "first_name",
                             "Last Name": "last_name", "Test 1 Marks": "test1_score",
                             "Test 2 Marks": "test2_score", "Total": "total_score"})
    df["student_name"] = (df["first_name"].fillna("") + " " + df["last_name"].fillna("")).str.strip()
    df["test1_score"] = df["test1_score"].fillna(0)
    df["test2_score"] = df["test2_score"].fillna(0)
    df["total_score"] = df["test1_score"] + df["test2_score"]
    df["academic_score"] = df["total_score"] / 40.0
    return df

@st.cache_data
def load_student_mapping():
    p = PROFILES_DIR / "student_mapping.csv"
    return pd.read_csv(p) if p.exists() else None

def get_annotated_videos():
    videos = sorted(OUTPUT_DIR.glob("annotated_*.mp4"))
    return videos

def get_mapping_frames(tag):
    d = MAPPING_FRAMES_DIR / tag
    return sorted(d.glob("*.jpg")) if d.exists() else []

def load_generated_modules():
    modules = {}
    for f in sorted(OUTPUT_DIR.glob("module_*.md")):
        c = f.read_text(encoding="utf-8", errors="ignore")
        if "429" not in c and "Error" not in c[:50]:
            modules[f.stem] = c
    return modules


with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0.5rem; text-align:center;">
        <div style="font-size:1.8rem; font-weight:900; background: linear-gradient(135deg, #a78bfa, #6366f1);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-1px;">
            EMERGENCE
        </div>
        <div style="color:#64748b; font-size:0.65rem; letter-spacing:2px; text-transform:uppercase; margin-top:2px;">
            Adaptive Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Overview", "📊 Analytics", "📈 Test Performance",
         "🎬 Video Analysis", "👤 Student Profiles",
         "🔗 Student Mapping", "📝 Generated Content", "⚙️ Architecture"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(
        "<p style='color:#475569; font-size:0.65rem; text-align:center; letter-spacing:0.5px;'>"
        "Intelligent Classroom Learning System<br>v2.0 · © 2026</p>",
        unsafe_allow_html=True
    )


if page == "🏠 Overview":
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🧠 EMERGENCE</div>
        <div class="hero-subtitle">Adaptive Classroom Intelligence System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-bottom:1.5rem;">
        <p style="color:#334155; font-size:0.92rem; line-height:1.7; margin:0;">
            <strong style="color:#4f46e5;">EMERGENCE</strong> is a three-layer AI architecture that transforms
            traditional <em>one-size-fits-all</em> instruction into <strong style="color:#0f172a;">adaptive,
            student-centric education</strong> — observing engagement through computer vision,
            reasoning over behavioral + academic signals with machine learning,
            and generating personalized content via large language models.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_log = load_engagement_log()
    df_prof = load_student_profiles()
    df_scores = load_test_scores()

    id_col = "sap_id" if df_prof is not None and "sap_id" in df_prof.columns else "student_id"
    eng_col = "class_engagement" if df_prof is not None and "class_engagement" in df_prof.columns else "engagement_score"

    n_students = len(df_prof) if df_prof is not None else 0
    n_frames = df_log["frame"].nunique() if df_log is not None else 0
    avg_eng = df_prof[eng_col].mean() if df_prof is not None and eng_col in df_prof.columns else 0
    avg_score = df_scores["academic_score"].mean() if df_scores is not None else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub in [
        (c1, "Students Tracked", str(n_students), "unique IDs profiled"),
        (c2, "Frames Analyzed", f"{n_frames:,}", "video frames processed"),
        (c3, "Avg Engagement", f"{avg_eng:.0%}", "class-wide average"),
        (c4, "Avg Test Score", f"{avg_score:.0%}", "academic performance"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card-v2">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="section-title">🔄 Three-Layer Pipeline</div>', unsafe_allow_html=True)

    p1, p2, p3 = st.columns(3)
    for col, icon, label, desc in [
        (p1, "👁️", "Phase 1 — Vision", "YOLOv11 Detection · Pose Estimation · Motion Analysis → Engagement Score"),
        (p2, "🧮", "Phase 2 — Reasoning", "Data Fusion · K-Means Clustering (3D) → Struggling / Developing / Excelling"),
        (p3, "✨", "Phase 3 — Generation", "Gemini 2.0 Flash · Adaptive Prompts → Personalized Modules & Tests"),
    ]:
        with col:
            st.markdown(f"""
            <div class="pipeline-step">
                <div class="pipeline-icon">{icon}</div>
                <div class="pipeline-label">{label}</div>
                <div class="pipeline-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    videos = get_annotated_videos()
    main_test_video = OUTPUT_DIR / "annotated_Main_Test.mp4"
    
    if main_test_video.exists():
        st.markdown("")
        st.markdown('<div class="section-title" style="color:#ef4444;">🛡️ Authority View: Main Test Recording</div>', unsafe_allow_html=True)
        st.markdown('<div class="video-container" style="border: 2px solid #ef4444; box-shadow: 0 4px 20px rgba(239, 68, 68, 0.2);">', unsafe_allow_html=True)
        st.video(str(main_test_video))
        st.markdown('</div>', unsafe_allow_html=True)

    if videos:
        st.markdown("")
        st.markdown('<div class="section-title">🎬 Latest Annotated Video</div>', unsafe_allow_html=True)
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        st.video(str(videos[0]))
        st.markdown('</div>', unsafe_allow_html=True)


elif page == "📊 Analytics":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">📊 Engagement Analytics</div>', unsafe_allow_html=True)

    df_log = load_engagement_log()
    df_prof = load_student_profiles()

    if df_log is None or df_prof is None:
        st.warning("No data found. Run the vision pipeline first.")
        st.stop()

    id_col = "sap_id" if "sap_id" in df_prof.columns else "student_id"
    eng_col = "class_engagement" if "class_engagement" in df_prof.columns else "engagement_score"
    has_names = "student_name" in df_prof.columns
    status_col = "status" if "status" in df_prof.columns else None

    col1, col2 = st.columns(2)

    with col1:
        if status_col:
            counts = df_prof[status_col].value_counts().reset_index()
            counts.columns = ["Status", "Count"]
            fig = px.pie(counts, values="Count", names="Status", color="Status",
                         color_discrete_map=COLOR_MAP, hole=0.5)
            fig.update_traces(textposition='inside', textinfo='percent+label',
                              textfont_size=12, marker=dict(line=dict(color='#06080f', width=2)))
            fig.update_layout(**PLOTLY_LAYOUT, title="Cluster Distribution",
                              showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_bar = df_prof.sort_values(eng_col, ascending=True).copy()
        df_bar["label"] = df_bar["student_name"] if has_names else "Student " + df_bar[id_col].astype(str)
        colors = df_bar[status_col].map(COLOR_MAP).tolist() if status_col else ["#6366f1"] * len(df_bar)

        fig = go.Figure(go.Bar(
            x=df_bar[eng_col], y=df_bar["label"], orientation="h",
            marker_color=colors, marker_line=dict(width=0),
            text=df_bar[eng_col].apply(lambda x: f"{x:.0%}"), textposition="outside",
            textfont=dict(size=11, color="#94a3b8")
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title="Engagement per Student",
                          xaxis=dict(range=[0, 1], **PLOTLY_LAYOUT["xaxis"]),
                          height=max(400, len(df_bar) * 38))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        score_cols = [c for c in ["gaze_score", "posture_score", "motion_score", eng_col] if c in df_prof.columns]
        if status_col and score_cols:
            radar_data = df_prof.groupby(status_col)[score_cols].mean()
            cats = ["Gaze", "Posture", "Motion", "Engagement"][:len(score_cols)]
            fig = go.Figure()
            for status in radar_data.index:
                vals = radar_data.loc[status].tolist() + [radar_data.loc[status].tolist()[0]]
                fig.add_trace(go.Scatterpolar(
                    r=vals, theta=cats + [cats[0]], fill="toself", name=status,
                    line=dict(color=COLOR_MAP.get(status, "#6366f1"), width=2),
                    fillcolor=COLOR_MAP.get(status, "#6366f1").replace(")", ",0.1)").replace("rgb", "rgba") if "rgb" in COLOR_MAP.get(status, "") else f"rgba(99,102,241,0.1)"
                ))
            fig.update_layout(
                **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')},
                title="Metrics by Cluster",
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(99,102,241,0.08)"),
                           angularaxis=dict(gridcolor="rgba(99,102,241,0.08)")),
                height=420
            )
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        log_id = "student_name" if "student_name" in df_log.columns else ("sap_id" if "sap_id" in df_log.columns else "student_id")
        fig = px.line(df_log, x="frame", y="engagement_score",
                      color=df_log[log_id].astype(str) if log_id in df_log.columns else df_log["student_id"].astype(str))
        fig.update_layout(**PLOTLY_LAYOUT, title="Engagement Timeline",
                          yaxis=dict(range=[0, 1], **PLOTLY_LAYOUT["yaxis"]),
                          legend_title_text="Student", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">🔥 Engagement Heatmap</div>', unsafe_allow_html=True)
    heat_id = "student_name" if "student_name" in df_log.columns else "student_id"
    pivot = df_log.pivot_table(index=heat_id, columns="frame", values="engagement_score", aggfunc="mean")
    fig = px.imshow(pivot, labels=dict(x="Frame", y="Student", color="Engagement"),
                     color_continuous_scale=["#ef4444", "#f59e0b", "#10b981"], aspect="auto")
    fig.update_layout(**{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')},
                      height=350, coloraxis_colorbar=dict(tickfont=dict(color="#334155")))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📈 Overall Engagement Distribution (Bell Curve)</div>', unsafe_allow_html=True)
    if df_prof is not None and eng_col in df_prof.columns:
        eng_data = df_prof[eng_col].dropna().values
        if len(eng_data) > 1:
            mean_eng = np.mean(eng_data)
            std_eng = np.std(eng_data)
            if std_eng == 0: std_eng = 0.01
            
            x_range = np.linspace(max(0, mean_eng - 3*std_eng), min(1, mean_eng + 3*std_eng), 200)
            y_curve = (1 / (std_eng * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mean_eng) / std_eng)**2)
            
            fig_kde = go.Figure()
            fig_kde.add_trace(go.Scatter(
                x=x_range, y=y_curve, mode='lines', 
                fill='tozeroy', fillcolor='rgba(79, 70, 229, 0.2)',
                line=dict(color='#4f46e5', width=3),
                name='Distribution'
            ))
            
            y_points = (1 / (std_eng * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((eng_data - mean_eng) / std_eng)**2)
            colors = df_prof[status_col].map(COLOR_MAP).tolist() if status_col else ["#4f46e5"] * len(eng_data)
            names = df_prof["student_name"] if has_names else df_prof[id_col].astype(str)
            
            fig_kde.add_trace(go.Scatter(
                x=eng_data, y=y_points, mode='markers',
                marker=dict(size=12, color=colors, line=dict(width=1, color='#ffffff')),
                text=names, hoverinfo='text+x',
                name='Students'
            ))
            
            layout_kde = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
            fig_kde.update_layout(**layout_kde, 
                xaxis=dict(title="Engagement Score", range=[0, 1], gridcolor="rgba(99,102,241,0.15)"),
                yaxis=dict(title="Density", showticklabels=False, gridcolor="rgba(99,102,241,0.15)"),
                height=400, showlegend=True
            )
            st.plotly_chart(fig_kde, use_container_width=True)


elif page == "📈 Test Performance":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">📈 Test Performance & Learning Analysis</div>', unsafe_allow_html=True)

    df_scores = load_test_scores()
    df_prof = load_student_profiles()

    if df_scores is None:
        st.warning("No test score data found.")
        st.stop()

    avg_t1 = df_scores["test1_score"].mean()
    avg_t2 = df_scores["test2_score"].mean()
    avg_total = df_scores["total_score"].mean()
    pass_rate = (df_scores["academic_score"] >= 0.5).mean()

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub in [
        (c1, "Test 1 — Easy", f"{avg_t1:.1f}/20", f"{avg_t1/20:.0%} average"),
        (c2, "Test 2 — Medium", f"{avg_t2:.1f}/20", f"{avg_t2/20:.0%} average"),
        (c3, "Total Score", f"{avg_total:.1f}/40", f"{avg_total/40:.0%} overall"),
        (c4, "Pass Rate (≥50%)", f"{pass_rate:.0%}", f"{int(pass_rate * len(df_scores))}/{len(df_scores)} students"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card-v2">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        df_s = df_scores.sort_values("total_score", ascending=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(y=df_s["student_name"], x=df_s["test1_score"], name="Test 1 (Easy)",
                             orientation="h", marker_color="#6366f1",
                             text=df_s["test1_score"].apply(lambda x: f"{x:.0f}"), textposition="inside"))
        fig.add_trace(go.Bar(y=df_s["student_name"], x=df_s["test2_score"], name="Test 2 (Medium)",
                             orientation="h", marker_color="#8b5cf6",
                             text=df_s["test2_score"].apply(lambda x: f"{x:.0f}"), textposition="inside"))
        layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
        fig.update_layout(**layout, barmode="stack", title="Scores by Student",
                          xaxis=dict(range=[0, 42], gridcolor="rgba(99,102,241,0.06)"),
                          yaxis=dict(gridcolor="rgba(99,102,241,0.06)"),
                          height=max(500, len(df_scores) * 28))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if df_prof is not None and "class_engagement" in df_prof.columns and "academic_score" in df_prof.columns:
            s_df = df_prof.copy()
            name_c = "student_name" if "student_name" in s_df.columns else None
            status_c = "status" if "status" in s_df.columns else None

            fig = px.scatter(s_df, x="class_engagement", y="academic_score",
                             color=status_c, color_discrete_map=COLOR_MAP,
                             hover_name=name_c, size_max=15)
            fig.add_hline(y=0.5, line_dash="dot", line_color="rgba(148,163,184,0.2)")
            fig.add_vline(x=0.55, line_dash="dot", line_color="rgba(148,163,184,0.2)")
            fig.add_annotation(x=0.8, y=0.85, text="⭐ Excelling", showarrow=False, font=dict(color="#34d399", size=11))
            fig.add_annotation(x=0.3, y=0.85, text="📚 Self-Learner", showarrow=False, font=dict(color="#fbbf24", size=11))
            fig.add_annotation(x=0.8, y=0.2, text="🤔 Concept Gap", showarrow=False, font=dict(color="#fbbf24", size=11))
            fig.add_annotation(x=0.3, y=0.2, text="🔴 Struggling", showarrow=False, font=dict(color="#f87171", size=11))
            layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
            fig.update_layout(**layout, title="Engagement vs. Academic Score",
                              xaxis=dict(range=[0, 1], title="Class Engagement", gridcolor="rgba(99,102,241,0.06)"),
                              yaxis=dict(range=[0, 1], title="Academic Score", gridcolor="rgba(99,102,241,0.06)"),
                              height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Complete the student mapping to see the scatter plot.")

    if df_prof is not None and "learning_level" in df_prof.columns:
        st.markdown('<div class="section-title">🧠 Learning Level Distribution</div>', unsafe_allow_html=True)
        ll_counts = df_prof["learning_level"].value_counts()
        ll_colors = {"Analytical Thinker": "#34d399", "Conceptual Learner": "#6ee7b7",
                     "Self-Learner": "#fbbf24", "Conceptual Gap": "#fb7185", "Foundational Need": "#f87171", "Standard": "#6366f1"}
        fig = px.pie(values=ll_counts.values, names=ll_counts.index,
                     color=ll_counts.index, color_discrete_map=ll_colors, hole=0.5)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          marker=dict(line=dict(color='#06080f', width=2)))
        fig.update_layout(**{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')},
                          title="", showlegend=True, height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📊 Score Distribution</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df_scores["test1_score"], name="Test 1 (Easy)",
                                marker_color="rgba(99,102,241,0.5)", nbinsx=10))
    fig.add_trace(go.Histogram(x=df_scores["test2_score"], name="Test 2 (Medium)",
                                marker_color="rgba(139,92,246,0.5)", nbinsx=10))
    layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
    fig.update_layout(**layout, barmode="overlay", title="Easy vs. Medium Score Spread",
                      xaxis=dict(title="Score", gridcolor="rgba(99,102,241,0.06)"),
                      yaxis=dict(title="Count", gridcolor="rgba(99,102,241,0.06)"),
                      height=350)
    st.plotly_chart(fig, use_container_width=True)


elif page == "🎬 Video Analysis":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">🎬 Annotated Video Analysis</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-bottom:1.5rem;">
        <p style="color:#cbd5e1; font-size:0.88rem; margin:0;">
            These videos show <strong style="color:#a78bfa;">real-time engagement detection</strong> overlaid on classroom footage.
            Each student is tracked with bounding boxes, engagement scores, gaze & posture metrics,
            and color-coded status indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)

    videos = get_annotated_videos()

    if videos:
        video_names = {v.stem.replace("annotated_", "").replace("_", " ").title(): v for v in videos}

        selected = st.selectbox("Select Video", list(video_names.keys()))
        if selected:
            video_path = video_names[selected]
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(str(video_path))
            st.markdown('</div>', unsafe_allow_html=True)

            file_size = video_path.stat().st_size / (1024 * 1024)
            cap = cv2.VideoCapture(str(video_path))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            mc1, mc2, mc3, mc4 = st.columns(4)
            for col, label, val in [
                (mc1, "Duration", f"{duration:.1f}s"),
                (mc2, "Resolution", f"{w}×{h}"),
                (mc3, "Frames", f"{total_frames:,}"),
                (mc4, "File Size", f"{file_size:.1f} MB"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="metric-card-v2">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value" style="font-size:1.4rem;">{val}</div>
                    </div>""", unsafe_allow_html=True)

        if len(videos) > 1:
            st.markdown('<div class="section-title">📂 All Annotated Videos</div>', unsafe_allow_html=True)
            for v in videos:
                name = v.stem.replace("annotated_", "").replace("_", " ").title()
                size = v.stat().st_size / (1024 * 1024)
                with st.expander(f"🎥 {name} ({size:.1f} MB)"):
                    st.video(str(v))
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🎥</div>
            <div style="color:#f1f5f9; font-size:1.1rem; font-weight:600; margin-bottom:0.5rem;">
                No Annotated Videos Yet
            </div>
            <div style="color:#64748b; font-size:0.85rem;">
                Run the vision pipeline to generate annotated videos with engagement overlays:<br>
                <code style="color:#a78bfa; background:rgba(99,102,241,0.1); padding:4px 10px; border-radius:6px; margin-top:8px; display:inline-block;">
                    python main.py --source data/input/iNPUT.mp4
                </code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    mapping_frames_dirs = [d for d in MAPPING_FRAMES_DIR.iterdir() if d.is_dir()] if MAPPING_FRAMES_DIR.exists() else []
    if mapping_frames_dirs:
        st.markdown('<div class="section-title">📸 Detection Snapshots</div>', unsafe_allow_html=True)
        for d in sorted(mapping_frames_dirs):
            frames = sorted(d.glob("*.jpg"))
            if frames:
                tag = d.name.replace("_", " ").title()
                with st.expander(f"📁 {tag} ({len(frames)} frames)"):
                    cols = st.columns(min(3, len(frames)))
                    for i, f in enumerate(frames[:6]):
                        with cols[i % 3]:
                            st.image(str(f), caption=f.name, use_container_width=True)


elif page == "👤 Student Profiles":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">👤 Student Profiles</div>', unsafe_allow_html=True)

    df_prof = load_student_profiles()
    if df_prof is None:
        st.warning("No profile data. Run the pipeline first.")
        st.stop()

    id_col = "sap_id" if "sap_id" in df_prof.columns else "student_id"
    has_names = "student_name" in df_prof.columns
    eng_col = "class_engagement" if "class_engagement" in df_prof.columns else "engagement_score"
    status_col = "status"

    if status_col in df_prof.columns:
        status_counts = df_prof[status_col].value_counts()
        emoji_map = {"Struggling": "🔴", "Developing": "🟡", "Excelling": "🟢",
                     "Needs Support": "🔴", "Active": "🟡", "Highly Engaged": "🟢"}
        cols = st.columns(min(len(status_counts), 3))
        for i, (status, count) in enumerate(status_counts.items()):
            with cols[i % 3]:
                e = emoji_map.get(status, "⚪")
                st.markdown(f"""
                <div class="metric-card-v2">
                    <div class="metric-label">{e} {status}</div>
                    <div class="metric-value">{count}</div>
                    <div class="metric-sub">students</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("")

    display_df = df_prof.copy()
    rename = {}
    if id_col == "sap_id": rename["sap_id"] = "SAP ID"
    else: rename["student_id"] = "Student ID"
    if has_names: rename["student_name"] = "Name"
    if eng_col in display_df.columns: rename[eng_col] = "Engagement"
    for c in ["test_engagement", "academic_score", "test1_score", "test2_score",
              "total_score", "status", "learning_level"]:
        if c in display_df.columns:
            rename[c] = c.replace("_", " ").title()

    display_df = display_df.rename(columns=rename)
    for c in ["Engagement", "Test Engagement", "Academic Score"]:
        if c in display_df.columns:
            display_df[c] = display_df[c].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")

    hide = [c for c in display_df.columns if any(k in c.lower() for k in
            ["cluster", "test gaze", "test posture", "test motion", "first name", "last name",
             "test1 norm", "test2 norm", "gaze score", "posture score", "motion score"])]
    show = [c for c in display_df.columns if c not in hide]
    st.dataframe(display_df[show], use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">🔍 Student Detail</div>', unsafe_allow_html=True)

    if has_names:
        names = df_prof["student_name"].dropna().unique().tolist()
        selected_name = st.selectbox("Select Student", names)
        student = df_prof[df_prof["student_name"] == selected_name].iloc[0]
    else:
        ids = df_prof[id_col].tolist()
        sel = st.selectbox("Select Student", ids, format_func=lambda x: f"Student {x}")
        student = df_prof[df_prof[id_col] == sel].iloc[0]

    status = student.get("status", "Active")
    ll = student.get("learning_level", "—")
    badge = BADGE_MAP.get(status, "active")

    sc1, sc2 = st.columns([1, 2])
    with sc1:
        name_d = student.get("student_name", f"Student {student.get(id_col, '?')}")
        sap_d = student.get("sap_id", student.get("student_id", ""))
        c_eng = student.get("class_engagement", student.get("engagement_score", 0))
        t_eng = student.get("test_engagement", None)
        acad = student.get("academic_score", None)
        t1 = student.get("test1_score", "—")
        t2 = student.get("test2_score", "—")

        t_eng_d = f"{t_eng:.0%}" if isinstance(t_eng, (int, float)) and pd.notna(t_eng) else "—"
        acad_d = f"{acad:.0%}" if isinstance(acad, (int, float)) and pd.notna(acad) else "—"

        st.markdown(f"""
        <div class="student-card">
            <div class="student-name">{name_d}</div>
            <div class="student-sap">SAP: {sap_d}</div>
            <span class="badge badge-{badge}">{status}</span>
            <div style="margin-top:0.8rem;">
                <div class="student-stat"><span>🎯 Learning Level</span><strong>{ll}</strong></div>
                <div class="student-stat"><span>📊 Class Engagement</span><strong>{c_eng:.0%}</strong></div>
                <div class="student-stat"><span>📝 Test Focus</span><strong>{t_eng_d}</strong></div>
                <div class="student-stat"><span>🏆 Academic Score</span><strong>{acad_d}</strong></div>
                <div class="student-stat"><span>✏️ Test 1 (Easy)</span><strong>{t1}/20</strong></div>
                <div class="student-stat"><span>✏️ Test 2 (Medium)</span><strong>{t2}/20</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        radar_cols = [c for c in ["gaze_score", "posture_score", "motion_score"] if c in student.index]
        vals = [student[c] for c in radar_cols] + [c_eng]
        cats = ["Gaze", "Posture", "Motion", "Engagement"][:len(vals)]
        vals_c = vals + [vals[0]]
        cats_c = cats + [cats[0]]

        fig = go.Figure(go.Scatterpolar(
            r=vals_c, theta=cats_c, fill="toself",
            line=dict(color="#6366f1", width=2),
            fillcolor="rgba(99,102,241,0.12)"
        ))
        fig.update_layout(
            polar=dict(bgcolor="rgba(0,0,0,0)",
                       radialaxis=dict(visible=True, range=[0, 1], gridcolor="rgba(99,102,241,0.15)")),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155", family="Inter"),
            margin=dict(t=30, b=30, l=50, r=50), height=300, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title" style="margin-top:0;">📈 Performance</div>', unsafe_allow_html=True)
        fig_perf = go.Figure()
        
        t1_val = t1 if isinstance(t1, (int, float)) else 0
        t2_val = t2 if isinstance(t2, (int, float)) else 0
        fig_perf.add_trace(go.Bar(x=["Test 1 (Easy)", "Test 2 (Medium)"], y=[t1_val, t2_val], name="Score", marker_color="#4f46e5"))
        
        df_scores = load_test_scores()
        if df_scores is not None:
            avg_t1 = df_scores["test1_score"].mean()
            avg_t2 = df_scores["test2_score"].mean()
            fig_perf.add_trace(go.Scatter(x=["Test 1 (Easy)", "Test 2 (Medium)"], y=[avg_t1, avg_t2], mode="lines+markers", name="Class Avg", line=dict(color="#f59e0b", width=2)))
        
        layout_perf = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ('xaxis', 'yaxis')}
        fig_perf.update_layout(**layout_perf, yaxis=dict(range=[0, 20], title="Score", gridcolor="rgba(99,102,241,0.15)"), margin=dict(t=20, b=20, l=40, r=20), height=250)
        st.plotly_chart(fig_perf, use_container_width=True)


elif page == "🔗 Student Mapping":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">🔗 Student Identity Mapping</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-bottom:1.5rem;">
        <p style="color:#334155; font-size:0.88rem; margin:0;">
            Map YOLO tracker IDs to real student SAP IDs. Look at the annotated frames
            to identify which tracker ID corresponds to which student, then assign using the dropdowns below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    df_scores = load_test_scores()
    if df_scores is None:
        st.warning("No student roster found.")
        st.stop()

    existing_mapping = load_student_mapping()

    tab_class, tab_test = st.tabs(["📹 Class Video", "📝 Test Video"])

    with tab_class:
        class_frames = get_mapping_frames("class")
        if class_frames:
            best = [f for f in class_frames if "best" in f.name]
            display_frame = best[0] if best else class_frames[-1]
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.image(str(display_frame), caption="Class Video — Tracker IDs", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if len(class_frames) > 1:
                with st.expander("More frames"):
                    for f in class_frames:
                        if f != display_frame:
                            st.image(str(f), caption=f.name, use_container_width=True)
        else:
            st.info("No frames. Run vision pipeline first.")

        df_log = load_engagement_log()
        if df_log is not None:
            tids = sorted(df_log["student_id"].unique())
            st.markdown(f"**Detected IDs:** `{tids}`")

            sap_opts = ["— Not mapped —"] + [f"{r['sap_id']} — {r['student_name']}" for _, r in df_scores.iterrows()]
            class_assignments = {}
            cols_per = 3
            for i in range(0, len(tids), cols_per):
                cols = st.columns(cols_per)
                for j, tid in enumerate(tids[i:i+cols_per]):
                    with cols[j]:
                        default = 0
                        if existing_mapping is not None:
                            m = existing_mapping[existing_mapping["class_tracker_id"] == tid]
                            if not m.empty:
                                sap = m.iloc[0]["sap_id"]
                                for k, o in enumerate(sap_opts):
                                    if str(int(sap)) in str(o):
                                        default = k
                                        break
                        sel = st.selectbox(f"ID {tid}", sap_opts, index=default, key=f"c_{tid}")
                        if sel != "— Not mapped —":
                            class_assignments[tid] = int(sel.split(" — ")[0])
        else:
            class_assignments = {}

    with tab_test:
        for i in range(6):
            frames = get_mapping_frames(f"test_{i}")
            if frames:
                best = [f for f in frames if "best" in f.name]
                df = best[0] if best else frames[-1]
                st.image(str(df), caption=f"Test Video {i+1}", use_container_width=True)

        test_log = load_test_engagement_log()
        if test_log is not None:
            test_tids = sorted(test_log["student_id"].unique())
            st.markdown(f"**Detected IDs:** `{test_tids}`")
            sap_opts_t = ["— Not mapped —"] + [f"{r['sap_id']} — {r['student_name']}" for _, r in df_scores.iterrows()]
            test_assignments = {}
            for i in range(0, len(test_tids), 3):
                cols = st.columns(3)
                for j, tid in enumerate(test_tids[i:i+3]):
                    with cols[j]:
                        default = 0
                        if existing_mapping is not None:
                            m = existing_mapping[existing_mapping["test_tracker_id"] == tid]
                            if not m.empty:
                                sap = m.iloc[0]["sap_id"]
                                for k, o in enumerate(sap_opts_t):
                                    if str(int(sap)) in str(o):
                                        default = k
                                        break
                        sel = st.selectbox(f"ID {tid}", sap_opts_t, index=default, key=f"t_{tid}")
                        if sel != "— Not mapped —":
                            test_assignments[tid] = int(sel.split(" — ")[0])
        else:
            test_assignments = {}

    st.markdown("---")
    if st.button("💾 Save Mapping", type="primary", use_container_width=True):
        rows = []
        for _, r in df_scores.iterrows():
            sid = r["sap_id"]
            ct = next((t for t, s in class_assignments.items() if s == sid), None)
            tt = next((t for t, s in test_assignments.items() if s == sid), None) if 'test_assignments' in dir() else None
            rows.append({"sap_id": sid, "student_name": r["student_name"],
                         "class_tracker_id": ct, "test_tracker_id": tt})
        pd.DataFrame(rows).to_csv(PROFILES_DIR / "student_mapping.csv", index=False)
        n_class = len(class_assignments)
        n_test = len(test_assignments) if 'test_assignments' in dir() else 0
        st.success(f"✅ Saved! {n_class} class + {n_test} test mappings.")
        st.cache_data.clear()
        st.rerun()


elif page == "📝 Generated Content":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">📝 AI-Generated Learning Modules</div>', unsafe_allow_html=True)

    sample_modules = {
        "Struggling": {
            "title": "🔴 Module for Struggling Students",
            "content": """## 🌱 Understanding Photosynthesis — Made Simple!

**Hey there! Let's break this down step by step.**

### 🧪 What Is Photosynthesis?
Think of photosynthesis as a **recipe** that plants follow to make their food.

**Ingredients:** ☀️ Sunlight · 💧 Water · 💨 Carbon dioxide

**What they make:** 🍬 Glucose (food!) · 🌬️ Oxygen (for us!)

### 🏠 Real-World Analogy
Like making a smoothie — the **blender** (sun) provides energy, **fruits** (water + CO₂) are the raw ingredients, and the **smoothie** (glucose) is the finished product!

### 🔑 Key Takeaway
> Plants are tiny factories that use sunlight to turn water and air into food. Without photosynthesis, there would be no oxygen! 🌍
"""
        },
        "Developing": {
            "title": "🟡 Module for Developing Students",
            "content": """## 🌿 Photosynthesis — The Engine of Life

### 📘 The balanced equation:
```
6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂
```

**Two stages:**
1. **Light-Dependent Reactions** — Water is split, ATP and NADPH are generated
2. **Calvin Cycle** — CO₂ is fixed into glucose

### 🌍 Analogy
Like a **solar-powered factory**: solar panels (chlorophyll) capture energy, the assembly line (Calvin Cycle) builds glucose.

### 🔑 Key Takeaway
> Photosynthesis is the foundation of almost all food chains on Earth.
"""
        },
        "Excelling": {
            "title": "🟢 Module for Excelling Students",
            "content": """## 🔬 Photosynthesis — Advanced Deep Dive

### 🧬 Quantum Biology of Photosynthesis
Near-perfect **quantum efficiency** (~95%) through **quantum coherence** in the FMO complex.

### ⚡ Z-Scheme Electron Transport
- **Photosystem II (P680)** — Oxidizes water, evolves O₂
- **Photosystem I (P700)** — Reduces NADP⁺ to NADPH

### 🧩 Challenge
> Explain why C3 photosynthesis fails at high temperatures and how C4 plants solve it through spatial separation.
"""
        }
    }

    for status, mod in sample_modules.items():
        with st.expander(mod["title"], expanded=(status == "Developing")):
            st.markdown(mod["content"])

    st.markdown("---")
    modules = load_generated_modules()
    if modules:
        st.markdown("### 📂 Generated Files")
        sel = st.selectbox("Select module", list(modules.keys()))
        if sel:
            st.markdown(modules[sel])
    else:
        st.info("Sample modules shown above. API-generated files will appear when available.")


elif page == "⚙️ Architecture":
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">⚙️ System Architecture</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="arch-flow">
        <h3 style="color:#a78bfa; margin-top:0; font-size:1rem; letter-spacing:0.5px;">End-to-End Pipeline</h3>
        <p style="color:#94a3b8; font-size:0.88rem; line-height:2;">
            <strong style="color:#f87171;">📹 Class Video</strong> →
            <strong style="color:#fbbf24;">YOLO Detection</strong> →
            <strong style="color:#fbbf24;">Pose + Motion</strong> →
            <strong style="color:#34d399;">Engagement Scores</strong> →
            <strong style="color:#6366f1;">Annotated Video (MP4)</strong><br>
            <strong style="color:#f87171;">📝 Test Videos (×6)</strong> →
            <strong style="color:#fbbf24;">Batch Detection</strong> →
            <strong style="color:#34d399;">Test Engagement</strong><br>
            <strong style="color:#8b5cf6;">📊 Test Scores (Excel)</strong> →
            <strong style="color:#6366f1;">SAP ID Mapping</strong> →
            <strong style="color:#6366f1;">3D Data Fusion</strong><br>
            → <strong style="color:#eab308;">K-Means Clustering</strong> →
            <strong style="color:#8b5cf6;">Gemini LLM</strong> →
            <strong style="color:#f1f5f9;">📄 Personalized Content</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Technology Stack")
    tech = pd.DataFrame({
        "Component": ["Student Detection", "Pose & Gaze", "Motion Analysis", "Engagement Fusion",
                       "Video Annotation", "Identity Mapping", "Test Scores", "Clustering",
                       "Content Generation", "Dashboard"],
        "Technology": ["YOLOv11 (Ultralytics)", "YOLO-Pose Keypoints", "Farneback Optical Flow",
                       "Weighted (0.6G + 0.25P + 0.15M)", "OpenCV VideoWriter (MP4)",
                       "SAP ID Registry", "Pandas + OpenPyXL", "K-Means (k=3, 3D)",
                       "Gemini 2.0 Flash", "Streamlit + Plotly"],
        "Layer": ["Vision", "Vision", "Vision", "Vision", "Vision",
                  "Reasoning", "Reasoning", "Reasoning", "Generation", "Presentation"]
    })
    st.dataframe(tech, use_container_width=True, hide_index=True)

    st.markdown("### 📐 Engagement Formula")
    st.latex(r"\text{E} = 0.6 \cdot \text{Gaze} + 0.25 \cdot \text{Posture} + 0.15 \cdot \text{Motion}")

    st.markdown("### 🎯 Clustering (Phase 2)")
    st.markdown("""
    | Dimension | Source | Description |
    |-----------|--------|-------------|
    | `class_engagement` | Class video | Average engagement during regular class |
    | `test_engagement` | Test videos | Focus level during examinations |
    | `academic_score` | Test scores | Normalized total score (0–1) |

    **Labels:** 🔴 Struggling · 🟡 Developing · 🟢 Excelling
    """)
