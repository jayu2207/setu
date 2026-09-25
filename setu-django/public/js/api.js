/* =========================================================
   API HELPER + AUTH UTILITIES (shared across all pages)
   ========================================================= */

const API_BASE = '/api';

function getToken() { return localStorage.getItem('sap_token'); }
function getUser() {
  const raw = localStorage.getItem('sap_user');
  return raw ? JSON.parse(raw) : null;
}
function setSession(token, user) {
  localStorage.setItem('sap_token', token);
  localStorage.setItem('sap_user', JSON.stringify(user));
}
function clearSession() {
  localStorage.removeItem('sap_token');
  localStorage.removeItem('sap_user');
}
function logout() {
  clearSession();
  window.location.href = '/index.html';
}

/** Redirect to login if not authenticated; optionally enforce a role. */
function requireAuth(role) {
  const user = getUser();
  const token = getToken();
  if (!user || !token) {
    window.location.href = '/login.html';
    return null;
  }
  if (role && user.role !== role) {
    window.location.href = `/${user.role}-dashboard.html`;
    return null;
  }
  return user;
}

/** Core fetch wrapper — attaches JWT, parses JSON, throws readable errors. */
async function apiRequest(path, { method = 'GET', body = null } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(API_BASE + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new Error('Cannot reach the server. Please check your connection and try again.');
  }

  let data = {};
  try { data = await res.json(); } catch (_) { /* no body */ }

  if (res.status === 401 || res.status === 403) {
    if (data.error && data.error.toLowerCase().includes('token')) {
      clearSession();
      window.location.href = '/login.html';
      return;
    }
  }

  if (!res.ok) {
    throw new Error(data.error || 'Something went wrong. Please try again.');
  }
  return data;
}

const api = {
  get: (path) => apiRequest(path),
  post: (path, body) => apiRequest(path, { method: 'POST', body }),
  put: (path, body) => apiRequest(path, { method: 'PUT', body }),
  del: (path) => apiRequest(path, { method: 'DELETE' }),
};

/* ---------- Toasts ---------- */
function toast(message, type = 'success') {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'toast-wrap';
    document.body.appendChild(wrap);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = message;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3800);
}

/* ---------- Small helpers ---------- */
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}
function initials(name) {
  if (!name) return '?';
  return name.trim().split(/\s+/).slice(0, 2).map((w) => w[0].toUpperCase()).join('');
}
function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
function showSection(id, navEl) {
  document.querySelectorAll('.section').forEach((s) => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  document.querySelectorAll('.side-nav a').forEach((a) => a.classList.remove('active'));
  if (navEl) navEl.classList.add('active');
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) sidebar.classList.remove('open');
}
function toggleSidebar() {
  document.querySelector('.sidebar').classList.toggle('open');
}
