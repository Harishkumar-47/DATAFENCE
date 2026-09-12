import { useState, useEffect } from "react";
import {
  Shield,
  LogOut,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  Globe,
  Database,
  Search,
  Brain,
  Lock,
  UserCircle,
} from "lucide-react";
import { runFullSecurityAnalysis } from "../services/api";
import "../hacker.css";

function RiskCard({ icon, title, value, subtitle }) {
  const percentage = typeof value === 'number' ? value : (parseInt(value) || 0);
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  
  return (
    <div className="osint-card" style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '15px' }}>
      <div style={{ position: 'relative', width: '60px', height: '60px' }}>
        <svg width="60" height="60" viewBox="0 0 60 60">
          <circle cx="30" cy="30" r={radius} fill="none" stroke="#1e293b" strokeWidth="6" />
          <circle cx="30" cy="30" r={radius} fill="none" stroke={percentage > 50 ? "#ef4444" : "#38bdf8"} strokeWidth="6" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" transform="rotate(-90 30 30)" style={{ transition: 'stroke-dashoffset 1s ease-in-out' }} />
        </svg>
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: percentage > 50 ? "#ef4444" : "#38bdf8" }}>
          {icon}
        </div>
      </div>
      <div>
        <h4 style={{ color: '#e2e8f0', margin: '0 0 5px', fontSize: '13px', textTransform: 'uppercase' }}>{title}</h4>
        <strong style={{ color: percentage > 50 ? '#ef4444' : '#38bdf8', fontSize: '20px', display: 'block' }}>{value}</strong>
        <span style={{ color: '#64748b', fontSize: '11px' }}>{subtitle}</span>
      </div>
    </div>
  );
}

