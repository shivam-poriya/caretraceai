import React, { useState } from 'react';
import { authAPI, patientAPI, intakeAPI, doctorAPI } from '../api/api';

export const ApiTesterPage = () => {
  const [activeTab, setActiveTab] = useState('auth'); // 'auth', 'patient', 'intake', 'doctor'
  const [selectedEndpoint, setSelectedEndpoint] = useState('custom-auth-test');
  const [requestParam, setRequestParam] = useState('');
  const [responseLog, setResponseLog] = useState(null);
  const [loading, setLoading] = useState(false);

  const runEndpoint = async (name, fn) => {
    setSelectedEndpoint(name);
    setLoading(true);
    setResponseLog(null);
    try {
      const res = await fn();
      setResponseLog({ status: '200 OK', data: res });
    } catch (err) {
      setResponseLog({
        status: err.response?.status || 'Error',
        error: err.response?.data || err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '32px', maxWidth: '1080px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', color: 'var(--teal-900)' }}>Live API Endpoint Explorer (35 Endpoints)</h1>
        <p style={{ color: 'var(--slate)', fontSize: '14.5px' }}>
          Test and verify every backend endpoint directly from the React interface.
        </p>
      </div>

      {/* Module Tabs */}
      <div className="auth-tabs" style={{ marginBottom: '24px' }}>
        <div className={`auth-tab ${activeTab === 'auth' ? 'active' : ''}`} onClick={() => setActiveTab('auth')}>
          Auth &amp; OTP (7)
        </div>
        <div className={`auth-tab ${activeTab === 'patient' ? 'active' : ''}`} onClick={() => setActiveTab('patient')}>
          Patient API (11)
        </div>
        <div className={`auth-tab ${activeTab === 'intake' ? 'active' : ''}`} onClick={() => setActiveTab('intake')}>
          GenAI Intake (8)
        </div>
        <div className={`auth-tab ${activeTab === 'doctor' ? 'active' : ''}`} onClick={() => setActiveTab('doctor')}>
          Doctor Dashboard (13)
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
        {/* Endpoint Buttons Grid */}
        <div className="card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {activeTab === 'auth' && (
            <>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/custom-auth/test', () => authAPI.testAuth())}>
                GET /v1/custom-auth/test
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/custom-auth/get-user-profile/', () => authAPI.getUserProfile())}>
                GET /get-user-profile/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('POST /forgot-password/', () => authAPI.forgotPassword('patient@example.com'))}>
                POST /forgot-password/
              </button>
            </>
          )}

          {activeTab === 'patient' && (
            <>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/profile/', () => patientAPI.getProfile())}>
                GET /patient/profile/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/resume-prompt/', () => patientAPI.getResumePrompt())}>
                GET /patient/resume-prompt/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/symptoms/', () => patientAPI.getSymptoms())}>
                GET /patient/symptoms/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/allergies/', () => patientAPI.getAllergies())}>
                GET /patient/allergies/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/medications/', () => patientAPI.getMedications())}>
                GET /patient/medications/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/medical-history/', () => patientAPI.getMedicalHistory())}>
                GET /patient/medical-history/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/attachments/', () => patientAPI.getAttachments())}>
                GET /patient/attachments/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/queued-questions/', () => patientAPI.getQueuedQuestions())}>
                GET /patient/queued-questions/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/doctor-view-preview/', () => patientAPI.getDoctorViewPreview())}>
                GET /patient/doctor-view-preview/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/patient/timeline/', () => patientAPI.getTimeline())}>
                GET /patient/timeline/
              </button>
            </>
          )}

          {activeTab === 'intake' && (
            <>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/intake/sessions/', () => intakeAPI.getSessions())}>
                GET /intake/sessions/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('POST /v1/intake/sessions/', () => intakeAPI.startSession())}>
                POST /intake/sessions/ (New)
              </button>
            </>
          )}

          {activeTab === 'doctor' && (
            <>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/doctor/patients/', () => doctorAPI.getPatients())}>
                GET /doctor/patients/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /v1/doctor/patients/search/?q=demo', () => doctorAPI.searchPatients('demo'))}>
                GET /doctor/patients/search/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /doctor/patients/1/overview/', () => doctorAPI.getPatientOverview(1))}>
                GET /patients/1/overview/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /doctor/patients/1/what-changed/', () => doctorAPI.getWhatChanged(1))}>
                GET /patients/1/what-changed/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /doctor/patients/1/intake-summary/', () => doctorAPI.getIntakeSummary(1))}>
                GET /patients/1/intake-summary/
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => runEndpoint('GET /doctor/patients/1/export-brief/', () => doctorAPI.exportBrief(1))}>
                GET /patients/1/export-brief/
              </button>
            </>
          )}
        </div>

        {/* Live Response Output Window */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--slate-light)', marginBottom: '8px' }}>
            Selected Endpoint: <strong>{selectedEndpoint}</strong>
          </div>

          {loading ? (
            <div style={{ padding: '20px', color: 'var(--slate)' }}>Executing request...</div>
          ) : responseLog ? (
            <div>
              <div
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: responseLog.error ? 'var(--critical-bg)' : 'var(--success-bg)',
                  color: responseLog.error ? 'var(--critical)' : 'var(--success)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '13px',
                  fontWeight: '700',
                  marginBottom: '14px',
                  display: 'inline-block',
                }}
              >
                {responseLog.status}
              </div>

              <pre
                style={{
                  background: 'var(--ink)',
                  color: '#7FE0A8',
                  padding: '16px',
                  borderRadius: '10px',
                  fontSize: '13px',
                  fontFamily: 'var(--font-mono)',
                  overflowX: 'auto',
                  maxHeight: '400px',
                }}
              >
                {JSON.stringify(responseLog.data || responseLog.error, null, 2)}
              </pre>
            </div>
          ) : (
            <div style={{ color: 'var(--slate)', padding: '20px' }}>
              Click an endpoint button on the left to execute live API call.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
