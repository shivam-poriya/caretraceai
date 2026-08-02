import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogoMark, IconGrid, IconUsers, IconNote } from '../../components/Icons';
import { DoctorDashboard } from './DoctorDashboard';
import { DoctorPatients } from './DoctorPatients';
import { DoctorClinicalOverview } from './DoctorClinicalOverview';
import { ApiTesterPage } from '../ApiTesterPage';

export const DoctorShell = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('home');
  const [selectedPatientId, setSelectedPatientId] = useState(1);

  const handleSelectPatient = (id) => {
    setSelectedPatientId(id);
    setCurrentView('overview');
  };

  return (
    <div className="app-shell">
      {/* Doctor Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <LogoMark />
          <span>CareTraceAI</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <a
            className={`side-link ${currentView === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentView('home')}
          >
            <IconGrid size={17} /> Dashboard
          </a>
          <a
            className={`side-link ${currentView === 'patients' ? 'active' : ''}`}
            onClick={() => setCurrentView('patients')}
          >
            <IconUsers size={17} /> Patients List
          </a>
          <a
            className={`side-link ${currentView === 'overview' ? 'active' : ''}`}
            onClick={() => setCurrentView('overview')}
          >
            <IconNote size={17} /> Clinical Overview
          </a>
          <a
            className={`side-link ${currentView === 'api-tester' ? 'active' : ''}`}
            onClick={() => setCurrentView('api-tester')}
            style={{ color: '#7FE0A8' }}
          >
            ⚡ API Endpoint Explorer
          </a>
        </nav>

        <div className="side-cta" onClick={() => setCurrentView('patients')}>
          Review Updates
        </div>

        <div className="sidebar-foot">
          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.85)', marginBottom: '8px' }}>
            Doctor: <strong>{user?.first_name ? `Dr. ${user.first_name}` : user?.username || 'Doctor'}</strong>
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

      {/* Main Doctor View */}
      <main className="main">
        {currentView === 'home' && <DoctorDashboard onSelectPatient={handleSelectPatient} />}
        {currentView === 'patients' && <DoctorPatients onSelectPatient={handleSelectPatient} />}
        {currentView === 'overview' && <DoctorClinicalOverview patientId={selectedPatientId} />}
        {currentView === 'api-tester' && <ApiTesterPage />}
      </main>
    </div>
  );
};
