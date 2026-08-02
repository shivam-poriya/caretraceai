import React from 'react';
import { IconCheck, IconLock } from '../../components/Icons';

export const PatientPrivacy = () => {
  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Privacy &amp; Trust</h1>
          <p className="sub">Who can see your information, and what stays private to your care team.</p>
        </div>
      </div>

      <div className="privacy-cols">
        <div className="card privacy-col">
          <h3 style={{ color: 'var(--teal-900)' }}>You can see</h3>
          <ul>
            <li>
              <IconCheck size={16} style={{ color: 'var(--success)' }} />
              Your submitted symptoms &amp; health concerns
            </li>
            <li>
              <IconCheck size={16} style={{ color: 'var(--success)' }} />
              Your full chronological timeline
            </li>
            <li>
              <IconCheck size={16} style={{ color: 'var(--success)' }} />
              Your AI intake conversation transcript
            </li>
            <li>
              <IconCheck size={16} style={{ color: 'var(--success)' }} />
              Every update you've ever made
            </li>
            <li>
              <IconCheck size={16} style={{ color: 'var(--success)' }} />
              "What Your Doctor Sees" intake brief preview
            </li>
          </ul>
        </div>

        <div className="card privacy-col">
          <h3 style={{ color: '#6E4FA8' }}>Doctor-only private workspace</h3>
          <ul>
            <li>
              <IconLock size={16} style={{ color: '#6E4FA8' }} />
              Doctor clinical assessment &amp; diagnostic reasoning
            </li>
            <li>
              <IconLock size={16} style={{ color: '#6E4FA8' }} />
              Official medical diagnosis
            </li>
            <li>
              <IconLock size={16} style={{ color: '#6E4FA8' }} />
              Clinical treatment plan
            </li>
            <li>
              <IconLock size={16} style={{ color: '#6E4FA8' }} />
              Prescriptions &amp; dosage orders
            </li>
            <li>
              <IconLock size={16} style={{ color: '#6E4FA8' }} />
              Private clinician notes
            </li>
          </ul>
        </div>
      </div>

      <div
        className="card"
        style={{
          marginTop: '28px',
          padding: '24px',
          background: 'var(--bg-alt)',
          borderColor: 'var(--line)',
        }}
      >
        <h4 style={{ fontSize: '16px', color: 'var(--teal-900)', marginBottom: '8px' }}>
          Strict AI Safety Guardrails
        </h4>
        <p style={{ color: 'var(--slate)', fontSize: '14px', lineHeight: '1.6' }}>
          CareTraceAI works strictly as a patient intake structuring assistant. It NEVER generates medical diagnoses, NEVER prescribes treatment or medication, and NEVER overwrites historical records. All clinical decision-making remains 100% under the control of qualified healthcare professionals.
        </p>
      </div>
    </div>
  );
};
