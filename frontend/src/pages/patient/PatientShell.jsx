import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogoMark, IconHome, IconNote, IconChat, IconClock, IconShield, IconPlus, IconUser } from '../../components/Icons';
import { PatientHome } from './PatientHome';
import { PatientInfo } from './PatientInfo';
import { PatientSymptoms } from './PatientSymptoms';
import { PatientAllergies } from './PatientAllergies';
import { PatientMedications } from './PatientMedications';
import { PatientMedicalHistory } from './PatientMedicalHistory';
import { PatientProfileEdit } from './PatientProfileEdit';
import { PatientAIIntake } from './PatientAIIntake';
import { PatientTimeline } from './PatientTimeline';
import { PatientPrivacy } from './PatientPrivacy';
import { ApiTesterPage } from '../ApiTesterPage';

export const PatientShell = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('home');

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar" style={{ width: '260px' }}>
        <div className="logo">
          <LogoMark />
          <span>CareTraceAI</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px', overflowY: 'auto' }}>
          <a
            className={`side-link ${currentView === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentView('home')}
          >
            <IconHome size={17} /> Home
          </a>
          <a
            className={`side-link ${currentView === 'info' ? 'active' : ''}`}
            onClick={() => setCurrentView('info')}
          >
            <IconNote size={17} /> My Information
          </a>
          <a
            className={`side-link ${currentView === 'symptoms' ? 'active' : ''}`}
            onClick={() => setCurrentView('symptoms')}
          >
            <IconPlus size={17} /> Symptoms Manager
          </a>
          <a
            className={`side-link ${currentView === 'allergies' ? 'active' : ''}`}
            onClick={() => setCurrentView('allergies')}
          >
            • Allergies
          </a>
          <a
            className={`side-link ${currentView === 'medications' ? 'active' : ''}`}
            onClick={() => setCurrentView('medications')}
          >
            • Medications
          </a>
          <a
            className={`side-link ${currentView === 'history' ? 'active' : ''}`}
            onClick={() => setCurrentView('history')}
          >
            • Medical History
          </a>
          <a
            className={`side-link ${currentView === 'profile-edit' ? 'active' : ''}`}
            onClick={() => setCurrentView('profile-edit')}
          >
            <IconUser size={17} /> Edit Profile
          </a>
          <a
            className={`side-link ${currentView === 'intake' ? 'active' : ''}`}
            onClick={() => setCurrentView('intake')}
          >
            <IconChat size={17} /> AI Intake Chat
          </a>
          <a
            className={`side-link ${currentView === 'timeline' ? 'active' : ''}`}
            onClick={() => setCurrentView('timeline')}
          >
            <IconClock size={17} /> Timeline
          </a>
          <a
            className={`side-link ${currentView === 'privacy' ? 'active' : ''}`}
            onClick={() => setCurrentView('privacy')}
          >
            <IconShield size={17} /> Privacy
          </a>
          <a
            className={`side-link ${currentView === 'api-tester' ? 'active' : ''}`}
            onClick={() => setCurrentView('api-tester')}
            style={{ color: '#7FE0A8' }}
          >
            ⚡ API Endpoint Explorer
          </a>
        </nav>

        <div className="side-cta" onClick={() => setCurrentView('intake')}>
          + Update My Information
        </div>

        <div className="sidebar-foot">
          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.85)', marginBottom: '8px' }}>
            Patient: <strong>{user?.username || 'Authenticated Patient'}</strong>
          </div>

          <button
            className="btn-ghost btn-sm"
            onClick={logout}
            style={{ color: 'rgba(255,255,255,0.7)', width: '100%', justifyContent: 'flex-start', paddingLeft: 0 }}
          >
            ← Log out
          </button>
        </div>
      </aside>

      {/* Main View Router */}
      <main className="main">
        {currentView === 'home' && <PatientHome onNavigate={(v) => setCurrentView(v)} />}
        {currentView === 'info' && <PatientInfo />}
        {currentView === 'symptoms' && <PatientSymptoms />}
        {currentView === 'allergies' && <PatientAllergies />}
        {currentView === 'medications' && <PatientMedications />}
        {currentView === 'history' && <PatientMedicalHistory />}
        {currentView === 'profile-edit' && <PatientProfileEdit />}
        {currentView === 'intake' && <PatientAIIntake />}
        {currentView === 'timeline' && <PatientTimeline />}
        {currentView === 'privacy' && <PatientPrivacy />}
        {currentView === 'api-tester' && <ApiTesterPage />}
      </main>
    </div>
  );
};
