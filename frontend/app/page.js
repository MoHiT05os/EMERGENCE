"use client";

import React, { useEffect, useRef } from "react";
import Link from "next/link";
import { ArrowRight, BrainCircuit, Eye, LineChart, Sparkles } from "lucide-react";

export default function LandingPage() {
  const canvasRef = useRef(null);

  // Background flowing animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;
    let time = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resize();
    window.addEventListener("resize", resize);

    const w = () => canvas.offsetWidth;
    const h = () => canvas.offsetHeight;

    const draw = () => {
      time += 0.002;
      ctx.clearRect(0, 0, w(), h());

      for (let i = 0; i < 3; i++) {
        ctx.beginPath();
        const yOff = h() * 0.4 + i * h() * 0.2;
        ctx.moveTo(0, yOff);
        for (let x = 0; x <= w(); x += 10) {
          const y = yOff +
            Math.sin(x * 0.003 + time + i * 0.5) * 50 +
            Math.cos(x * 0.002 + time * 0.8 + i) * 30;
          ctx.lineTo(x, y);
        }
        ctx.lineTo(w(), h());
        ctx.lineTo(0, h());
        ctx.closePath();

        const alpha = 0.02 + i * 0.01;
        ctx.fillStyle = `rgba(139, 92, 246, ${alpha})`;
        ctx.fill();
      }

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#f5f2eb", fontFamily: "'Space Mono', monospace", color: "#2e3328", position: "relative", overflowX: "hidden" }}>
      
      {/* Background Canvas */}
      <canvas ref={canvasRef} style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 0 }} />

      {/* Navigation */}
      <nav style={{ position: "relative", zIndex: 10, padding: "2rem 4rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.5rem", fontWeight: 700, fontStyle: "italic", letterSpacing: "-0.5px", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Sparkles style={{ width: 20, height: 20, color: "#7c3aed" }} /> EMERGENCE
        </div>
        <Link href="/login" style={{ textDecoration: "none", background: "#2e3328", color: "#f5f2eb", padding: "0.8rem 2rem", borderRadius: "4px", fontSize: "0.85rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", display: "flex", alignItems: "center", gap: "0.5rem", transition: "all 0.3s ease" }}>
          Faculty Login <ArrowRight style={{ width: 16, height: 16 }} />
        </Link>
      </nav>

      {/* Hero Section */}
      <main style={{ position: "relative", zIndex: 10, padding: "6rem 4rem 4rem", maxWidth: "1200px", margin: "0 auto" }}>
        <div style={{ maxWidth: "800px" }}>
          <div style={{ display: "inline-block", padding: "0.4rem 1rem", background: "rgba(124, 58, 237, 0.1)", color: "#7c3aed", borderRadius: "50px", fontSize: "0.75rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", marginBottom: "2rem" }}>
            The New Era of Teaching
          </div>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "5.5rem", fontWeight: 700, lineHeight: 1.1, letterSpacing: "-2px", color: "#2e3328", marginBottom: "2rem" }}>
            Classrooms,<br />
            <span style={{ fontStyle: "italic", color: "rgba(46,51,40,0.4)" }}>now conscious.</span>
          </h1>
          <p style={{ fontSize: "1.1rem", lineHeight: 1.8, color: "#6e7361", maxWidth: "600px", marginBottom: "3rem" }}>
            EMERGENCE is a state-of-the-art multimodal AI system that fuses computer vision and academic records into predictive pedagogical outcomes. We engineer evolutionary pressure for education.
          </p>
          <div style={{ display: "flex", gap: "1.5rem" }}>
            <Link href="/login" style={{ textDecoration: "none", background: "#7c3aed", color: "white", padding: "1.2rem 2.5rem", borderRadius: "4px", fontSize: "0.9rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", transition: "all 0.3s ease", boxShadow: "0 10px 30px rgba(124,58,237,0.3)" }}>
              Enter the Arena
            </Link>
            <a href="#features" style={{ textDecoration: "none", background: "transparent", border: "1px solid rgba(46,51,40,0.2)", color: "#2e3328", padding: "1.2rem 2.5rem", borderRadius: "4px", fontSize: "0.9rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase", transition: "all 0.3s ease" }}>
              Explore Technology
            </a>
          </div>
        </div>

        {/* Feature Grid */}
        <div id="features" style={{ marginTop: "10rem", display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "2rem" }}>
          
          <div style={{ background: "rgba(255,255,255,0.5)", border: "1px solid rgba(46,51,40,0.05)", padding: "3rem", borderRadius: "8px", transition: "transform 0.3s ease" }}>
            <Eye style={{ width: 32, height: 32, color: "#0284c7", marginBottom: "1.5rem" }} />
            <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.8rem", fontWeight: 600, marginBottom: "1rem" }}>Spatial Reasoning</h3>
            <p style={{ color: "#6e7361", fontSize: "0.9rem", lineHeight: 1.7 }}>
              Our YOLO-powered OSNet Re-ID pipeline continuously maps student gaze, posture, and attention metrics in real-time, extracting deep behavioral signals without human intervention.
            </p>
          </div>

          <div style={{ background: "rgba(255,255,255,0.5)", border: "1px solid rgba(46,51,40,0.05)", padding: "3rem", borderRadius: "8px", transition: "transform 0.3s ease", transform: "translateY(-1rem)" }}>
            <LineChart style={{ width: 32, height: 32, color: "#f59e0b", marginBottom: "1.5rem" }} />
            <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.8rem", fontWeight: 600, marginBottom: "1rem" }}>Data Fusion</h3>
            <p style={{ color: "#6e7361", fontSize: "0.9rem", lineHeight: 1.7 }}>
              Vision metrics are intelligently bridged with traditional academic scoring matrices. Our clustering engine dynamically segments students into Excelling, Developing, and Struggling cohorts.
            </p>
          </div>

          <div style={{ background: "rgba(255,255,255,0.5)", border: "1px solid rgba(46,51,40,0.05)", padding: "3rem", borderRadius: "8px", transition: "transform 0.3s ease" }}>
            <BrainCircuit style={{ width: 32, height: 32, color: "#10b981", marginBottom: "1.5rem" }} />
            <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: "1.8rem", fontWeight: 600, marginBottom: "1rem" }}>Generative Feedback</h3>
            <p style={{ color: "#6e7361", fontSize: "0.9rem", lineHeight: 1.7 }}>
              Powered by DeepSeek V3 and MiniMax M2.5, EMERGENCE autonomously generates hyper-personalized, cluster-specific pedagogical modules for immediate classroom intervention.
            </p>
          </div>

        </div>

        {/* Visual Showcase (Mockups) */}
        <div style={{ marginTop: "10rem", marginBottom: "8rem", position: "relative" }}>
          <div style={{ textAlign: "center", marginBottom: "6rem" }}>
            <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: "3.5rem", fontWeight: 700, fontStyle: "italic", letterSpacing: "-1px" }}>See it in action.</h2>
          </div>
          
          {/* Block 1: Vision Mapping */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center", marginBottom: "8rem" }}>
            <div style={{ borderRadius: "12px", overflow: "hidden", border: "1px solid rgba(0,0,0,0.1)", boxShadow: "0 20px 40px rgba(0,0,0,0.08)", transform: "rotate(-2deg)" }}>
              <div style={{ background: "#2e3328", padding: "10px 15px", display: "flex", gap: "6px" }}>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#ef4444"}}></div>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#f59e0b"}}></div>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#10b981"}}></div>
              </div>
              <img src="/landing-vision.jpg" alt="Vision Mapping" style={{ width: "100%", height: "auto", display: "block", objectFit: "cover", objectPosition: "center" }} />
            </div>
            
            <div>
              <h3 style={{ fontSize: "1.8rem", fontWeight: 700, marginBottom: "1rem" }}>State-of-the-Art Vision Mapping</h3>
              <p style={{ color: "#6e7361", lineHeight: 1.8, marginBottom: "2rem" }}>
                EMERGENCE utilizes advanced OSNet Re-ID and YOLO models to continuously map student behavior and engagement in every classroom without human intervention. We map the invisible topography of human attention.
              </p>
              <Link href="/login" style={{ color: "#7c3aed", textDecoration: "none", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                Explore the technology <ArrowRight style={{ width: 16, height: 16 }} />
              </Link>
            </div>
          </div>

          {/* Block 2: Dashboard Profiling */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4rem", alignItems: "center" }}>
            <div style={{ order: 2, borderRadius: "12px", overflow: "hidden", border: "1px solid rgba(0,0,0,0.1)", boxShadow: "0 20px 40px rgba(0,0,0,0.08)", transform: "rotate(2deg)" }}>
              <div style={{ background: "#2e3328", padding: "10px 15px", display: "flex", gap: "6px" }}>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#ef4444"}}></div>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#f59e0b"}}></div>
                <div style={{width:10, height:10, borderRadius:"50%", background:"#10b981"}}></div>
              </div>
              <img src="/landing-dashboard.jpg" alt="Dashboard Profiling" style={{ width: "100%", height: "auto", display: "block", objectFit: "cover", objectPosition: "center" }} />
            </div>
            
            <div style={{ order: 1 }}>
              <h3 style={{ fontSize: "1.8rem", fontWeight: 700, marginBottom: "1rem" }}>Automated Profiling & Leaderboards</h3>
              <p style={{ color: "#6e7361", lineHeight: 1.8, marginBottom: "2rem" }}>
                Experience a premium, dynamic dashboard that calculates individual student profiling and generates classroom leaderboards on a daily basis. Our engine understands exactly who is engaged and who is lost before a test is ever graded.
              </p>
              <Link href="/login" style={{ color: "#7c3aed", textDecoration: "none", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                Enter the dashboard <ArrowRight style={{ width: 16, height: 16 }} />
              </Link>
            </div>
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid rgba(46,51,40,0.1)", padding: "4rem", textAlign: "center" }}>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: "2rem", fontWeight: 700, fontStyle: "italic", opacity: 0.2, marginBottom: "1rem" }}>EMERGENCE</h2>
        <p style={{ color: "#6e7361", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "1px" }}>Architected by Mohit Yadav © 2026</p>
      </footer>

    </div>
  );
}
