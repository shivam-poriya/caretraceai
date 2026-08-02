import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LandingPage } from './pages/LandingPage';
import { PatientShell } from './pages/patient/PatientShell';
import { DoctorShell } from './pages/doctor/DoctorShell';
import { AuthModal } from './components/AuthModal';

const AppContent = () => {
  const { token, role } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState('login');
  const [authModalRole, setAuthModalRole] = useState('patient');

  const handleOpenAuth = (tab = 'login', role = 'patient') => {
    setAuthModalTab(tab);
    setAuthModalRole(role);
    setAuthModalOpen(true);
  };

  return (
    <>
      {token ? (
        role === 'doctor' ? (
          <DoctorShell />
        ) : (
          <PatientShell />
        )
      ) : (
        <LandingPage onOpenAuth={handleOpenAuth} />
      )}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialTab={authModalTab}
        initialRole={authModalRole}
      />
    </>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
