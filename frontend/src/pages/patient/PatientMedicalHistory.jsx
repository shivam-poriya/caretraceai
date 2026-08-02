import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconPlus } from '../../components/Icons';

export const PatientMedicalHistory = () => {
  const { showToast } = useAuth();
  const [history, setHistory] = useState([]);
  const [condition, setCondition] = useState('');
  const [diagnosisDate, setDiagnosisDate] = useState('');
  const [statusText, setStatusText] = useState('Active');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const res = await patientAPI.getMedicalHistory();
      setHistory(res || []);
    } catch (err) {
      console.error('Failed to load medical history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleAddHistory = async (e) => {
    e.preventDefault();
    if (!condition.trim()) {
      showToast('Please enter a medical condition');
      return;
    }
    setSubmitting(true);
    try {
      await patientAPI.createMedicalHistory({
        condition: condition.trim(),
        diagnosis_date: diagnosisDate.trim(),
        status: statusText.trim(),
        notes: notes.trim(),
      });
      showToast('Medical history item added successfully!');
      setCondition('');
      setDiagnosisDate('');
      setStatusText('Active');
      setNotes('');
      loadHistory();
    } catch (err) {
      showToast('Failed to add medical history: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Medical History</h1>
          <p className="sub">API Endpoints: GET &amp; POST /v1/patient/medical-history/</p>
        </div>
      </div>

      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
          + Add Medical History Item
        </h3>
        <form onSubmit={handleAddHistory}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="field">
              <label>Condition / Surgery *</label>
              <input
                type="text"
                placeholder="e.g. Asthma, Type 2 Diabetes, Appendectomy"
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Diagnosis Date / Year</label>
              <input
                type="text"
                placeholder="e.g. 2021, March 2019"
                value={diagnosisDate}
                onChange={(e) => setDiagnosisDate(e.target.value)}
              />
            </div>
            <div className="field">
              <label>Status</label>
              <select value={statusText} onChange={(e) => setStatusText(e.target.value)}>
                <option value="Active">Active</option>
                <option value="Resolved">Resolved</option>
                <option value="Managed">Managed</option>
              </select>
            </div>
            <div className="field">
              <label>Notes</label>
              <input
                type="text"
                placeholder="Additional notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-primary btn-sm" type="submit" disabled={submitting}>
            <IconPlus size={16} /> {submitting ? 'Adding...' : 'Add Medical History'}
          </button>
        </form>
      </div>

      <h3 style={{ marginBottom: '14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        Recorded Medical History ({history.length})
      </h3>

      {loading ? (
        <div style={{ color: 'var(--slate)' }}>Loading medical history...</div>
      ) : history.length === 0 ? (
        <div className="card" style={{ padding: '36px', textAlign: 'center', color: 'var(--slate)' }}>
          No medical history items recorded.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '14px' }}>
          {history.map((h) => (
            <div key={h.id} className="card" style={{ padding: '18px' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--teal-900)' }}>
                {h.condition}
              </div>
              <div style={{ color: 'var(--slate)', fontSize: '13.5px', marginTop: '4px' }}>
                Status: <strong>{h.status || 'Active'}</strong> · Diagnosed: {h.diagnosis_date || 'N/A'}
              </div>
              {h.notes && (
                <div style={{ fontSize: '12.5px', fontStyle: 'italic', marginTop: '4px', color: 'var(--slate)' }}>
                  "{h.notes}"
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
