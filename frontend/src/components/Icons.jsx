import React from 'react';

export const LogoMark = ({ className = "logo-mark" }) => (
  <svg className={className} viewBox="0 0 30 30" fill="none">
    <path
      d="M4 21c3-1 4-4 6-4s2 5 5 5 2-9 6-9 3 6 5 6"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const IconHome = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path
      d="M4 11l8-7 8 7v9a1 1 0 01-1 1h-4v-6H9v6H5a1 1 0 01-1-1v-9z"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
  </svg>
);

export const IconInfo = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path d="M12 11v6M12 8v.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const IconChat = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path
      d="M4 5h16v11H8l-4 4V5z"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
  </svg>
);

export const IconClock = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path d="M12 7v5l3 3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const IconUser = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="12" cy="8" r="3.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path
      d="M5 20c1-4 4.5-6 7-6s6 2 7 6"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

export const IconUsers = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="9" cy="8" r="3" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <circle cx="17" cy="9" r="2.4" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path
      d="M3 19c.6-3 3-5 6-5s5.4 2 6 5M14 14c2.4.2 4.4 1.8 5 4.5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

export const IconLock = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path d="M8 10V7a4 4 0 018 0v3" fill="none" stroke="currentColor" strokeWidth="1.8" />
  </svg>
);

export const IconShield = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path
      d="M12 3l7 3v6c0 5-3 8-7 9-4-1-7-4-7-9V6l7-3z"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
  </svg>
);

export const IconGrid = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <rect x="4" y="4" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <rect x="13" y="4" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <rect x="4" y="13" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <rect x="13" y="13" width="7" height="7" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
  </svg>
);

export const IconNote = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path d="M6 3h9l5 5v13H6V3z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    <path d="M9 12h6M9 16h6M9 8h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const IconSearch = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path d="M20 20l-4.5-4.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const IconMic = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <rect x="9" y="3" width="6" height="11" rx="3" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path d="M6 11a6 6 0 0012 0M12 17v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const IconSend = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path d="M4 12l16-8-6 16-2.5-7L4 12z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
  </svg>
);

export const IconPlus = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

export const IconCheck = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path d="M5 12l5 5L19 7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const IconAlert = ({ size = 18, className = "" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" className={className}>
    <path d="M12 3l10 18H2L12 3z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    <path d="M12 9v5M12 17v.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);
