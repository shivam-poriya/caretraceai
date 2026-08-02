import React, { useState, useEffect } from 'react';
import { doctorAPI } from '../../api/api';
import { IconSearch, IconAlert } from '../../components/Icons';

export const DoctorPatients = ({ onSelectPatient }) => {
  const [patients, setPatients] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTab, setFilterTab] = useState('All');
  const [loading, setLoading] = useState(true);

  const fetchPatients = async (query = '') => {
    setLoading(true);
    try {
      let data;
      if (query.trim()) {
        data = await doctorAPI.searchPatients(query);
      } else {
        data = await doctorAPI.getPatients();
      }
      setPatients(data || []);
    } catch (err) {
      console.error('Failed to fetch patient list:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients(searchQuery);
  }, [searchQuery]);

  const filteredPatients = patients.filter((p) => {
    if (filterTab === 'New updates') return p.change_count > 0;
    if (filterTab === 'Needs review') return p.has_safety_flag || p.change_count > 0;
    return true;
  });

  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Patients</h1>
          <p className="sub">Search and filter your assigned patient list.</p>
        </div>
      </div>

      {/* Search Input and Filters */}
      <div style={{ display: 'flex', gap: '14px', marginBottom: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <IconSearch
            size={18}
            style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--slate)' }}
          />
          <input
            type="text"
            placeholder="Search patients by name or username…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '11px 14px 11px 40px',
              border: '1px solid var(--line)',
              borderRadius: '100px',
              fontSize: '14px',
            }}
          />
        </div>

        <div className="tl-filters" style={{ margin: 0 }}>
          {['All', 'New updates', 'Needs review'].map((tab) => (
            <button
              key={tab}
              className={`chip ${filterTab === tab ? 'active' : ''}`}
              onClick={() => setFilterTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Patient Table */}
      <div className="card" style={{ overflowX: 'auto' }}>
        <table className="p-table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Contact / Demographics</th>
              <th>Last Update</th>
              <th>Status &amp; Badges</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '30px', color: 'var(--slate)' }}>
                  Loading patient list...
                </td>
              </tr>
            ) : filteredPatients.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '30px', color: 'var(--slate)' }}>
                  No matching patients found.
                </td>
              </tr>
            ) : (
              filteredPatients.map((p) => (
                <tr key={p.patient_id}>
                  <td>
                    <div className="p-name" style={{ fontSize: '15px', color: 'var(--teal-900)' }}>
                      {p.name}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--slate-light)', fontFamily: 'var(--font-mono)' }}>
                      ID #{p.patient_id} (@{p.username})
                    </div>
                  </td>

                  <td style={{ fontSize: '13.5px', color: 'var(--slate)' }}>
                    {p.gender || 'N/A'} {p.blood_group ? `· Blood: ${p.blood_group}` : ''}
                    <br />
                    Phone: {p.phone || 'N/A'}
                  </td>

                  <td style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>
                    {p.last_update ? new Date(p.last_update).toLocaleDateString() : 'None'}
                  </td>

                  <td>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {p.has_safety_flag && (
                        <span className="badge badge-critical">
                          <IconAlert size={12} /> Red Flag
                        </span>
                      )}
                      {p.change_count > 0 ? (
                        <span className="badge badge-updated">
                          ↻ {p.change_count} Change{p.change_count > 1 ? 's' : ''}
                        </span>
                      ) : (
                        <span className="badge badge-patient">Reviewed</span>
                      )}
                    </div>
                  </td>

                  <td>
                    <button className="btn btn-primary btn-sm" onClick={() => onSelectPatient(p.patient_id)}>
                      Review Record
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
