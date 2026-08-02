import React, { useState, useEffect } from 'react';
import { patientAPI } from '../../api/api';

export const PatientTimeline = () => {
  const [timeline, setTimeline] = useState([]);
  const [filter, setFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTimeline = async () => {
      setLoading(true);
      try {
        const data = await patientAPI.getTimeline(filter);
        setTimeline(data || []);
      } catch (err) {
        console.error('Failed to fetch timeline:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, [filter]);

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Timeline</h1>
          <p className="sub">Every update you've shared, in chronological order.</p>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="tl-filters">
        {['All', 'Symptom', 'Allergy', 'Medication'].map((cat) => (
          <button
            key={cat}
            className={`chip ${filter === cat ? 'active' : ''}`}
            onClick={() => setFilter(cat)}
          >
            {cat === 'All' ? 'All Updates' : `${cat}s`}
          </button>
        ))}
      </div>

      {/* Timeline Thread */}
      {loading ? (
        <div style={{ color: 'var(--slate)', padding: '20px 0' }}>Loading timeline...</div>
      ) : timeline.length === 0 ? (
        <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--slate)' }}>
          No timeline records found for category "{filter}".
        </div>
      ) : (
        <div className="timeline">
          {timeline.map((item) => (
            <div key={item.id} className={`tl-item ${item.action_type === 'Added' ? 'is-new' : ''}`}>
              <div className="tl-date">
                {new Date(item.timestamp).toLocaleString()} · Source: {item.source || 'Patient Intake'}
              </div>
              <div className="card tl-card">
                <h4>
                  {item.category}: {item.new_value}
                </h4>
                {item.previous_value && (
                  <p style={{ color: 'var(--slate-light)', fontSize: '12.5px' }}>
                    Previous: {item.previous_value}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
