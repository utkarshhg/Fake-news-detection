
const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('token');
}

export function setToken(token) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('user'));
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.href = '/';
    throw new Error('Session expired');
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));

    let message = `Request failed (${res.status})`;

    if (typeof body.detail === 'string') {
      message = body.detail;
    } else if (Array.isArray(body.detail)) {
      message = body.detail
        .map((item) => item.msg || JSON.stringify(item))
        .join(', ');
    } else if (body.detail) {
      message = JSON.stringify(body.detail);
    } else if (body.message) {
      message = body.message;
    } else if (body.error) {
      message = body.error;
    }

    throw new Error(message);
  }

  return res.json();
}

export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export function register(username, email, password, role) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password, role }),
  });
}

export function analyzeArticle(text, url, modelName) {
  return request('/analyze', {
    method: 'POST',
    body: JSON.stringify({ text, url, model_name: modelName }),
  });
}

export function getDashboardStats() {
  return request('/dashboard/stats');
}

export function getHistory(limit = 50, riskLevel, language) {
  const params = new URLSearchParams({ limit });
  if (riskLevel && riskLevel !== 'All') params.set('risk_level', riskLevel);
  if (language && language !== 'All') params.set('language', language);
  return request(`/history?${params}`);
}

export function getHistoryDetail(id) {
  return request(`/history/${id}`);
}

export function getAdminUsers() {
  return request('/admin/users');
}

export function updateUserRole(userId, role) {
  return request(`/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  });
}

export function toggleUserActive(userId) {
  return request(`/admin/users/${userId}/toggle`, { method: 'PUT' });
}

export function getAdminMetrics() {
  return request('/admin/metrics');
}

export function getAdminFlagged(statusFilter) {
  const params = new URLSearchParams();
  if (statusFilter && statusFilter !== 'All') params.set('status_filter', statusFilter);
  return request(`/admin/flagged?${params}`);
}

export function reviewFlag(flagId, status, notes = '') {
  return request(`/admin/flagged/${flagId}`, {
    method: 'PUT',
    body: JSON.stringify({ status, notes }),
  });
}
