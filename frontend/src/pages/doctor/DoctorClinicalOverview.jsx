import React, { useState, useEffect } from 'react';
import { doctorAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconAlert, IconLock, IconCheck, IconNote, IconSend } from '../../components/Icons';

export const DoctorClinicalOverview = ({ patientId }) => {
  const { showToast } = useAuth();
  const [overview, setOverview] = useState(null);
  const [whatChanged, setWhatChanged] = useState(null);
  const [brief, setBrief] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  // Source quote modal state
  const [sourceModalText, setSourceModalText] = useState(null);

  // EHR Export modal state
  const [exportModalText, setExportModalText] = useState(null);
  const [copied, setCopied] = useState(false);

  // Queue question state
  const [queueInput, setQueueInput] = useState('');
  const [queuing, setQueuing] = useState(false);

  // Doctor clinical workspace fields
  const [assessment, setAssessment] = useState('');
  const [diagnosis, setDiagnosis] = useState('');
  const [treatmentPlan, setTreatmentPlan] = useState('');
  const [medName, setMedName] = useState('');
  const [dosage, setDosage] = useState('');
  const [instructions, setInstructions] = useState('');
  const [privateNote, setPrivateNote] = useState('');
  const [savingClinical, setSavingClinical] = useState(false);

  const loadPatientData = async () => {
    if (!patientId) return;
    setLoading(true);
    try {
      const [ov, wc, br, atts, convs, tl] = await Promise.all([
        doctorAPI.getPatientOverview(patientId).catch(() => null),
        doctorAPI.getWhatChanged(patientId).catch(() => null),
        doctorAPI.getIntakeSummary(patientId).catch(() => null),
        doctorAPI.getPatientAttachments(patientId).catch(() => []),
        doctorAPI.getPatientConversations(patientId).catch(() => []),
        doctorAPI.getPatientTimeline(patientId).catch(() => []),
      ]);

      setOverview(ov);
      setWhatChanged(wc);
      setBrief(br);
      setAttachments(atts || []);
      setConversations(convs || []);
      setTimeline(tl || []);
    } catch (err) {
      console.error('Failed to load patient clinical data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatientData();
  }, [patientId]);

  const handleMarkReviewed = async () => {
    try {
      const res = await doctorAPI.markReviewed(patientId, 'Reviewed by doctor');
      showToast(res.message);
      loadPatientData();
    } catch (err) {
      showToast('Error marking reviewed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleExportBrief = async () => {
    try {
      const res = await doctorAPI.exportBrief(patientId);
      const textToExport = res.export_formatted_text || res.plain_text_brief || JSON.stringify(res, null, 2);
      setExportModalText(textToExport);
      setCopied(false);
      try {
        await navigator.clipboard.writeText(textToExport);
        setCopied(true);
        showToast('EHR Brief copied to clipboard!');
      } catch (clipErr) {
        showToast('EHR Brief generated! Review below.');
      }
    } catch (err) {
      showToast('Failed to export brief: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDownloadTxt = () => {
    if (!exportModalText) return;
    const blob = new Blob([exportModalText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `EHR_Brief_Patient_${patientId}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showToast('Downloaded EHR Brief file!');
  };

  const handleQueueQuestion = async (e) => {
    e.preventDefault();
    if (!queueInput.trim()) return;
    setQueuing(true);
    try {
      const res = await doctorAPI.queueQuestion(patientId, queueInput.trim());
      showToast(res.message);
      setQueueInput('');
    } catch (err) {
      showToast('Failed to queue question: ' + (err.response?.data?.detail || err.message));
    } finally {
      setQueuing(false);
    }
  };

  const handleSaveClinicalNote = async () => {
    setSavingClinical(true);
    try {
      if (assessment || diagnosis) {
        await doctorAPI.saveClinicalAssessment(patientId, {
          assessment,
          diagnosis,
          treatment_plan: treatmentPlan,
        });
      }
      if (medName) {
        await doctorAPI.savePrescription(patientId, {
          medication_name: medName,
          dosage,
          instructions,
        });
      }
      if (privateNote) {
        await doctorAPI.saveNotes(patientId, { note_text: privateNote });
      }
      showToast('Private clinical note saved securely!');
    } catch (err) {
      showToast('Error saving clinical note: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSavingClinical(false);
    }
  };

  if (loading) {
    return <div style={{ color: 'var(--slate)', padding: '40px 0' }}>Loading clinical record...</div>;
  }

  const patientName = overview?.user
    ? `${overview.user.first_name} ${overview.user.last_name}`.trim() || overview.user.username
    : `Patient #${patientId}`;

  return (
    <div>
      {/* Patient Header */}
      <div className="page-head">
        <div>
          <h1>Patient #{patientId} — {patientName}</h1>
          <p className="sub mono">
            Patient-reported information · ID #{patientId} · Blood: {overview?.profile?.blood_group || 'N/A'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary btn-sm" onClick={handleExportBrief}>
            📋 Export EHR Brief
          </button>
          <button className="btn btn-primary btn-sm" onClick={handleMarkReviewed}>
            <IconCheck size={16} /> Mark as Reviewed
          </button>
        </div>
      </div>

      {/* Safety Alert Banner */}
      {overview?.has_safety_flag && (
        <div className="safety-banner critical">
          <IconAlert className="ic" size={22} />
          <div>
            <h5>Attention Required — Safety Flag Triggered</h5>
            <p>
              Patient has reported symptoms that may warrant prompt review. CareTraceAI does not diagnose medical conditions.
            </p>
          </div>
        </div>
      )}

      {/* WHAT CHANGED? Baseline Diff Card */}
      <h3 style={{ margin: '24px 0 14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        What Changed Since Last Review?
      </h3>
      <div className="card wc-card" style={{ marginBottom: '28px' }}>
        <div className="wc-head">
          <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)', color: 'var(--slate-light)' }}>
            Baseline Checkpoint Comparison
          </div>
          <button className="btn btn-secondary btn-sm" onClick={handleMarkReviewed}>
            Establish New Baseline Checkpoint
          </button>
        </div>

        {/* New items */}
        <div className="wc-group">
          <div className="wc-group-label new">+ New Reported Symptoms</div>
          {whatChanged?.new_symptoms?.length > 0 ? (
            whatChanged.new_symptoms.map((s, i) => (
              <div key={i} className="wc-row">
                <span>{s.concern} (Severity {s.severity}/10)</span>
                <span className="badge badge-new">New</span>
              </div>
            ))
          ) : (
            <div className="wc-row" style={{ color: 'var(--slate-light)' }}>No new symptoms</div>
          )}
        </div>

        {/* Updated items */}
        <div className="wc-group">
          <div className="wc-group-label updated">↻ Updated Symptoms</div>
          {whatChanged?.updated_symptoms?.length > 0 ? (
            whatChanged.updated_symptoms.map((s, i) => (
              <div key={i} className="wc-row">
                <span>{s.concern}</span>
                <span className="wc-diff">
                  <span className="old">{s.previous_severity}/10</span> →{' '}
                  <span className="new-val">{s.current_severity}/10</span>
                </span>
              </div>
            ))
          ) : (
            <div className="wc-row" style={{ color: 'var(--slate-light)' }}>No updated symptoms</div>
          )}
        </div>

        {/* Unchanged items */}
        <div className="wc-group">
          <div className="wc-group-label unchanged">— Unchanged Information</div>
          <div className="wc-row">
            <span>Allergy &amp; Medical History Status</span>
            <span style={{ color: 'var(--slate-light)', fontSize: '13px' }}>Unchanged</span>
          </div>
        </div>
      </div>

      {/* AI Intake Brief Card */}
      <h3 style={{ margin: '0 0 14px', fontSize: '18px', color: 'var(--teal-900)' }}>
        AI Doctor Brief
      </h3>
      <div className="card brief-card" style={{ marginBottom: '28px' }}>
        <div className="brief-section">
          <h5>Recent Patient Concerns</h5>
          {overview?.symptoms?.length > 0 ? (
            overview.symptoms.map((s) => (
              <div key={s.id} className="brief-line">
                <span>
                  <strong>{s.concern}</strong> — Severity {s.severity}/10
                  {s.duration ? `, duration ${s.duration}` : ''}
                </span>
                <button
                  className="view-source"
                  onClick={() => setSourceModalText(`"${s.concern} - reported duration: ${s.duration || 'Not specified'}"`)}
                >
                  View source
                </button>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--slate)', fontSize: '13.5px' }}>No symptoms reported.</p>
          )}
        </div>

        <div className="brief-section">
          <h5>Patient-Reported Medications</h5>
          {overview?.medications?.length > 0 ? (
            overview.medications.map((m) => (
              <div key={m.id} className="brief-line">
                <span>{m.medication_name} ({m.dosage || 'Dosage unstated'})</span>
                <span className="badge badge-patient">Patient reported</span>
              </div>
            ))
          ) : (
            <p style={{ color: 'var(--slate)', fontSize: '13.5px' }}>No medications reported.</p>
          )}
        </div>

        <div className="ai-tag">✨ AI-generated from patient-reported information</div>
      </div>

      {/* "Ask the Patient This" Doctor Queue Form */}
      <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '8px' }}>
          "Ask the Patient This" Doctor Question Queue
        </h3>
        <p style={{ color: 'var(--slate)', fontSize: '13.5px', marginBottom: '14px' }}>
          Queue specific clarifying questions that CareTraceAI will present to the patient on their next intake session.
        </p>

        <form onSubmit={handleQueueQuestion} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder="e.g. Does the headache feel worse when lying down?"
            value={queueInput}
            onChange={(e) => setQueueInput(e.target.value)}
            style={{
              flex: 1,
              padding: '11px 14px',
              border: '1px solid var(--line)',
              borderRadius: '10px',
              fontSize: '14px',
            }}
          />
          <button className="btn btn-primary btn-sm" type="submit" disabled={queuing}>
            <IconSend size={15} /> {queuing ? 'Queueing...' : 'Queue Question'}
          </button>
        </form>
      </div>

      {/* Medication Photo Attachments */}
      {attachments.length > 0 && (
        <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
            Patient Medication Strip &amp; Box Photos ({attachments.length})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '14px' }}>
            {attachments.map((att) => (
              <div key={att.id} style={{ border: '1px solid var(--line)', borderRadius: '10px', padding: '10px', background: 'var(--bg-alt)' }}>
                {att.file_url && (
                  <img
                    src={`http://127.0.0.1:8000${att.file_url}`}
                    alt="Medication Box"
                    style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '6px', marginBottom: '6px' }}
                  />
                )}
                <div style={{ fontSize: '12px', fontWeight: '600' }}>{att.description || 'Medication strip photo'}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw AI Conversations */}
      {conversations.length > 0 && (
        <div className="card" style={{ padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '17px', color: 'var(--teal-900)', marginBottom: '14px' }}>
            Raw Patient-AI Chat Transcript
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '300px', overflowY: 'auto' }}>
            {conversations.map((c) => (
              <div key={c.id} className={`bubble ${c.sender === 'patient' ? 'patient' : 'ai'}`}>
                <strong>{c.sender === 'patient' ? 'Patient: ' : 'CareTraceAI: '}</strong>
                {c.content}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Private Doctor-Only Workspace */}
      <div className="clinical-label">
        <IconLock size={16} /> PRIVATE CLINICAL WORKSPACE
      </div>
      <div className="clinical-box">
        <div className="clinical-notice">
          Private clinical information — visible only to authorized clinical staff. Never shown to patients.
        </div>

        <div className="field">
          <label>Clinical Assessment</label>
          <textarea
            placeholder="Enter clinical assessment &amp; examination findings..."
            value={assessment}
            onChange={(e) => setAssessment(e.target.value)}
          />
        </div>

        <div className="field">
          <label>Diagnosis</label>
          <input
            type="text"
            placeholder="Official diagnosis (clinician only)"
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
          />
        </div>

        <div className="field">
          <label>Treatment Plan</label>
          <textarea
            placeholder="Clinical recommendations and treatment plan..."
            value={treatmentPlan}
            onChange={(e) => setTreatmentPlan(e.target.value)}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="field">
            <label>Prescription Medication Name</label>
            <input
              type="text"
              placeholder="e.g. Amoxicillin"
              value={medName}
              onChange={(e) => setMedName(e.target.value)}
            />
          </div>
          <div className="field">
            <label>Dosage &amp; Frequency</label>
            <input
              type="text"
              placeholder="e.g. 500mg, 3x daily"
              value={dosage}
              onChange={(e) => setDosage(e.target.value)}
            />
          </div>
        </div>

        <div className="field">
          <label>Private Clinician Notes</label>
          <textarea
            placeholder="Private confidential notes..."
            value={privateNote}
            onChange={(e) => setPrivateNote(e.target.value)}
          />
        </div>

        <button className="btn btn-primary btn-sm" onClick={handleSaveClinicalNote} disabled={savingClinical}>
          {savingClinical ? 'Saving Clinical Note...' : 'Save Private Clinical Note'}
        </button>
      </div>

      {/* View Source Modal */}
      {sourceModalText && (
        <div className="modal-overlay" onClick={() => setSourceModalText(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Original Patient Statement</h3>
            <div className="src-quote">{sourceModalText}</div>
            <button className="btn btn-secondary btn-block" onClick={() => setSourceModalText(null)}>
              Close
            </button>
          </div>
        </div>
      )}

      {/* EHR Export Modal */}
      {exportModalText && (
        <div className="modal-overlay" onClick={() => setExportModalText(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ margin: 0, color: 'var(--teal-900)' }}>📋 Exported EHR Clinical Brief</h3>
              <button className="btn-ghost" onClick={() => setExportModalText(null)} style={{ fontSize: '20px' }}>×</button>
            </div>

            <p style={{ color: 'var(--slate)', fontSize: '13.5px', marginBottom: '14px' }}>
              One-click formatted plain-text intake brief ready for instant pasting into any Electronic Health Record (EHR) system (Epic, Cerner, AthenaHealth).
            </p>

            <pre
              style={{
                background: 'var(--ink)',
                color: '#7FE0A8',
                padding: '16px',
                borderRadius: '10px',
                fontFamily: 'var(--font-mono)',
                fontSize: '13px',
                whiteSpace: 'pre-wrap',
                maxHeight: '320px',
                overflowY: 'auto',
                marginBottom: '16px',
                border: '1px solid var(--line)'
              }}
            >
              {exportModalText}
            </pre>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                className="btn btn-primary"
                style={{ flex: 1 }}
                onClick={async () => {
                  await navigator.clipboard.writeText(exportModalText);
                  setCopied(true);
                  showToast('EHR Brief copied to clipboard!');
                }}
              >
                {copied ? '✓ Copied to Clipboard!' : '📋 Copy to Clipboard'}
              </button>

              <button
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={handleDownloadTxt}
              >
                💾 Download .TXT File
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
