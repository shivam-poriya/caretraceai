import React, { useState, useEffect } from 'react';
import { doctorAPI } from '../../api/api';
import { useAuth } from '../../context/AuthContext';
import { IconAlert, IconUsers, IconClock } from '../../components/Icons';

export const DoctorDashboard = ({ onSelectPatient }) => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const data = await doctorAPI.getPatients();
        setPatients(data || []);
      } catch (err) {
        console.error('Failed to fetch doctor dashboard patients:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  const doctorName = user?.last_name ? `Dr. ${user.last_name}` : user?.username ? `Dr. ${user.username}` : 'Doctor';

  const totalPatients = patients.length;
  const newUpdatesCount = patients.filter((p) => p.change_count > 0).length;
  const safetyFlaggedCount = patients.filter((p) => p.has_safety_flag).length;

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Good morning, {doctorName}</h1>
          <p className="sub">Here's what's changed since you last reviewed.</p>
        </div>
      </div>

      {/* Stat Row */}
      <div className="stat-row">
        <div className="card stat-card">
          <div className="num">{totalPatients}</div>
          <div className="label">Assigned Patients</div>
        </div>
        <div className="card stat-card">
          <div className="num" style={{ color: 'var(--amber)' }}>
            {newUpdatesCount}
          </div>
          <div className="label">New Updates</div>
        </div>
        <div className="card stat-card">
          <div className="num" style={{ color: 'var(--critical)' }}>
            {safetyFlaggedCount}
          </div>
          <div className="label">Safety Flagged</div>
        </div>
        <div className="card stat-card">
          <div className="num">{totalPatients > 0 ? totalPatients : 12}</div>
          <div className="label">Today's Consultations</div>
        </div>
      </div>

      <h3 style={{ marginBottom: '16px', fontSize: '18px', color: 'var(--teal-900)' }}>
        Priority Patient Queue
      </h3>

      {loading ? (
        <div style={{ color: 'var(--slate)' }}>Loading patient queue...</div>
      ) : patients.length === 0 ? (
        <div className="card" style={{ padding: '36px', textAlign: 'center', color: 'var(--slate)' }}>
          No patients assigned yet.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {patients.map((p) => (
            <div
              key={p.patient_id}
              className="card"
              onClick={() => onSelectPatient(p.patient_id)}
              style={{
                padding: '18px 22px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                borderLeft: p.has_safety_flag ? '4px solid var(--critical)' : p.change_count > 0 ? '4px solid var(--amber)' : '1px solid var(--line)',
                transition: 'transform 0.15s ease',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className="p-name" style={{ fontSize: '16px', color: 'var(--teal-900)' }}>
                    {p.name}
                  </span>
                  {p.has_safety_flag && (
                    <span className="badge badge-critical">
                      <IconAlert size={12} /> Red Flag Alert
                    </span>
                  )}
                  {p.change_count > 0 && (
                    <span className="badge badge-updated">
                      ↻ {p.change_count} Change{p.change_count > 1 ? 's' : ''}
                    </span>
                  )}
                </div>
                <div style={{ color: 'var(--slate)', fontSize: '13px', marginTop: '4px' }}>
                  {p.gender ? `${p.gender}` : ''} {p.blood_group ? `· Blood Group: ${p.blood_group}` : ''}{' '}
                  · Phone: {p.phone || 'N/A'}
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--slate-light)' }}>
                  {p.last_update ? `Updated ${new Date(p.last_update).toLocaleTimeString()}` : 'No recent updates'}
                </div>
                <button className="btn btn-secondary btn-sm" style={{ marginTop: '6px' }}>
                  Review Clinical Brief →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
