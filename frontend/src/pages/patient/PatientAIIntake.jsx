import React, { useState, useEffect, useRef } from 'react';
import { intakeAPI, patientAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconSend, IconMic, IconCheck, IconAlert } from '../../components/Icons';

export const PatientAIIntake = () => {
  const { user, showToast } = useAuth();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [completeness, setCompleteness] = useState(40);
  const [readBackCard, setReadBackCard] = useState(null);
  const [missingFields, setMissingFields] = useState([]);
  const [safetyAlert, setSafetyAlert] = useState(null);
  const [queuedQuestions, setQueuedQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, readBackCard]);

  // Load active session and doctor queued questions on mount
  useEffect(() => {
    const initIntake = async () => {
      try {
        // Fetch doctor queued questions
        const qQs = await patientAPI.getQueuedQuestions().catch(() => []);
        setQueuedQuestions(qQs || []);

        // Fetch sessions or start new one
        const sessions = await intakeAPI.getSessions().catch(() => []);
        if (sessions && sessions.length > 0) {
          const active = sessions.find((s) => s.status === 'active') || sessions[0];
          setSessionId(active.id);
          const msgs = await intakeAPI.getMessages(active.id);
          setMessages(msgs || []);
          if (active.completeness_score) {
            setCompleteness(active.completeness_score);
          }
        } else {
          const newSession = await intakeAPI.startSession();
          setSessionId(newSession.id);
          setMessages([
            {
              sender: 'ai',
              content: `Hi ${user?.first_name || user?.username || 'there'}! What health updates or symptoms would you like to share today?`,
            },
          ]);
        }
      } catch (err) {
        console.error('Failed to initialize intake session:', err);
      }
    };
    initIntake();
  }, [user]);

  const handleSendMessage = async (msgText = inputMessage, action = null, skipField = null) => {
    if (!msgText.trim() && !action) return;
    if (!sessionId) return;

    const userMsg = msgText.trim();
    setInputMessage('');
    setReadBackCard(null);

    // Optimistically append patient message
    const updatedMsgs = [...messages, { sender: 'patient', content: userMsg || '[Action]' }];
    setMessages(updatedMsgs);
    setLoading(true);

    try {
      const res = await intakeAPI.sendMessage(sessionId, userMsg, action, skipField);

      // Append AI response
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', content: res.ai_response },
      ]);

      // Update completeness ring
      if (res.completeness_percentage !== undefined) {
        setCompleteness(res.completeness_percentage);
      }

      // Update read-it-back confirmation card if present
      if (res.confirmation_card) {
        setReadBackCard(res.confirmation_card);
      }

      // Missing fields for skip button
      if (res.missing_information) {
        setMissingFields(res.missing_information);
      }

      // Safety escalation check
      if (res.safety_escalation) {
        setSafetyAlert(res.safety_escalation);
      } else {
        setSafetyAlert(null);
      }
    } catch (err) {
      showToast('Error processing message: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmExtraction = async (choice) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      const res = await intakeAPI.confirmExtraction(sessionId, choice === 'Yes, correct' ? 'yes' : 'fix');
      showToast(res.message);
      setReadBackCard(null);
      setMessages((prev) => [
        ...prev,
        { sender: 'patient', content: choice },
        { sender: 'ai', content: res.response || "Thank you for confirming! Your response is updated." },
      ]);
    } catch (err) {
      showToast('Confirmation error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickUpdateChip = async (chipType) => {
    setLoading(true);
    try {
      const res = await patientAPI.quickUpdate(chipType);
      showToast(res.message);
      setMessages((prev) => [
        ...prev,
        { sender: 'patient', content: `[Quick Update: ${chipType.replace('_', ' ')}]` },
        { sender: 'ai', content: `Got it! Recorded quick update: "${res.message}". Is there anything else?` },
      ]);
    } catch (err) {
      showToast('Quick update failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleSkipField = async () => {
    const fieldToSkip = missingFields[0] || 'missing detail';
    handleSendMessage(`I don't know`, 'skip', fieldToSkip);
  };

  // SVG stroke-dashoffset calculation for Completeness Ring
  const strokeDashoffset = 140 - (140 * completeness) / 100;

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>AI Intake Chat</h1>
          <p className="sub">Tell CareTraceAI what you'd like to update — there's no wrong way to say it.</p>
        </div>
      </div>

      {/* Safety Escalation Alert */}
      {safetyAlert && (
        <div className="safety-banner critical">
          <IconAlert className="ic" size={20} />
          <div>
            <h5>Urgent Care Notice</h5>
            <p>{safetyAlert.recommendation || 'Symptoms reported may require immediate medical evaluation. Please call emergency services if needed.'}</p>
          </div>
        </div>
      )}

      {/* Doctor Queued Questions Banner */}
      {queuedQuestions.length > 0 && (
        <div
          style={{
            background: '#F1EAF9',
            border: '1px solid #C9B8E8',
            borderRadius: '14px',
            padding: '14px 18px',
            marginBottom: '20px',
          }}
        >
          <div style={{ fontSize: '12px', fontWeight: '700', color: '#6E4FA8', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
            📌 Doctor Queued Questions ({queuedQuestions.length})
          </div>
          {queuedQuestions.map((q) => (
            <div key={q.id} style={{ fontSize: '14px', color: '#4A3274', margin: '4px 0' }}>
              • {q.question_text}
            </div>
          ))}
        </div>
      )}

      <div className="intake-layout">
        {/* Main Chat Box */}
        <div className="card intake-chat">
          <div className="intake-msgs">
            {messages.map((m, idx) => (
              <div key={idx} className={`bubble ${m.sender === 'patient' ? 'patient' : 'ai'}`}>
                {m.content}
              </div>
            ))}

            {loading && (
              <div className="bubble ai">
                <div className="typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            {/* Read-it-back Confirmation Card */}
            {readBackCard && (
              <div className="readback-card">
                <div className="readback-title">✨ Read-Back Confirmation</div>
                <div className="readback-text">{readBackCard.card_text || "I've recorded your update. Is this correct?"}</div>
                <div className="readback-actions">
                  <button className="btn btn-primary btn-sm" onClick={() => handleConfirmExtraction('Yes, correct')}>
                    <IconCheck size={14} /> Yes, correct
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => handleConfirmExtraction('Fix this')} style={{ background: '#fff' }}>
                    Fix this
                  </button>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick-Update Chips */}
          <div className="chips-row">
            <button className="suggest-chip" onClick={() => handleQuickUpdateChip('got_worse')}>
              ⚡ Got worse
            </button>
            <button className="suggest-chip" onClick={() => handleQuickUpdateChip('got_better')}>
              ✨ Got better
            </button>
            <button className="suggest-chip" onClick={() => handleQuickUpdateChip('same')}>
              — Same
            </button>
            <button className="suggest-chip" onClick={() => handleQuickUpdateChip('new_symptom')}>
              + New symptom
            </button>

            {missingFields.length > 0 && (
              <button
                className="suggest-chip"
                style={{ background: 'var(--amber-bg)', color: 'var(--amber)', borderColor: '#ECD8AC' }}
                onClick={handleSkipField}
              >
                ❓ Skip / I don't know
              </button>
            )}
          </div>

          {/* Input Row */}
          <div className="intake-input-row">
            <button
              className="btn-ghost btn-sm"
              title="Voice Input (Placeholder)"
              onClick={() => showToast('Voice mic input listening placeholder')}
            >
              <IconMic size={18} />
            </button>
            <textarea
              placeholder="Type what you'd like to update…"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <button className="btn btn-primary btn-sm" onClick={() => handleSendMessage()} disabled={loading}>
              <IconSend size={16} />
            </button>
          </div>
        </div>

        {/* Sidebar Info Panel & Completeness Ring */}
        <div className="card side-panel">
          <h4>Intake Completeness</h4>

          {/* Completeness Ring Metric */}
          <div className="ring-container">
            <div className="ring-circle">
              <svg viewBox="0 0 56 56">
                <circle className="ring-bg" cx="28" cy="28" r="22" />
                <circle
                  className="ring-progress"
                  cx="28"
                  cy="28"
                  r="22"
                  style={{ strokeDashoffset }}
                />
              </svg>
              <div className="ring-text">{completeness}%</div>
            </div>
            <div>
              <div style={{ fontWeight: '700', fontSize: '14px' }}>
                {completeness >= 80 ? 'Intake Complete' : completeness >= 50 ? 'Good Progress' : 'Initial Intake'}
              </div>
              <div style={{ color: 'var(--slate)', fontSize: '12px' }}>
                {completeness}% of intake details gathered
              </div>
            </div>
          </div>

          <div className="badge badge-ai" style={{ marginBottom: '12px' }}>
            ✨ GenAI Assisted Intake
          </div>

          <p style={{ fontSize: '12.5px', color: 'var(--slate)', lineHeight: '1.5' }}>
            CareTraceAI asks clarifying questions and organizes your reported symptoms for your doctor. It does not diagnose medical conditions.
          </p>

          {missingFields.length > 0 && (
            <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--line)' }}>
              <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--slate)', marginBottom: '6px' }}>
                Suggested details:
              </div>
              {missingFields.map((f, i) => (
                <div key={i} style={{ fontSize: '12px', color: 'var(--teal-700)', margin: '2px 0' }}>
                  • {f}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
