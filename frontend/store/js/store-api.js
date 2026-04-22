/* ═══════════════════════════════════════════════════════════
   Exposys Mart — Store API + Utilities
   ═══════════════════════════════════════════════════════════ */

const _isLocal = window.location.protocol === 'file:';
const API_BASE = _isLocal ? 'http://127.0.0.1:8000' : `${window.location.protocol}//${window.location.hostname}:8000`;

class StoreAPI {
  static getToken() {
    return localStorage.getItem('store_token') || '';
  }

  static isLoggedIn() {
    return !!this.getToken();
  }

  static getUser() {
    try { return JSON.parse(localStorage.getItem('store_user') || 'null'); } catch { return null; }
  }

  static logout() {
    localStorage.removeItem('store_token');
    localStorage.removeItem('store_user');
    window.location.href = 'auth.html';
  }

  static async fetch(url, options = {}) {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), 9000);
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    const token = this.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const res = await fetch(`${API_BASE}${url}`, {
        ...options,
        signal: ctrl.signal,
        headers,
      });
      clearTimeout(id);
      if (res.status === 401 && token) {
        // Token expired or invalid — clear it but don't force redirect for browsing
        // Only redirect if they were doing an action that requires auth
        return null;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      clearTimeout(id);
      throw e;
    }
  }

  static getProducts(category) {
    const q = category && category !== 'all' ? `?category=${category}` : '';
    return this.fetch(`/api/store/products${q}`);
  }
  static getProduct(id) { return this.fetch(`/api/store/products/${id}`); }
  static getCategories() { return this.fetch('/api/store/categories'); }
  static trackInteraction(data) {
    return this.fetch('/api/store/track', {
      method: 'POST',
      body: JSON.stringify({
        session_id: getSessionId(),
        page: data.page || 'homepage',
        action: data.action || 'pageview',
        product_id: data.product_id || null,
        search_query: data.search_query || null,
        category: data.category || null,
      }),
    });
  }
}

/* ── Session ──────────────────────────────────────────── */
function getSessionId() {
  let sid = localStorage.getItem('sz_session');
  if (!sid) {
    sid = 'sz_' + Date.now().toString(36) + Math.random().toString(36).slice(2);
    localStorage.setItem('sz_session', sid);
  }
  return sid;
}

/* ── Update Nav Account State ─────────────────────────── */
function updateNavAuth() {
  const link = document.getElementById('nav-account-link');
  const text = document.getElementById('nav-account-text');
  const logoutBtn = document.getElementById('nav-logout-btn');

  if (StoreAPI.isLoggedIn()) {
    const user = StoreAPI.getUser();
    if (text) text.textContent = user?.username || 'Account';
    if (link) link.href = 'profile.html';
    if (logoutBtn) logoutBtn.style.display = 'flex';
  } else {
    if (text) text.textContent = 'Login';
    if (link) link.href = 'auth.html';
    if (logoutBtn) logoutBtn.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', updateNavAuth);

/* ── Traffic Counter ──────────────────────────────────── */
let _traffic = parseInt(localStorage.getItem('sz_traffic') || '0');

function updateTraffic(n) {
  _traffic += n;
  localStorage.setItem('sz_traffic', _traffic);
}



async function track(page, action, productId, searchQuery, category) {
  try {
    const r = await StoreAPI.trackInteraction({ page, action, product_id: productId, search_query: searchQuery, category });
    if (r.traffic_generated) updateTraffic(r.traffic_generated);
  } catch { /* silent */ }
}

/* ── Toast ────────────────────────────────────────────── */
const ICONS = {
  success: `<svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  error:   `<svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
  info:    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

function showToast(msg, type = 'success') {
  const stack = document.getElementById('toast-stack');
  if (!stack) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span class="toast-icon">${ICONS[type] || ICONS.info}</span><span class="toast-msg">${msg}</span><button class="toast-close" onclick="this.parentElement.remove()">×</button>`;
  stack.appendChild(t);
  setTimeout(() => t.remove(), 4500);
}

/* ── Stars helper ─────────────────────────────────────── */
function renderStars(rating) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  const star = `<svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
  const halfStar = `<svg viewBox="0 0 24 24" style="opacity:.6"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
  const emptyStar = `<svg viewBox="0 0 24 24" class="empty"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
  return star.repeat(full) + (half ? halfStar : '') + emptyStar.repeat(empty);
}

/* ── Badge helper ─────────────────────────────────────── */
function badgeClass(badge) {
  const b = badge.toLowerCase();
  if (['deal','sale'].includes(b)) return 'p-badge-sale';
  if (['new','trending','hot'].includes(b)) return 'p-badge-new';
  if (['bestseller','#1 best','popular'].includes(b)) return 'p-badge-top';
  return 'p-badge-hot';
}
