const STORAGE_KEY = 'papertrail_records';
const API_BASE = 'http://127.0.0.1:8000';

export function buildAbsoluteMediaUrl(url) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  return `${API_BASE}${url}`;
}

export function readRecords() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveRecord(record) {
  const nextRecord = {
    ...record,
    image_url: buildAbsoluteMediaUrl(record.image_url),
  };
  const existing = readRecords().filter((item) => item.id !== nextRecord.id);
  const next = [nextRecord, ...existing].slice(0, 20);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return nextRecord;
}

export function findRecord(recordId) {
  return readRecords().find((item) => item.id === recordId) || null;
}

export function getLatestRecord() {
  return readRecords()[0] || null;
}

export function updateStoredRecord(recordId, updates) {
  const records = readRecords();
  const next = records.map((item) => (item.id === recordId ? { ...item, ...updates } : item));
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next.find((item) => item.id === recordId) || null;
}
