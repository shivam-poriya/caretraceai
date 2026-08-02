import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconPlus, IconCheck } from '../../components/Icons';

export const PatientSymptoms = () => {
  const { showToast } = useAuth();
  const [symptoms, setSymptoms] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states for creating new symptom
  const [concern, setConcern] = useState('');
  const [severity, setSeverity] = useState(5);
  const [duration, setDuration] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Edit symptom state
  const [editingId, setEditingId] = useState(null);
  const [editSeverity, setEditSeverity] = useState(5);
  const [editDuration, setEditDuration] = useState('');

  const loadSymptoms = async () => {
    setLoading(true);
    try {
      const res = await patientAPI.getSymptoms();
      setSymptoms(res || []);
    } catch (err) {
      console.error('Failed to load symptoms:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSymptoms();
  }, []);

  const handleCreateSymptom = async (e) => {
    e.preventDefault();
    if (!concern.trim()) {
      showToast('Please enter a symptom concern');
      return;
    }
    setSubmitting(true);
    try {
      await patientAPI.createSymptom({
        concern: concern.trim(),
        severity: parseInt(severity),
        duration: duration.trim() || 'Not specified',
        notes: notes.trim(),
      });
      showToast('New symptom reported successfully!');
      setConcern('');
      setSeverity(5);
      setDuration('');
      setNotes('');
      loadSymptoms();
    } catch (err) {
      showToast('Failed to report symptom: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateSymptom = async (id) => {
    try {
      await patientAPI.updateSymptom(id, {
        severity: parseInt(editSeverity),
        duration: editDuration.trim(),
      });
      showToast('Symptom updated successfully!');
      setEditingId(null);
      loadSymptoms();
    } catch (err) {
      showToast('Failed to update symptom: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Reported Symptoms</h1>
          <p className="sub">API Endpoint: POST /v1/patient/symptoms/ &amp; PUT /v1/patient/symptoms/&#123;id&#125;/</p>
        </div>
      </div>

      {/* Form to Report New Symptom */}
      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
          + Report New Health Symptom
        </h3>
        <form onSubmit={handleCreateSymptom}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="field">
              <label>Symptom Concern *</label>
              <input
                type="text"
                placeholder="e.g. Chest pain, Lower back pain"
                value={concern}
                onChange={(e) => setConcern(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Duration</label>
              <input
                type="text"
                placeholder="e.g. 2 days, 3 weeks"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />
            </div>
          </div>

          <div className="field">
            <label>Severity Score (1 to 10): {severity}/10</label>
            <input
              type="range"
              min="1"
              max="10"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              style={{ width: '100%' }}
            />
          </div>

          <div className="field">
            <label>Additional Notes</label>
            <textarea
              placeholder="Describe what triggers it or any related notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          <button className="btn btn-primary btn-sm" type="submit" disabled={submitting}>
            <IconPlus size={16} /> {submitting ? 'Submitting...' : 'Submit Symptom Report'}
          </button>
        </form>
      </div>

      {/* Existing Symptoms List */}
      <h3 style={{ marginBottom: '14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        Your Recorded Symptoms ({symptoms.length})
      </h3>

      {loading ? (
        <div style={{ color: 'var(--slate)' }}>Loading symptoms...</div>
      ) : symptoms.length === 0 ? (
        <div className="card" style={{ padding: '36px', textAlign: 'center', color: 'var(--slate)' }}>
          No symptoms reported yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {symptoms.map((s) => (
            <div key={s.id} className="card" style={{ padding: '18px 22px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--teal-900)' }}>
                    {s.concern}
                  </div>
                  <div style={{ color: 'var(--slate)', fontSize: '13.5px', marginTop: '2px' }}>
                    Severity: <strong>{s.severity}/10</strong> · Duration: {s.duration || 'N/A'} · Reported:{' '}
                    {new Date(s.reported_at).toLocaleDateString()}
                  </div>
                  {s.notes && (
                    <div style={{ fontSize: '13px', fontStyle: 'italic', marginTop: '4px', color: 'var(--slate)' }}>
                      "{s.notes}"
                    </div>
                  )}
                </div>

                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    setEditingId(s.id);
                    setEditSeverity(s.severity);
                    setEditDuration(s.duration || '');
                  }}
                >
                  Edit Severity
                </button>
              </div>

              {/* Inline Edit Form */}
              {editingId === s.id && (
                <div
                  style={{
                    marginTop: '14px',
                    paddingTop: '14px',
                    borderTop: '1px solid var(--line)',
                    background: 'var(--bg-alt)',
                    padding: '14px',
                    borderRadius: '10px',
                  }}
                >
                  <div style={{ fontWeight: '600', fontSize: '13px', marginBottom: '8px' }}>
                    Update Symptom #{s.id}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div className="field">
                      <label>New Severity (1-10): {editSeverity}/10</label>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={editSeverity}
                        onChange={(e) => setEditSeverity(e.target.value)}
                      />
                    </div>
                    <div className="field">
                      <label>Updated Duration</label>
                      <input
                        type="text"
                        value={editDuration}
                        onChange={(e) => setEditDuration(e.target.value)}
                      />
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-primary btn-sm" onClick={() => handleUpdateSymptom(s.id)}>
                      Save Changes
                    </button>
                    <button className="btn btn-secondary btn-sm" onClick={() => setEditingId(null)}>
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
