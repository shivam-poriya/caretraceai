import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/api';

export const AuthModal = ({ isOpen, onClose, initialTab = 'login', initialRole = 'patient' }) => {
  const { login, register, showToast } = useAuth();
  const [activeTab, setActiveTab] = useState(initialTab); // 'login', 'register', 'forgot'

  // Login form state
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form state
  const [regRole, setRegRole] = useState(initialRole);
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regFirstName, setRegFirstName] = useState('');
  const [regLastName, setRegLastName] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regSpecialty, setRegSpecialty] = useState('General Physician');

  // Forgot password OTP flow state
  const [otpStep, setOtpStep] = useState(1); // 1: email, 2: verify, 3: reset
  const [otpEmail, setOtpEmail] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!loginUsername || !loginPassword) {
      showToast('Please enter username and password');
      return;
    }
    setLoading(true);
    const res = await login(loginUsername, loginPassword);
    setLoading(false);
    if (res.success) {
      onClose();
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!regUsername || !regEmail || !regPassword) {
      showToast('Please fill required fields (username, email, password)');
      return;
    }
    setLoading(true);
    const res = await register({
      username: regUsername,
      email: regEmail,
      password: regPassword,
      role: regRole,
      first_name: regFirstName,
      last_name: regLastName,
      phone: regPhone,
      specialty: regRole === 'doctor' ? regSpecialty : undefined,
    });
    setLoading(false);
    if (res.success) {
      setActiveTab('login');
      setLoginUsername(regUsername);
    }
  };

  const handleRequestOTP = async (e) => {
    e.preventDefault();
    if (!otpEmail) {
      showToast('Please enter your email');
      return;
    }
    setLoading(true);
    try {
      await authAPI.forgotPassword(otpEmail);
      showToast('OTP sent to your email! (Check inbox)');
      setOtpStep(2);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    if (!otpCode) {
      showToast('Please enter 6-digit OTP code');
      return;
    }
    setLoading(true);
    try {
      await authAPI.verifyOTP(otpEmail, otpCode);
      showToast('OTP verified successfully!');
      setOtpStep(3);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Invalid or expired OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!newPassword) {
      showToast('Please enter a new password');
      return;
    }
    setLoading(true);
    try {
      await authAPI.resetPassword(otpEmail, otpCode, newPassword);
      showToast('Password reset successfully! Please log in.');
      setActiveTab('login');
      setOtpStep(1);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '460px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0, fontSize: '18px', color: 'var(--teal-900)' }}>Account Access</h3>
          <button className="btn-ghost" onClick={onClose} style={{ fontSize: '20px', padding: '4px 8px' }}>×</button>
        </div>

        {/* Auth Tabs */}
        <div className="auth-tabs">
          <div
            className={`auth-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => setActiveTab('login')}
          >
            Log In
          </div>
          <div
            className={`auth-tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            Register
          </div>
          <div
            className={`auth-tab ${activeTab === 'forgot' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('forgot');
              setOtpStep(1);
            }}
          >
            Forgot Password
          </div>
        </div>

        {/* TAB 1: LOGIN */}
        {activeTab === 'login' && (
          <form onSubmit={handleLoginSubmit}>
            <div className="field">
              <label>Username or Email</label>
              <input
                type="text"
                placeholder="Enter username or email"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              {loading ? 'Logging in...' : 'Log In'}
            </button>
          </form>
        )}

        {/* TAB 2: REGISTER */}
        {activeTab === 'register' && (
          <form onSubmit={handleRegisterSubmit}>
            <div className="field">
              <label>Registering as:</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className={`btn btn-sm ${regRole === 'patient' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1 }}
                  onClick={() => setRegRole('patient')}
                >
                  Patient
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${regRole === 'doctor' ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ flex: 1 }}
                  onClick={() => setRegRole('doctor')}
                >
                  Doctor
                </button>
              </div>
            </div>
            <div className="field">
              <label>Username *</label>
              <input
                type="text"
                placeholder="choose username"
                value={regUsername}
                onChange={(e) => setRegUsername(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Email *</label>
              <input
                type="email"
                placeholder="your@email.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Password *</label>
              <input
                type="password"
                placeholder="create password"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div className="field">
                <label>First Name</label>
                <input
                  type="text"
                  placeholder="First name"
                  value={regFirstName}
                  onChange={(e) => setRegFirstName(e.target.value)}
                />
              </div>
              <div className="field">
                <label>Last Name</label>
                <input
                  type="text"
                  placeholder="Last name"
                  value={regLastName}
                  onChange={(e) => setRegLastName(e.target.value)}
                />
              </div>
            </div>
            {regRole === 'doctor' && (
              <div className="field">
                <label>Specialty</label>
                <input
                  type="text"
                  placeholder="e.g. General Physician, Cardiology"
                  value={regSpecialty}
                  onChange={(e) => setRegSpecialty(e.target.value)}
                />
              </div>
            )}
            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              {loading ? 'Registering...' : `Create ${regRole === 'doctor' ? 'Doctor' : 'Patient'} Account`}
            </button>
          </form>
        )}

        {/* TAB 3: FORGOT PASSWORD (OTP FLOW) */}
        {activeTab === 'forgot' && (
          <div>
            <div style={{ fontSize: '13px', color: 'var(--slate)', marginBottom: '14px' }}>
              {otpStep === 1 && 'Step 1: Enter your account email to receive a 6-digit OTP code.'}
              {otpStep === 2 && `Step 2: Enter the 6-digit OTP sent to ${otpEmail}.`}
              {otpStep === 3 && 'Step 3: Enter your new password.'}
            </div>

            {otpStep === 1 && (
              <form onSubmit={handleRequestOTP}>
                <div className="field">
                  <label>Email Address</label>
                  <input
                    type="email"
                    placeholder="registered@email.com"
                    value={otpEmail}
                    onChange={(e) => setOtpEmail(e.target.value)}
                    required
                  />
                </div>
                <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
                  {loading ? 'Sending OTP...' : 'Send 6-Digit OTP'}
                </button>
              </form>
            )}

            {otpStep === 2 && (
              <form onSubmit={handleVerifyOTP}>
                <div className="field">
                  <label>6-Digit OTP Code</label>
                  <input
                    type="text"
                    placeholder="123456"
                    maxLength={6}
                    className="mono"
                    style={{ letterSpacing: '4px', fontSize: '18px', textAlign: 'center' }}
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    required
                  />
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => setOtpStep(1)}
                  >
                    Back
                  </button>
                  <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
                    {loading ? 'Verifying...' : 'Verify OTP'}
                  </button>
                </div>
              </form>
            )}

            {otpStep === 3 && (
              <form onSubmit={handleResetPassword}>
                <div className="field">
                  <label>New Password</label>
                  <input
                    type="password"
                    placeholder="Enter new password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                  />
                </div>
                <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
                  {loading ? 'Resetting Password...' : 'Confirm New Password'}
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
