import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { patientAPI } from '../../api/api';
import { IconNote, IconClock, IconChat, IconShield, IconPlus } from '../../components/Icons';

export const PatientHome = ({ onNavigate }) => {
  const { user } = useAuth();
  const [resumePrompt, setResumePrompt] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResumePrompt = async () => {
      try {
        const res = await patientAPI.getResumePrompt();
        setResumePrompt(res.resume_prompt);
      } catch (err) {
        console.error('Failed to load resume prompt:', err);
      } finally {
        setLoading(false);
      }
    };
    loadResumePrompt();
  }, []);

  const name = user?.first_name ? user.first_name : user?.username || 'Patient';

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Good morning, {name}</h1>
          <p className="sub">Keep your care information up to date.</p>
        </div>
        <button className="btn btn-primary" onClick={() => onNavigate('intake')}>
          <IconPlus size={16} />
          Update My Information
        </button>
      </div>

      {/* Resume Prompt Banner */}
      {resumePrompt && (
        <div
          style={{
            background: 'var(--teal-100)',
            border: '1px solid var(--teal-500)',
            borderRadius: '16px',
            padding: '20px 24px',
            marginBottom: '28px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            flexWrap: 'wrap',
          }}
        >
          <div>
            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                fontWeight: '700',
                color: 'var(--teal-700)',
                textTransform: 'uppercase',
                marginBottom: '4px',
              }}
            >
              Continuous Care Assistant Prompt
            </div>
            <div style={{ fontSize: '15px', fontWeight: '500', color: 'var(--teal-900)' }}>
              "{resumePrompt}"
            </div>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('intake')}>
            Answer Prompt
          </button>
        </div>
      )}

      {/* Dashboard Tiles */}
      <div className="dash-grid">
        <div className="card dash-card" onClick={() => onNavigate('info')}>
          <div className="icon">
            <IconNote size={18} />
          </div>
          <h3>My Information</h3>
          <p>Your latest patient-reported symptoms, medications, and health history.</p>
        </div>

        <div className="card dash-card" onClick={() => onNavigate('intake')}>
          <div className="icon">
            <IconChat size={18} />
          </div>
          <h3>AI Intake Chat</h3>
          <p>Talk with CareTraceAI to record new updates or answer doctor questions.</p>
        </div>

        <div className="card dash-card" onClick={() => onNavigate('timeline')}>
          <div className="icon">
            <IconClock size={18} />
          </div>
          <h3>Timeline</h3>
          <p>See how your reported health information has changed chronologically.</p>
        </div>

        <div className="card dash-card" onClick={() => onNavigate('privacy')}>
          <div className="icon">
            <IconShield size={18} />
          </div>
          <h3>Privacy &amp; Trust</h3>
          <p>Understand how your data is structured and what remains private to doctors.</p>
        </div>
      </div>
    </div>
  );
};
