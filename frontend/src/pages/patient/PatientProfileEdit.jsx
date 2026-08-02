import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconCheck } from '../../components/Icons';

export const PatientProfileEdit = () => {
  const { showToast } = useAuth();
  const [profile, setProfile] = useState(null);
  const [bloodGroup, setBloodGroup] = useState('');
  const [emergencyName, setEmergencyName] = useState('');
  const [emergencyPhone, setEmergencyPhone] = useState('');
  const [medicalNotes, setMedicalNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const data = await patientAPI.getProfile();
        setProfile(data);
        if (data) {
          setBloodGroup(data.blood_group || '');
          setEmergencyName(data.emergency_contact_name || '');
          setEmergencyPhone(data.emergency_contact_phone || '');
          setMedicalNotes(data.medical_notes || '');
        }
      } catch (err) {
        console.error('Failed to fetch patient profile:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await patientAPI.updateProfile({
        blood_group: bloodGroup,
        emergency_contact_name: emergencyName,
        emergency_contact_phone: emergencyPhone,
        medical_notes: medicalNotes,
      });
      showToast('Health profile updated successfully!');
    } catch (err) {
      showToast('Failed to update profile: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ color: 'var(--slate)', padding: '40px 0' }}>Loading profile data...</div>;
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Edit Health Profile</h1>
          <p className="sub">API Endpoint: GET &amp; PUT /v1/patient/profile/</p>
        </div>
      </div>

      <div className="card" style={{ padding: '28px', maxWidth: '640px' }}>
        <form onSubmit={handleSave}>
          <div className="field">
            <label>Blood Group</label>
            <select value={bloodGroup} onChange={(e) => setBloodGroup(e.target.value)}>
              <option value="">Select Blood Group</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="field">
              <label>Emergency Contact Name</label>
              <input
                type="text"
                placeholder="Name"
                value={emergencyName}
                onChange={(e) => setEmergencyName(e.target.value)}
              />
            </div>
            <div className="field">
              <label>Emergency Contact Phone</label>
              <input
                type="text"
                placeholder="Phone number"
                value={emergencyPhone}
                onChange={(e) => setEmergencyPhone(e.target.value)}
              />
            </div>
          </div>

          <div className="field">
            <label>General Medical Notes</label>
            <textarea
              placeholder="Any ongoing conditions, implants, or general notes for your healthcare provider..."
              value={medicalNotes}
              onChange={(e) => setMedicalNotes(e.target.value)}
            />
          </div>

          <button className="btn btn-primary btn-sm" type="submit" disabled={saving}>
            <IconCheck size={16} /> {saving ? 'Saving...' : 'Save Profile Changes'}
          </button>
        </form>
      </div>
    </div>
  );
};
