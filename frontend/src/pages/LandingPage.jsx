import React, { useState } from 'react';
import { LogoMark, IconChat, IconClock, IconNote, IconShield, IconCheck, IconAlert } from '../components/Icons';

export const LandingPage = ({ onOpenAuth }) => {
  const [activeTab, setActiveTab] = useState('diff'); // 'diff' or 'chat'

  return (
    <div id="landing" style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      {/* Top Navbar */}
      <nav className="topnav">
        <div className="topnav-inner" style={{ padding: '14px 28px' }}>
          <div className="logo">
            <LogoMark />
            <span style={{ fontFamily: 'var(--font-display)', fontWeight: '800', letterSpacing: '-0.02em' }}>
              CareTraceAI
            </span>
          </div>
          <div className="topnav-links">
            <a href="#features">Features</a>
            <a href="#how">How It Works</a>
            <a href="#trust">Trust &amp; Safety</a>
          </div>
          <div className="topnav-cta">
            <button className="btn btn-secondary btn-sm" onClick={() => onOpenAuth('login')}>
              Log In
            </button>
            <button className="btn btn-primary btn-sm" onClick={() => onOpenAuth('register')}>
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Compact 2 Column Layout */}
      <section style={{ padding: '48px 0 36px', background: 'linear-gradient(180deg, #FAF8F4 0%, #F3F0E9 100%)' }}>
        <div className="container" style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: '36px', alignItems: 'center' }}>
          <div>
            <div className="eyebrow" style={{ marginBottom: '8px' }}>
              ✨ GenAI-Powered Clinical Intake &amp; Handoff
            </div>
            <h1 style={{ fontSize: 'clamp(32px, 4vw, 48px)', fontWeight: '800', color: 'var(--teal-900)', lineHeight: '1.08', marginBottom: '14px' }}>
              Every update matters.
            </h1>
            <p style={{ fontSize: '16.5px', color: 'var(--slate)', lineHeight: '1.55', marginBottom: '24px', maxWidth: '520px' }}>
              CareTraceAI transforms patient-reported symptoms into a clear, continuous "What Changed?" summary for doctors — without diagnosing or prescribing.
            </p>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => onOpenAuth('register')}>
                Get Started Free →
              </button>
              <button className="btn btn-secondary" onClick={() => onOpenAuth('login')}>
                Doctor &amp; Patient Login
              </button>
            </div>

            <div style={{ display: 'flex', gap: '20px', marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--line)' }}>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '800', color: 'var(--teal-900)' }}>100%</div>
                <div style={{ fontSize: '12px', color: 'var(--slate)' }}>Doctor Controlled</div>
              </div>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '800', color: 'var(--teal-900)' }}>Zero</div>
                <div style={{ fontSize: '12px', color: 'var(--slate)' }}>AI Hallucinations</div>
              </div>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: '20px', fontWeight: '800', color: 'var(--teal-900)' }}>Instant</div>
                <div style={{ fontSize: '12px', color: 'var(--slate)' }}>EHR Export</div>
              </div>
            </div>
          </div>

          {/* Interactive Pipeline Card */}
          <div className="card" style={{ padding: '24px', borderRadius: '20px', boxShadow: 'var(--shadow-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', fontWeight: '700', fontFamily: 'var(--font-mono)', color: 'var(--teal-700)', textTransform: 'uppercase' }}>
                Continuous Clinical Thread
              </div>
              <div className="badge badge-ai">GenAI Intake</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ background: 'var(--teal-100)', padding: '12px 14px', borderRadius: '12px', borderLeft: '3px solid var(--teal-700)' }}>
                <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--teal-700)', fontWeight: '600' }}>PATIENT REPORT</div>
                <div style={{ fontSize: '13.5px', color: 'var(--teal-900)', fontWeight: '500' }}>"My headache got worse, now a 7/10 with nausea."</div>
              </div>

              <div style={{ textAlign: 'center', color: 'var(--teal-500)', fontSize: '16px' }}>↓</div>

              <div style={{ background: 'var(--teal-900)', color: '#fff', padding: '12px 14px', borderRadius: '12px' }}>
                <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: '#7FE0A8', fontWeight: '600' }}>WHAT CHANGED DIFF</div>
                <div style={{ fontSize: '13px', marginTop: '2px' }}>
                  <span style={{ color: '#7FE0A8' }}>+ New: Nausea</span> · <span style={{ color: '#F0C878' }}>↻ Updated: Severity 4/10 → 7/10</span>
                </div>
              </div>

              <div style={{ textAlign: 'center', color: 'var(--teal-500)', fontSize: '16px' }}>↓</div>

              <div style={{ background: 'var(--bg-alt)', padding: '12px 14px', borderRadius: '12px', border: '1px solid var(--line)' }}>
                <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--slate)', fontWeight: '600' }}>CLINICIAN HANDOFF BRIEF</div>
                <div style={{ fontSize: '13px', color: 'var(--ink)', fontWeight: '500' }}>Concise 30-second intake summary ready for EHR paste.</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Grid Feature Cards Section */}
      <section className="section" id="features" style={{ padding: '48px 0' }}>
        <div className="container">
          <div className="section-head" style={{ marginBottom: '32px' }}>
            <div className="eyebrow">Designed for Modern Healthcare</div>
            <h2>Built for Patient Clarity &amp; Doctor Efficiency</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '18px' }}>
            <div className="card" style={{ padding: '22px' }}>
              <div className="dash-card" style={{ padding: 0, boxShadow: 'none' }}>
                <div className="icon"><IconChat size={18} /></div>
                <h3 style={{ fontSize: '16px' }}>GenAI Intake Chat</h3>
                <p style={{ fontSize: '13.5px', color: 'var(--slate)' }}>
                  Patients report symptoms naturally. AI extracts facts and tracks completeness (0–100%).
                </p>
              </div>
            </div>

            <div className="card" style={{ padding: '22px' }}>
              <div className="dash-card" style={{ padding: 0, boxShadow: 'none' }}>
                <div className="icon"><IconClock size={18} /></div>
                <h3 style={{ fontSize: '16px' }}>"What Changed?" Diff</h3>
                <p style={{ fontSize: '13.5px', color: 'var(--slate)' }}>
                  Instant baseline diff highlights new, updated, and unchanged health parameters.
                </p>
              </div>
            </div>

            <div className="card" style={{ padding: '22px' }}>
              <div className="dash-card" style={{ padding: 0, boxShadow: 'none' }}>
                <div className="icon"><IconNote size={18} /></div>
                <h3 style={{ fontSize: '16px' }}>1-Click EHR Export</h3>
                <p style={{ fontSize: '13.5px', color: 'var(--slate)' }}>
                  Plain-text formatted intake briefs ready for instant copy-pasting into any EHR.
                </p>
              </div>
            </div>

            <div className="card" style={{ padding: '22px' }}>
              <div className="dash-card" style={{ padding: 0, boxShadow: 'none' }}>
                <div className="icon"><IconShield size={18} /></div>
                <h3 style={{ fontSize: '16px' }}>Private Workspace</h3>
                <p style={{ fontSize: '13.5px', color: 'var(--slate)' }}>
                  Doctor assessments, diagnoses, and prescriptions stay private to clinical staff.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works & Trust Combined Section */}
      <section className="section section-alt" id="how" style={{ padding: '48px 0' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', alignItems: 'center' }}>
            {/* How it works steps */}
            <div>
              <div className="eyebrow" style={{ marginBottom: '6px' }}>How CareTraceAI Works</div>
              <h2 style={{ fontSize: '26px', color: 'var(--teal-900)', marginBottom: '16px' }}>
                From Natural Conversation to Clinical Action
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div className="card" style={{ padding: '14px 18px', display: 'flex', gap: '14px', alignItems: 'center' }}>
                  <div className="step-num" style={{ fontSize: '14px', flexShrink: 0 }}>01</div>
                  <div>
                    <h4 style={{ fontSize: '15px' }}>Patient communicates naturally</h4>
                    <p style={{ fontSize: '13px', color: 'var(--slate)' }}>By typing or using quick-update chips anytime.</p>
                  </div>
                </div>

                <div className="card" style={{ padding: '14px 18px', display: 'flex', gap: '14px', alignItems: 'center' }}>
                  <div className="step-num" style={{ fontSize: '14px', flexShrink: 0 }}>02</div>
                  <div>
                    <h4 style={{ fontSize: '15px' }}>GenAI organizes &amp; validates</h4>
                    <p style={{ fontSize: '13px', color: 'var(--slate)' }}>Uses "Read it back" cards to confirm extracted facts.</p>
                  </div>
                </div>

                <div className="card" style={{ padding: '14px 18px', display: 'flex', gap: '14px', alignItems: 'center' }}>
                  <div className="step-num" style={{ fontSize: '14px', flexShrink: 0 }}>03</div>
                  <div>
                    <h4 style={{ fontSize: '15px' }}>Doctor reviews in seconds</h4>
                    <p style={{ fontSize: '13px', color: 'var(--slate)' }}>Sees what changed and sets review checkpoints.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Trust commitments */}
            <div className="card" id="trust" style={{ padding: '28px', background: 'var(--teal-900)', color: '#fff' }}>
              <div className="eyebrow" style={{ color: '#7FE0A8', marginBottom: '8px' }}>Trust &amp; Safety Protocol</div>
              <h3 style={{ fontSize: '22px', color: '#fff', marginBottom: '14px' }}>Clinicians Remain in Full Control</h3>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px' }}>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <IconCheck size={18} style={{ color: '#7FE0A8', flexShrink: 0 }} />
                  <strong>No AI Diagnosis:</strong> CareTraceAI structures data, never diagnoses medical conditions.
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <IconCheck size={18} style={{ color: '#7FE0A8', flexShrink: 0 }} />
                  <strong>No AI Prescriptions:</strong> All treatment decisions remain with licensed doctors.
                </li>
                <li style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <IconCheck size={18} style={{ color: '#7FE0A8', flexShrink: 0 }} />
                  <strong>Strict Auditability:</strong> Every update is timestamped in an unalterable timeline.
                </li>
              </ul>

              <button
                className="btn btn-primary btn-block"
                style={{ marginTop: '24px', background: '#fff', color: 'var(--teal-900)' }}
                onClick={() => onOpenAuth('register')}
              >
                Access System Now →
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Compact Footer */}
      <footer className="footer" style={{ padding: '24px 0', fontSize: '13px' }}>
        CareTraceAI — Every update matters. · GenAI for Good Patient Intake &amp; Clinical Handoff
      </footer>
    </div>
  );
};
