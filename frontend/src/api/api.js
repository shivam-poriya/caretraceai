import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT Bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const authAPI = {
  testAuth: async () => {
    const response = await api.get('/v1/custom-auth/test');
    return response.data;
  },
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/v1/custom-auth/login/', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },
  register: async (userData) => {
    const response = await api.post('/v1/custom-auth/register/', userData);
    return response.data;
  },
  getUserProfile: async () => {
    const response = await api.get('/v1/custom-auth/get-user-profile/');
    return response.data;
  },
  forgotPassword: async (email) => {
    const response = await api.post('/v1/custom-auth/forgot-password/', { email });
    return response.data;
  },
  verifyOTP: async (email, otp) => {
    const response = await api.post('/v1/custom-auth/verify-otp/', { email, otp });
    return response.data;
  },
  resetPassword: async (email, otp, new_password) => {
    const response = await api.post('/v1/custom-auth/reset-password/', {
      email,
      otp,
      new_password,
    });
    return response.data;
  },
};

export const patientAPI = {
  getProfile: async () => {
    const response = await api.get('/v1/patient/profile/');
    return response.data;
  },
  updateProfile: async (data) => {
    const response = await api.put('/v1/patient/profile/', data);
    return response.data;
  },
  getResumePrompt: async () => {
    const response = await api.get('/v1/patient/resume-prompt/');
    return response.data;
  },
  quickUpdate: async (chipType, symptomId = null, note = '') => {
    const response = await api.post('/v1/patient/quick-update/', {
      chip_type: chipType,
      symptom_id: symptomId,
      note: note,
    });
    return response.data;
  },
  getSymptoms: async () => {
    const response = await api.get('/v1/patient/symptoms/');
    return response.data;
  },
  createSymptom: async (symptomData) => {
    const response = await api.post('/v1/patient/symptoms/', symptomData);
    return response.data;
  },
  updateSymptom: async (symptomId, symptomData) => {
    const response = await api.put(`/v1/patient/symptoms/${symptomId}/`, symptomData);
    return response.data;
  },
  getAllergies: async () => {
    const response = await api.get('/v1/patient/allergies/');
    return response.data;
  },
  createAllergy: async (allergyData) => {
    const response = await api.post('/v1/patient/allergies/', allergyData);
    return response.data;
  },
  getMedicalHistory: async () => {
    const response = await api.get('/v1/patient/medical-history/');
    return response.data;
  },
  createMedicalHistory: async (historyData) => {
    const response = await api.post('/v1/patient/medical-history/', historyData);
    return response.data;
  },
  getMedications: async () => {
    const response = await api.get('/v1/patient/medications/');
    return response.data;
  },
  createMedication: async (medData) => {
    const response = await api.post('/v1/patient/medications/', medData);
    return response.data;
  },
  uploadAttachment: async (file, description = '') => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) formData.append('description', description);
    const response = await api.post('/v1/patient/attachments/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  getAttachments: async () => {
    const response = await api.get('/v1/patient/attachments/');
    return response.data;
  },
  getQueuedQuestions: async () => {
    const response = await api.get('/v1/patient/queued-questions/');
    return response.data;
  },
  getDoctorViewPreview: async () => {
    const response = await api.get('/v1/patient/doctor-view-preview/');
    return response.data;
  },
  getTimeline: async (category = '', days = 30) => {
    let url = `/v1/patient/timeline/?days=${days}`;
    if (category && category !== 'All') {
      url += `&category=${category}`;
    }
    const response = await api.get(url);
    return response.data;
  },
};

export const intakeAPI = {
  startSession: async () => {
    const response = await api.post('/v1/intake/sessions/');
    return response.data;
  },
  getSessions: async () => {
    const response = await api.get('/v1/intake/sessions/');
    return response.data;
  },
  getSessionDetails: async (sessionId) => {
    const response = await api.get(`/v1/intake/sessions/${sessionId}/`);
    return response.data;
  },
  sendMessage: async (sessionId, message, action = null, skipField = null) => {
    const response = await api.post(`/v1/intake/sessions/${sessionId}/message/`, {
      message,
      action,
      skip_field: skipField,
    });
    return response.data;
  },
  confirmExtraction: async (sessionId, action, notes = '') => {
    const response = await api.post(
      `/v1/intake/sessions/${sessionId}/confirm-extraction/`,
      { action, notes }
    );
    return response.data;
  },
  skipField: async (sessionId, fieldName) => {
    const response = await api.post(`/v1/intake/sessions/${sessionId}/skip-field/`, {
      field_name: fieldName,
    });
    return response.data;
  },
  getMessages: async (sessionId) => {
    const response = await api.get(`/v1/intake/sessions/${sessionId}/messages/`);
    return response.data;
  },
  endSession: async (sessionId) => {
    const response = await api.post(`/v1/intake/sessions/${sessionId}/end/`);
    return response.data;
  },
};

export const doctorAPI = {
  getPatients: async () => {
    const response = await api.get('/v1/doctor/patients/');
    return response.data;
  },
  searchPatients: async (query) => {
    const response = await api.get(`/v1/doctor/patients/search/?q=${encodeURIComponent(query)}`);
    return response.data;
  },
  getPatientOverview: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/overview/`);
    return response.data;
  },
  getPatientTimeline: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/timeline/`);
    return response.data;
  },
  markReviewed: async (patientId, note = '') => {
    const response = await api.post(`/v1/doctor/patients/${patientId}/mark-reviewed/`, { note });
    return response.data;
  },
  getWhatChanged: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/what-changed/`);
    return response.data;
  },
  getIntakeSummary: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/intake-summary/`);
    return response.data;
  },
  queueQuestion: async (patientId, questionText) => {
    const response = await api.post(`/v1/doctor/patients/${patientId}/queue-question/`, {
      question_text: questionText,
    });
    return response.data;
  },
  exportBrief: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/export-brief/`);
    return response.data;
  },
  getPatientAttachments: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/attachments/`);
    return response.data;
  },
  getPatientConversations: async (patientId) => {
    const response = await api.get(`/v1/doctor/patients/${patientId}/conversations/`);
    return response.data;
  },
  saveClinicalAssessment: async (patientId, data) => {
    const response = await api.post(
      `/v1/doctor/patients/${patientId}/clinical-assessment/`,
      data
    );
    return response.data;
  },
  savePrescription: async (patientId, data) => {
    const response = await api.post(
      `/v1/doctor/patients/${patientId}/prescription/`,
      data
    );
    return response.data;
  },
  saveNotes: async (patientId, data) => {
    const response = await api.post(
      `/v1/doctor/patients/${patientId}/notes/`,
      data
    );
    return response.data;
  },
};

export default api;
