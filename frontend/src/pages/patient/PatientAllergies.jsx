import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconPlus } from '../../components/Icons';

export const PatientAllergies = () => {
  const { showToast } = useAuth();
  const [allergies, setAllergies] = useState([]);
  const [allergen, setAllergen] = useState('');
  const [reaction, setReaction] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadAllergies = async () => {
    setLoading(true);
    try {
      const res = await patientAPI.getAllergies();
      setAllergies(res || []);
    } catch (err) {
      console.error('Failed to load allergies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllergies();
  }, []);

  const handleAddAllergy = async (e) => {
    e.preventDefault();
    if (!allergen.trim()) {
      showToast('Please enter an allergen name');
      return;
    }
    setSubmitting(true);
    try {
      await patientAPI.createAllergy({
        allergen: allergen.trim(),
        reaction: reaction.trim(),
      });
      showToast('Allergy added successfully!');
      setAllergen('');
      setReaction('');
      loadAllergies();
    } catch (err) {
      showToast('Failed to add allergy: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Allergies Management</h1>
          <p className="sub">API Endpoints: GET &amp; POST /v1/patient/allergies/</p>
        </div>
      </div>

      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
          + Add New Allergy
        </h3>
        <form onSubmit={handleAddAllergy}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="field">
              <label>Allergen Name *</label>
              <input
                type="text"
                placeholder="e.g. Penicillin, Peanuts, Latex"
                value={allergen}
                onChange={(e) => setAllergen(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>Reaction / Symptoms</label>
              <input
                type="text"
                placeholder="e.g. Hives, Anaphylaxis, Rash"
                value={reaction}
                onChange={(e) => setReaction(e.target.value)}
              />
            </div>
          </div>
          <button className="btn btn-primary btn-sm" type="submit" disabled={submitting}>
            <IconPlus size={16} /> {submitting ? 'Adding...' : 'Add Allergy Record'}
          </button>
        </form>
      </div>

      <h3 style={{ marginBottom: '14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        Your Recorded Allergies ({allergies.length})
      </h3>

      {loading ? (
        <div style={{ color: 'var(--slate)' }}>Loading allergies...</div>
      ) : allergies.length === 0 ? (
        <div className="card" style={{ padding: '36px', textAlign: 'center', color: 'var(--slate)' }}>
          No allergies reported.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '14px' }}>
          {allergies.map((a) => (
            <div key={a.id} className="card" style={{ padding: '18px' }}>
              <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--teal-900)' }}>
                {a.allergen}
              </div>
              <div style={{ color: 'var(--slate)', fontSize: '13.5px', marginTop: '4px' }}>
                Reaction: {a.reaction || 'Unspecified'}
              </div>
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
