"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [mode, setMode] = useState("login"); // "login" | "signup" | "confirmation"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [signupData, setSignupData] = useState(null);
  const canvasRef = useRef(null);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined") {
      const auth = localStorage.getItem("emergence_auth");
      if (auth) {
        try {
          const parsed = JSON.parse(auth);
          // Only redirect if session is fresh (< 24 hours old)
          if (parsed.loginTime && Date.now() - parsed.loginTime < 24 * 60 * 60 * 1000) {
            router.push("/dashboard");
            return;
          }
        } catch {}
        // Expired or invalid — clear it
        localStorage.removeItem("emergence_auth");
      }
    }
  }, [router]);

  // ── Organic flowing animation on the right panel ──
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animId;
    let time = 0;

    const resize = () => {
      canvas.width = canvas.offsetWidth * 2;
      canvas.height = canvas.offsetHeight * 2;
      ctx.scale(2, 2);
    };
    resize();
    window.addEventListener("resize", resize);

    const w = () => canvas.offsetWidth;
    const h = () => canvas.offsetHeight;

    const draw = () => {
      time += 0.003;
      ctx.clearRect(0, 0, w(), h());

      // Warm flowing curves
      for (let i = 0; i < 5; i++) {
        ctx.beginPath();
        const yOff = h() * 0.2 + i * h() * 0.15;
        ctx.moveTo(0, yOff);
        for (let x = 0; x <= w(); x += 4) {
          const y = yOff +
            Math.sin(x * 0.005 + time + i * 0.8) * 40 +
            Math.cos(x * 0.003 + time * 0.7 + i) * 25 +
            Math.sin(x * 0.008 + time * 1.3) * 15;
          ctx.lineTo(x, y);
        }
        ctx.lineTo(w(), h());
        ctx.lineTo(0, h());
        ctx.closePath();

        const alpha = 0.03 + i * 0.012;
        const colors = [
          `rgba(79, 99, 75, ${alpha})`,
          `rgba(124, 128, 101, ${alpha})`,
          `rgba(176, 138, 84, ${alpha})`,
          `rgba(61, 66, 51, ${alpha})`,
          `rgba(140, 83, 77, ${alpha})`,
        ];
        ctx.fillStyle = colors[i];
        ctx.fill();
      }

      // Floating circles
      for (let i = 0; i < 8; i++) {
        const x = w() * 0.15 + Math.sin(time * 0.5 + i * 1.2) * w() * 0.35;
        const y = h() * 0.3 + Math.cos(time * 0.4 + i * 0.9) * h() * 0.3;
        const r = 60 + Math.sin(time + i) * 30;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(79, 99, 75, ${0.02 + Math.sin(time + i) * 0.01})`;
        ctx.fill();
      }

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, [mounted]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    await new Promise((r) => setTimeout(r, 1200));

    const validCredentials = [
      { email: "teacher@emergence.edu", password: "emergence2026" },
      { email: "mohit@emergence.edu", password: "emergence2026" },
      { email: "admin@emergence.edu", password: "admin123" },
    ];

    // Also check localStorage for signed-up users
    const storedUsers = JSON.parse(localStorage.getItem("emergence_users") || "[]");
    const allCreds = [...validCredentials, ...storedUsers];

    const match = allCreds.find(
      (c) => c.email === email.toLowerCase().trim() && c.password === password
    );

    if (match) {
      localStorage.setItem(
        "emergence_auth",
        JSON.stringify({
          email: match.email,
          name: match.name || match.email.split("@")[0].charAt(0).toUpperCase() + match.email.split("@")[0].slice(1),
          loginTime: Date.now(),
        })
      );
      router.push("/dashboard");
    } else {
      setError("Invalid credentials. Please check your Faculty ID and password.");
      setIsLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    if (!name.trim() || !email.trim() || !password.trim() || !department.trim()) {
      setError("All fields are required.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setIsLoading(true);
    await new Promise((r) => setTimeout(r, 1500));

    // Store in localStorage
    const storedUsers = JSON.parse(localStorage.getItem("emergence_users") || "[]");
    const exists = storedUsers.find((u) => u.email === email.toLowerCase().trim());
    if (exists) {
      setError("This email is already registered. Please sign in.");
      setIsLoading(false);
      return;
    }

    const newUser = {
      email: email.toLowerCase().trim(),
      password,
      name: name.trim(),
      department: department.trim(),
      createdAt: new Date().toISOString(),
    };
    storedUsers.push(newUser);
    localStorage.setItem("emergence_users", JSON.stringify(storedUsers));

    setSignupData(newUser);
    setIsLoading(false);
    setMode("confirmation");
  };

  if (!mounted) return null;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Space+Mono:wght@400;700&display=swap');

        .login-root {
          min-height: 100vh;
          display: flex;
          background: #f5f2eb;
          font-family: 'Space Mono', monospace;
          color: #2e3328;
        }

        /* ── Left Panel ── */
        .login-left {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 3rem 4rem;
          max-width: 560px;
          min-width: 440px;
          position: relative;
        }

        /* ── Right Panel (Animation) ── */
        .login-right {
          flex: 1.4;
          position: relative;
          overflow: hidden;
          background: #eae7df;
        }

        .login-right canvas {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
        }

        .login-right-overlay {
          position: absolute;
          inset: 0;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          z-index: 2;
          pointer-events: none;
        }

        .login-right-brand {
          font-family: 'Playfair Display', serif;
          font-size: 4.5rem;
          font-weight: 700;
          font-style: italic;
          color: rgba(46, 51, 40, 0.08);
          letter-spacing: 4px;
          user-select: none;
        }

        .login-right-tagline {
          font-size: 0.7rem;
          color: rgba(46, 51, 40, 0.2);
          letter-spacing: 3px;
          text-transform: uppercase;
          margin-top: 0.5rem;
        }

        /* ── Logo ── */
        .login-logo {
          display: flex;
          align-items: center;
          gap: 0.6rem;
          margin-bottom: 3rem;
        }

        .login-logo-text {
          font-family: 'Playfair Display', serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: #2e3328;
          letter-spacing: 2px;
        }

        /* ── Tab Switcher ── */
        .login-tabs {
          display: flex;
          gap: 0;
          margin-bottom: 2.5rem;
          border: 1px solid rgba(0,0,0,0.08);
          border-radius: 6px;
          overflow: hidden;
          background: rgba(0,0,0,0.02);
        }

        .login-tab {
          flex: 1;
          padding: 0.7rem 1rem;
          border: none;
          background: transparent;
          font-family: 'Space Mono', monospace;
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 1px;
          text-transform: uppercase;
          color: #6e7361;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .login-tab.active {
          background: #2e3328;
          color: #fdfbf7;
        }

        /* ── Form Title ── */
        .login-form-title {
          font-family: 'Playfair Display', serif;
          font-size: 2rem;
          font-weight: 600;
          font-style: italic;
          color: #2e3328;
          margin-bottom: 0.35rem;
        }

        .login-form-subtitle {
          color: #6e7361;
          font-size: 0.78rem;
          line-height: 1.6;
          margin-bottom: 2rem;
        }

        /* ── Inputs ── */
        .login-field {
          margin-bottom: 1.25rem;
        }

        .login-field-label {
          display: block;
          font-size: 0.65rem;
          font-weight: 700;
          color: #6e7361;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          margin-bottom: 0.4rem;
        }

        .login-field-input {
          width: 100%;
          padding: 0.85rem 1rem;
          background: rgba(253, 251, 247, 0.9);
          border: 1px solid rgba(0,0,0,0.08);
          border-radius: 6px;
          color: #2e3328;
          font-family: 'Space Mono', monospace;
          font-size: 0.85rem;
          outline: none;
          transition: all 0.2s ease;
        }

        .login-field-input::placeholder {
          color: #b0ab9e;
        }

        .login-field-input:focus {
          border-color: rgba(46,51,40,0.3);
          box-shadow: 0 0 0 3px rgba(46,51,40,0.04);
        }

        /* ── Button ── */
        .login-btn {
          width: 100%;
          margin-top: 0.5rem;
          padding: 0.9rem;
          border: 1px solid #2e3328;
          border-radius: 4px;
          background: #2e3328;
          color: #fdfbf7;
          font-family: 'Space Mono', monospace;
          font-size: 0.8rem;
          font-weight: 700;
          letter-spacing: 1px;
          text-transform: uppercase;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          transition: all 0.2s ease;
        }

        .login-btn:hover {
          background: #fdfbf7;
          color: #2e3328;
        }

        .login-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* ── Error ── */
        .login-error {
          padding: 0.7rem 1rem;
          background: rgba(140,83,77,0.06);
          border: 1px solid rgba(140,83,77,0.12);
          border-radius: 6px;
          color: #8c534d;
          font-size: 0.78rem;
          margin-bottom: 1rem;
        }

        /* ── Demo Credentials ── */
        .login-demo {
          margin-top: 2rem;
          padding-top: 1.5rem;
          border-top: 1px solid rgba(0,0,0,0.05);
        }

        .login-demo-label {
          font-size: 0.6rem;
          text-transform: uppercase;
          letter-spacing: 2px;
          color: #6e7361;
          font-weight: 700;
          margin-bottom: 0.4rem;
        }

        .login-demo-code {
          font-size: 0.78rem;
          color: #545c47;
        }

        /* ── Footer ── */
        .login-left-footer {
          position: absolute;
          bottom: 2rem;
          left: 4rem;
          right: 4rem;
          font-size: 0.65rem;
          color: #b0ab9e;
          letter-spacing: 0.3px;
        }

        /* ── Confirmation ── */
        .confirm-card {
          text-align: center;
        }

        .confirm-icon {
          width: 64px;
          height: 64px;
          border-radius: 50%;
          background: rgba(79,99,75,0.08);
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 1.5rem;
        }

        .confirm-title {
          font-family: 'Playfair Display', serif;
          font-size: 1.6rem;
          font-weight: 600;
          font-style: italic;
          color: #2e3328;
          margin-bottom: 0.5rem;
        }

        .confirm-subtitle {
          color: #6e7361;
          font-size: 0.8rem;
          line-height: 1.6;
          margin-bottom: 2rem;
        }

        .confirm-email-preview {
          background: rgba(253,251,247,0.9);
          border: 1px solid rgba(0,0,0,0.06);
          border-radius: 10px;
          padding: 1.5rem;
          text-align: left;
          margin-bottom: 2rem;
        }

        .confirm-email-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid rgba(0,0,0,0.05);
          margin-bottom: 1rem;
        }

        .confirm-email-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #4f634b;
        }

        .confirm-email-from {
          font-size: 0.7rem;
          color: #6e7361;
          letter-spacing: 0.5px;
        }

        .confirm-email-body h3 {
          font-family: 'Playfair Display', serif;
          font-size: 1.1rem;
          font-style: italic;
          color: #2e3328;
          margin-bottom: 0.75rem;
        }

        .confirm-email-body p {
          font-size: 0.78rem;
          color: #6e7361;
          line-height: 1.7;
          margin-bottom: 0.75rem;
        }

        .confirm-email-body .cred-box {
          background: rgba(46,51,40,0.04);
          border: 1px solid rgba(0,0,0,0.05);
          border-radius: 4px;
          padding: 0.6rem 0.85rem;
          margin: 0.75rem 0;
          font-size: 0.78rem;
        }

        .confirm-email-body .cred-box strong {
          color: #2e3328;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .login-spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(253,251,247,0.3);
          border-top-color: #fdfbf7;
          border-radius: 50%;
          animation: spin 0.7s linear infinite;
          display: inline-block;
        }

        .login-btn:hover .login-spinner {
          border-color: rgba(46,51,40,0.3);
          border-top-color: #2e3328;
        }
      `}</style>

      <div className="login-root">
        {/* ── Left Panel: Form ── */}
        <div className="login-left">
          {/* Logo */}
          <div className="login-logo">
            <svg width="28" height="28" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="22" stroke="#2e3328" strokeWidth="1.5" />
              <circle cx="24" cy="24" r="13" stroke="#2e3328" strokeWidth="1" opacity="0.4" />
              <circle cx="24" cy="24" r="5" fill="#2e3328" />
            </svg>
            <span className="login-logo-text">EMERGENCE</span>
          </div>

          {mode !== "confirmation" ? (
            <>
              {/* Tab Switcher */}
              <div className="login-tabs">
                <button
                  className={`login-tab ${mode === "login" ? "active" : ""}`}
                  onClick={() => { setMode("login"); setError(""); }}
                >
                  Sign In
                </button>
                <button
                  className={`login-tab ${mode === "signup" ? "active" : ""}`}
                  onClick={() => { setMode("signup"); setError(""); }}
                >
                  Sign Up
                </button>
              </div>

              {mode === "login" ? (
                <>
                  <h1 className="login-form-title">Welcome Back</h1>
                  <p className="login-form-subtitle">
                    Sign in with your Faculty ID to access the classroom intelligence dashboard
                  </p>

                  <form onSubmit={handleLogin}>
                    {error && <div className="login-error">{error}</div>}

                    <div className="login-field">
                      <label className="login-field-label">Faculty Email</label>
                      <input
                        className="login-field-input"
                        type="email"
                        placeholder="teacher@emergence.edu"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        autoComplete="email"
                      />
                    </div>

                    <div className="login-field">
                      <label className="login-field-label">Password</label>
                      <input
                        className="login-field-input"
                        type="password"
                        placeholder="••••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        autoComplete="current-password"
                      />
                    </div>

                    <button className="login-btn" type="submit" disabled={isLoading}>
                      {isLoading ? <span className="login-spinner" /> : null}
                      {isLoading ? "Authenticating..." : "Sign In →"}
                    </button>
                  </form>

                  <div className="login-demo">
                    <p className="login-demo-label">Demo Credentials</p>
                    <code className="login-demo-code">teacher@emergence.edu / emergence2026</code>
                  </div>
                </>
              ) : (
                <>
                  <h1 className="login-form-title">Create Faculty Account</h1>
                  <p className="login-form-subtitle">
                    Register your Faculty ID to access EMERGENCE. A confirmation will be sent to your email.
                  </p>

                  <form onSubmit={handleSignup}>
                    {error && <div className="login-error">{error}</div>}

                    <div className="login-field">
                      <label className="login-field-label">Full Name</label>
                      <input
                        className="login-field-input"
                        type="text"
                        placeholder="Dr. Jane Smith"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                      />
                    </div>

                    <div className="login-field">
                      <label className="login-field-label">Faculty Email</label>
                      <input
                        className="login-field-input"
                        type="email"
                        placeholder="jane.smith@emergence.edu"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>

                    <div className="login-field">
                      <label className="login-field-label">Department</label>
                      <input
                        className="login-field-input"
                        type="text"
                        placeholder="Computer Science & Engineering"
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        required
                      />
                    </div>

                    <div className="login-field">
                      <label className="login-field-label">Password</label>
                      <input
                        className="login-field-input"
                        type="password"
                        placeholder="Min 6 characters"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={6}
                      />
                    </div>

                    <button className="login-btn" type="submit" disabled={isLoading}>
                      {isLoading ? <span className="login-spinner" /> : null}
                      {isLoading ? "Creating Account..." : "Create Account →"}
                    </button>
                  </form>
                </>
              )}
            </>
          ) : (
            /* ── Confirmation View ── */
            <div className="confirm-card">
              <div className="confirm-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#4f634b" strokeWidth="2" strokeLinecap="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </div>
              <h2 className="confirm-title">Account Created</h2>
              <p className="confirm-subtitle">
                A confirmation has been sent to <strong>{signupData?.email}</strong>
              </p>

              {/* Simulated Email Preview */}
              <div className="confirm-email-preview">
                <div className="confirm-email-header">
                  <div className="confirm-email-dot" />
                  <span className="confirm-email-from">From: noreply@emergence.edu</span>
                </div>
                <div className="confirm-email-body">
                  <h3>Welcome to EMERGENCE, {signupData?.name}</h3>
                  <p>
                    Your Faculty account has been successfully created on the <strong>EMERGENCE Adaptive Classroom Intelligence System</strong> — an AI-powered platform that combines computer vision behavioral analytics with academic performance data to deliver personalized, data-driven teaching insights.
                  </p>
                  <p>
                    EMERGENCE uses real-time student engagement tracking via YOLO-based posture and gaze detection, fused with academic scores through our proprietary clustering engine, to generate adaptive curriculum modules tailored to each student cohort.
                  </p>
                  <div className="cred-box">
                    <div><strong>Login Email:</strong> {signupData?.email}</div>
                    <div><strong>Department:</strong> {signupData?.department}</div>
                    <div style={{ marginTop: "0.4rem", fontSize: "0.7rem", color: "#b0ab9e" }}>
                      Use the password you set during registration to sign in.
                    </div>
                  </div>
                  <p style={{ fontSize: "0.7rem", color: "#b0ab9e", marginTop: "0.5rem" }}>
                    — The EMERGENCE Team · Engineered by Mohit Yadav
                  </p>
                </div>
              </div>

              <button
                className="login-btn"
                onClick={() => {
                  setMode("login");
                  setEmail(signupData?.email || "");
                  setPassword("");
                  setError("");
                }}
              >
                Continue to Sign In →
              </button>
            </div>
          )}

          <div className="login-left-footer">
            Engineered by <strong style={{ color: "#6e7361" }}>Mohit Yadav</strong> · EMERGENCE © 2026
          </div>
        </div>

        {/* ── Right Panel: Animation ── */}
        <div className="login-right">
          <canvas ref={canvasRef} />
          <div className="login-right-overlay">
            <div className="login-right-brand">EMERGENCE</div>
            <div className="login-right-tagline">Adaptive Classroom Intelligence</div>
          </div>
        </div>
      </div>
    </>
  );
}
