import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconPlus } from '../../components/Icons';

export const PatientMedications = () => {
  const { showToast } = useAuth();
  const [medications, setMedications] = useState([]);
  const [medName, setMedName] = useState('');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState('');
  const [prescribedBy, setPrescribedBy] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadMedications = async () => {
    setLoading(true);
    try {
      const res = await patientAPI.getMedications();
      setMedications(res || []);
    } catch (err) {
      console.error('Failed to load medications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMedications();
  }, []);

  const handleAddMedication = async (e) => {
    e.preventDefault();
    if (!medName.trim()) {
      showToast('Please enter a medication name');
      return;
    }
    setSubmitting(true);
    try {
      await patientAPI.createMedication({
        medication_name: medName.trim(),
        dosage: dosage.trim(),
        frequency: frequency.trim(),
        prescribed_by: prescribedBy.trim(),
      });
      showToast('Medication added successfully!');
      setMedName('');
      setDosage('');
      setFrequency('');
      setPrescribedBy('');
      loadMedications();
    } catch (err) {
      showToast('Failed to add medication: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Medications Management</h1>
          <p className="sub">API Endpoints: GET &amp; POST /v1/patient/medications/</p>
        </div>
      </div>

      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
          + Add Patient-Reported Medication
        </h3>
        <form onSubmit={handleAddMedication}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="field">
              <label>Medication Name *</label>
              <input
                type="text"
                placeholder="e.g. Ibuprofen, Metformin, Lisinopril"
                value={medName}
                onChange={(e) => setMedName(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Dosage</label>
              <input
                type="text"
                placeholder="e.g. 200mg, 500mg"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
              />
            </div>
            <div className="field">
              <label>Frequency</label>
              <input
                type="text"
                placeholder="e.g. As needed, Once daily"
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
              />
            </div>
            <div className="field">
              <label>Prescribed By / Source</label>
              <input
                type="text"
                placeholder="e.g. Dr. Smith / Over the counter"
                value={prescribedBy}
                onChange={(e) => setPrescribedBy(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-primary btn-sm" type="submit" disabled={submitting}>
            <IconPlus size={16} /> {submitting ? 'Adding...' : 'Add Medication Record'}
          </button>
        </form>
      </div>

      <h3 style={{ marginBottom: '14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        Your Reported Medications ({medications.length})
      </h3>

      {loading ? (
        <div style={{ color: 'var(--slate)' }}>Loading medications...</div>
      ) : medications.length === 0 ? (
        <div className="card" style={{ padding: '36px', textAlign: 'center', color: 'var(--slate)' }}>
          No medications reported.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '14px' }}>
          {medications.map((m) => (
            <div key={m.id} className="card" style={{ padding: '18px' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--teal-900)' }}>
                {m.medication_name}
              </div>
              <div style={{ color: 'var(--slate)', fontSize: '13.5px', marginTop: '4px' }}>
                Dosage: {m.dosage || 'N/A'} · Frequency: {m.frequency || 'N/A'}
              </div>
              {m.prescribed_by && (
                <div style={{ color: 'var(--slate-light)', fontSize: '12px', marginTop: '2px' }}>
                  Prescribed by: {m.prescribed_by}
                </div>
              )}
              <span className="badge badge-patient" style={{ marginTop: '8px' }}>
                Patient reported
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