export default function Dashboard({ onLogout }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState(null);

  const user = JSON.parse(localStorage.getItem("datafence_user") || '{"name": "User", "email": ""}');
  const targetEmail = localStorage.getItem("datafence_target_email") || "";
  const targetPhone = localStorage.getItem("datafence_target_phone") || "";

  useEffect(() => {
    let mounted = true;

    const analyzeData = async () => {
      try {
        const data = await runFullSecurityAnalysis(targetEmail, targetPhone);
        if (mounted) setAnalysis(data);
      } catch (err) {
        if (mounted) setError(err.message || "Failed to run analysis.");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    analyzeData();
    
    return () => {
      mounted = false;
    };
  }, [targetEmail, targetPhone]);

  const [showRemediation, setShowRemediation] = useState(false);
  const [resolvingStep, setResolvingStep] = useState(null);
  const [resolvedSteps, setResolvedSteps] = useState({});

  const handleProtect = (stepIndex) => {
    setResolvingStep(stepIndex);
    setTimeout(() => {
      setResolvedSteps(prev => ({ ...prev, [stepIndex]: true }));
      setResolvingStep(null);
    }, 2000);
  };
  
  const security = analysis?.security || { security_score: 0, risk_level: "UNKNOWN", risk_score: 0 };
  const intelligence = analysis?.intelligence || {
    exposure: { score: 0, total_items: 0 },
    inference: { score: 0, findings: [] },
    threat: { score: 0, level: "UNKNOWN" },
    blast_radius: { score: 0, connected_services: 0 },
  };
  const remediation_plan = analysis?.remediation_plan || [];

  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <Shield size={28} className="brand-mark" />
          <div>
            <h1>DATAFENCE</h1>
            <span>Personal Data Security</span>
          </div>
        </div>

        <div className="topbar-right">
          <div className="user-profile">
            <div className="user-avatar">
              <UserCircle size={20} />
            </div>
            <div className="profile-summary">
              <strong>{user.name}</strong>
              <span>{user.email}</span>
            </div>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            SYSTEM ONLINE
          </div>

          <button className="logout-button" onClick={onLogout}>
            <LogOut size={18} />
            LOGOUT
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <section className="hero">
          <div className="hero-content">
            <p className="eyebrow">PERSONAL DATA INTELLIGENCE</p>
            <h2>
              Understand what your <span>data reveals.</span>
            </h2>
            <p className="hero-text">
              DATAFENCE has analyzed the digital footprint, exposure, and security risks for this data.
            </p>

            <div className="identity-badge">
              <div className="identity-avatar">{targetEmail ? targetEmail.charAt(0).toUpperCase() : (targetPhone ? targetPhone.charAt(0) : 'U')}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <span style={{ fontSize: "10px", color: "var(--color-primary)", letterSpacing: "1px", fontWeight: "600" }}>TARGET ACQUIRED</span>
                <strong style={{ color: "#fff", fontSize: "15px" }}>{targetEmail || targetPhone}</strong>
                {targetEmail && targetPhone && <span style={{ color: "var(--color-muted)", fontSize: "12px" }}>{targetPhone}</span>}
              </div>
            </div>
            
            <button 
              className="action-button secondary" 
              onClick={() => {
                localStorage.removeItem("datafence_target_email");
                localStorage.removeItem("datafence_target_phone");
                onLogout();
              }}
              style={{ marginTop: "20px" }}
            >
              Analyze Another Target
            </button>
          </div>
        </section>

        {error && (
          <div className="dashboard-error">
            <AlertTriangle size={16} />
            <span>{error}</span>
            <button onClick={() => setError("")}>×</button>
          </div>
        )}

        {loading && !analysis ? (
          <div className="loading-screen" style={{ minHeight: "300px", background: "transparent" }}>
            <div className="loading-spinner"></div>
            <p style={{ marginTop: "20px" }}>ANALYZING DATA SOURCES...</p>
          </div>
        ) : analysis ? (
          <div className="hacker-dashboard">
            
            <div className="osint-grid" style={{ marginBottom: "40px" }}>
              <RiskCard icon={<AlertTriangle size={18} />} title="Data Exposure" value={intelligence.exposure.score} subtitle={`${intelligence.exposure.total_items} points found`} />
              <RiskCard icon={<Brain size={18} />} title="Inference Risk" value={intelligence.inference.score} subtitle={`${intelligence.inference.findings.length} profiles inferred`} />
              <RiskCard icon={<Activity size={18} />} title="Threat Level" value={intelligence.threat.score} subtitle={intelligence.threat.level} />
              <RiskCard icon={<Lock size={18} />} title="Blast Radius" value={intelligence.blast_radius.score} subtitle={`${intelligence.blast_radius.connected_services} connected nodes`} />
            </div>

            <h2 className="hacker-title glitch-text">
              <Activity size={24} /> REAL-TIME OSINT TRACE
            </h2>

            <div className="osint-grid">
              {/* EMAIL BREACH TRACE */}
              {targetEmail && (
                <div className={`osint-card ${analysis?.breach_analysis?.breaches > 0 ? 'danger' : ''}`}>
                  <div className="osint-card-title">
                    <span><Globe size={14} style={{ marginRight: '5px' }} /> Email Intelligence (XposedOrNot Engine)</span>
                    <span>{analysis?.breach_analysis?.breaches || 0} BREACHES</span>
                  </div>
                  
                  {analysis?.breach_analysis?.breaches > 0 ? (
                    <div>
                      <div className="terminal-line">
                        <span className="terminal-label">TARGET:</span>
                        <span className="terminal-value" style={{ color: "#ff003c" }}>{targetEmail}</span>
                      </div>
                      <div className="terminal-line" style={{ marginBottom: "15px" }}>
                        <span className="terminal-label">STATUS:</span>
                        <span className="terminal-value" style={{ color: "#ff003c" }}>COMPROMISED</span>
                      </div>
                      <span className="terminal-label" style={{ display: 'block', marginBottom: '10px' }}>BREACH ORIGINS:</span>
                      <ul className="breach-list">
                        {analysis.breach_analysis.breach_sites?.map((site, idx) => (
                          <li key={idx}>{site}</li>
                        )) || <li>Unknown Datasets</li>}
                      </ul>
                    </div>
                  ) : (
                    <div>
                      <div className="terminal-line">
                        <span className="terminal-label">TARGET:</span>
                        <span className="terminal-value">{targetEmail}</span>
                      </div>
                      <div className="terminal-line">
                        <span className="terminal-label">STATUS:</span>
                        <span className="terminal-value">SECURE</span>
                      </div>
                      <p style={{ color: '#888', marginTop: '15px', fontSize: '12px' }}>No active breaches detected in public datasets.</p>
                    </div>
                  )}
                </div>
              )}

              {/* PHONE NUMBER TRACE */}
              {targetPhone && (
                <div className={`osint-card ${intelligence.inference.findings.length > 0 ? 'danger' : ''}`}>
                  <div className="osint-card-title">
                    <span><Database size={14} style={{ marginRight: '5px' }} /> Telecom Intelligence (Sanchar Saathi Trace)</span>
                    <span>ACTIVE</span>
                  </div>
                  
                  <div className="terminal-line">
                    <span className="terminal-label">TARGET:</span>
                    <span className="terminal-value">{targetPhone}</span>
                  </div>

                  {intelligence.inference.findings.map((finding, idx) => {
                    if (finding.source_categories.includes("Phone Number")) {
                      return (
                        <div key={idx} style={{ marginTop: "15px", borderTop: "1px dashed #00ff00", paddingTop: "15px" }}>
                          <span className="terminal-label" style={{ display: 'block', marginBottom: '10px' }}>NETWORK TRACE FOUND:</span>
                          <p style={{ color: "#ff003c", fontSize: "14px", lineHeight: "1.5" }}>{finding.inference}</p>
                          <div className="terminal-line" style={{ marginTop: "10px" }}>
                            <span className="terminal-label">LINKED SIM CARDS:</span>
                            <span className="terminal-value">1 (Simulated)</span>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  })}
                  
                  {!intelligence.inference.findings.some(f => f.source_categories.includes("Phone Number")) && (
                    <div style={{ marginTop: "15px" }}>
                      <p style={{ color: '#888', fontSize: '12px' }}>Trace active. Awaiting carrier ping.</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div style={{ textAlign: "center", margin: "40px 0 20px" }}>
              <button 
                className="action-button primary" 
                onClick={() => setShowRemediation(true)}
                style={{ background: "#ff003c", color: "#fff", boxShadow: "0 0 20px rgba(255,0,60,0.4)" }}
              >
                <Shield size={20} />
                INITIATE PROTECTION SEQUENCE
              </button>
            </div>

            {showRemediation && (
              <section className="remediation-section osint-card danger" style={{ marginTop: "20px" }}>
                <div className="osint-card-title">
                  <span><Shield size={16} style={{ marginRight: '5px' }} /> EMERGENCY ACTION PLAN</span>
                  <span className="glitch-text">REQUIRED</span>
                </div>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "15px", marginTop: "15px" }}>
                  {remediation_plan.map((step, idx) => (
                    <div key={idx} style={{ padding: "20px", background: "rgba(15, 23, 42, 0.8)", borderRadius: "6px", borderLeft: `4px solid ${step.critical ? '#ef4444' : '#38bdf8'}` }}>
                      <h4 style={{ color: step.critical ? "#fca5a5" : "#e0f2fe", marginBottom: "10px", fontSize: "15px", textTransform: "uppercase" }}>
                        {step.title}
                      </h4>
                      <p style={{ color: "#94a3b8", fontSize: "13px", lineHeight: "1.6" }}>{step.description}</p>
                      
                      {/* Internal Simulated Buttons */}
                      <button 
                        onClick={() => handleProtect(idx)}
                        disabled={resolvingStep === idx || resolvedSteps[idx]}
                        className={`internal-protect-btn ${resolvingStep === idx ? 'resolving' : ''} ${resolvedSteps[idx] ? 'resolved' : ''}`}
                      >
                        {resolvedSteps[idx] ? (
                          <><CheckCircle size={14} /> Protection Active</>
                        ) : resolvingStep === idx ? (
                          <><Activity size={14} className="glitch-text" /> Establishing Secure Connection...</>
                        ) : step.title.includes("Passwords") ? (
                          <><Lock size={14} /> Automate Password Rotation</>
                        ) : step.title.includes("Phone") ? (
                          <><Database size={14} /> Disavow Telecom Connections</>
                        ) : (
                          <><Shield size={14} /> Revoke Digital Permissions</>
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
