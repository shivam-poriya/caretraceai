import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconPlus, IconNote, IconCheck } from '../../components/Icons';

export const PatientInfo = () => {
  const { showToast } = useAuth();
  const [symptoms, setSymptoms] = useState([]);
  const [allergies, setAllergies] = useState([]);
  const [medications, setMedications] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [doctorPreview, setDoctorPreview] = useState(null);
  const [showDoctorPreview, setShowDoctorPreview] = useState(false);
  const [loading, setLoading] = useState(true);

  // Upload attachment form
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadDesc, setUploadDesc] = useState('');
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [syms, alls, meds, atts, docPrev] = await Promise.all([
        patientAPI.getSymptoms().catch(() => []),
        patientAPI.getAllergies().catch(() => []),
        patientAPI.getMedications().catch(() => []),
        patientAPI.getAttachments().catch(() => []),
        patientAPI.getDoctorViewPreview().catch(() => null),
      ]);
      setSymptoms(syms || []);
      setAllergies(alls || []);
      setMedications(meds || []);
      setAttachments(atts || []);
      setDoctorPreview(docPrev);
    } catch (err) {
      console.error('Failed to load patient information:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      showToast('Please select an image file to upload');
      return;
    }
    setUploading(true);
    try {
      await patientAPI.uploadAttachment(uploadFile, uploadDesc);
      showToast('Photo attachment uploaded successfully!');
      setUploadFile(null);
      setUploadDesc('');
      loadData();
    } catch (err) {
      showToast('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>My Information</h1>
          <p className="sub">What you've reported so far for doctor review.</p>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setShowDoctorPreview(!showDoctorPreview)}
        >
          {showDoctorPreview ? 'Hide Doctor Preview' : '👁️ What Your Doctor Sees'}
        </button>
      </div>

      {/* Doctor View Preview Card */}
      {showDoctorPreview && doctorPreview && (
        <div
          className="card"
          style={{
            padding: '24px',
            marginBottom: '28px',
            background: 'var(--teal-900)',
            color: '#fff',
          }}
        >
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              textTransform: 'uppercase',
              color: '#7FE0A8',
              marginBottom: '8px',
            }}
          >
            "What Your Doctor Sees" Transparency Preview
          </div>
          <h3 style={{ fontSize: '18px', color: '#fff', marginBottom: '14px' }}>
            Structured Intake Brief
          </h3>
          {doctorPreview.intake_brief ? (
            <div style={{ whiteSpace: 'pre-line', fontSize: '14px', lineHeight: '1.6', opacity: 0.9 }}>
              {doctorPreview.intake_brief}
            </div>
          ) : (
            <p style={{ fontSize: '14px', opacity: 0.8 }}>No intake summary generated yet.</p>
          )}
          <div
            style={{
              marginTop: '14px',
              fontSize: '12px',
              color: 'rgba(255,255,255,0.6)',
              fontFamily: 'var(--font-mono)',
            }}
          >
            🔒 Doctor's private clinical notes are kept separate to maintain clinician workflow.
          </div>
        </div>
      )}

      {/* Main Info Card */}
      <div className="card brief-card" style={{ marginBottom: '28px' }}>
        {/* Symptoms Section */}
        <div className="brief-section">
          <h5>Recent Concerns &amp; Symptoms</h5>
          {symptoms.length === 0 ? (
            <p style={{ color: 'var(--slate)', fontSize: '13.5px' }}>No symptoms reported yet.</p>
          ) : (
            symptoms.map((s) => (
              <div key={s.id} className="brief-line">
                <span>
                  <strong>{s.concern}</strong> — Severity {s.severity}/10
                  {s.duration && ` (${s.duration})`}
                </span>
                <span className="badge badge-patient">Patient reported</span>
              </div>
            ))
          )}
        </div>

        {/* Allergies Section */}
        <div className="brief-section">
          <h5>Allergies</h5>
          {allergies.length === 0 ? (
            <p style={{ color: 'var(--slate)', fontSize: '13.5px' }}>No allergies reported yet.</p>
          ) : (
            allergies.map((a) => (
              <div key={a.id} className="brief-line">
                <span>
                  <strong>{a.allergen}</strong> {a.reaction ? `— Reaction: ${a.reaction}` : ''}
                </span>
                <span className="badge badge-patient">Patient reported</span>
              </div>
            ))
          )}
        </div>

        {/* Medications Section */}
        <div className="brief-section">
          <h5>Patient-Reported Medications</h5>
          {medications.length === 0 ? (
            <p style={{ color: 'var(--slate)', fontSize: '13.5px' }}>No medications reported yet.</p>
          ) : (
            medications.map((m) => (
              <div key={m.id} className="brief-line">
                <span>
                  <strong>{m.medication_name}</strong> {m.dosage ? `(${m.dosage})` : ''}{' '}
                  {m.frequency ? `— ${m.frequency}` : ''}
                </span>
                <span className="badge badge-patient">Patient reported</span>
              </div>
            ))
          )}
        </div>

        <div className="ai-tag">✨ Organized by CareTraceAI from what you've reported</div>
      </div>

      {/* Medication Strip Photo Attachment Upload */}
      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '8px' }}>
          Photo Attachments (Medication Box / Strip Photos)
        </h3>
        <p style={{ color: 'var(--slate)', fontSize: '14px', marginBottom: '18px' }}>
          Photograph your medication boxes or strips for direct doctor review. Photos are stored securely as raw patient-reported attachments without AI inference errors.
        </p>

        <form onSubmit={handleUpload} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setUploadFile(e.target.files[0])}
            style={{ fontSize: '14px' }}
          />
          <input
            type="text"
            placeholder="Optional description (e.g. Morning pill box)"
            value={uploadDesc}
            onChange={(e) => setUploadDesc(e.target.value)}
            style={{
              flex: 1,
              minWidth: '200px',
              padding: '9px 12px',
              border: '1px solid var(--line)',
              borderRadius: '8px',
              fontSize: '14px',
            }}
          />
          <button className="btn btn-primary btn-sm" type="submit" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload Photo'}
          </button>
        </form>

        {/* Existing Attachments List */}
        {attachments.length > 0 && (
          <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '14px' }}>
            {attachments.map((att) => (
              <div key={att.id} style={{ border: '1px solid var(--line)', borderRadius: '10px', padding: '10px', background: 'var(--bg-alt)' }}>
                {att.file_url && (
                  <img
                    src={`http://127.0.0.1:8000${att.file_url}`}
                    alt="Attachment"
                    style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '6px', marginBottom: '6px' }}
                  />
                )}
                <div style={{ fontSize: '12px', fontWeight: '600' }}>{att.description || 'Medication photo'}</div>
                <div style={{ fontSize: '11px', color: 'var(--slate-light)', fontFamily: 'var(--font-mono)' }}>
                  Uploaded {new Date(att.uploaded_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
