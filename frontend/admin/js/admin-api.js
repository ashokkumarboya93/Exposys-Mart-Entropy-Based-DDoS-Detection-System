/* ═══════════════════════════════════════════════════════════
   Exposys Mart Admin — API Client (Authenticated)
   ═══════════════════════════════════════════════════════════ */

const _isLocal = window.location.protocol === 'file:';
const ADMIN_API_BASE = (_isLocal || window.location.port === '8000')
  ? 'http://127.0.0.1:8000'
  : `${window.location.protocol}//${window.location.hostname}:8000`;

class AdminAPI {
  static getToken() {
    return localStorage.getItem('shopzone_admin_token') || '';
  }

  static async _tryParseJson(response) {
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) return null;
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  static async fetch(url, options = {}) {
    const token = this.getToken();
    const res = await fetch(`${ADMIN_API_BASE}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...(options.headers || {}),
      },
    });

    if (res.status === 401 || res.status === 403) {
      localStorage.removeItem('shopzone_admin_token');
      window.location.href = 'login.html';
      throw new Error('Unauthorized');
    }

    const payload = await this._tryParseJson(res);
    if (!res.ok) {
      const errorDetail = payload?.detail || payload?.message || `HTTP ${res.status}`;
      throw new Error(errorDetail);
    }
    return payload || {};
  }

  static async login(username, password) {
    const res = await fetch(`${ADMIN_API_BASE}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    const payload = await this._tryParseJson(res);
    if (!res.ok) {
      return {
        success: false,
        message: payload?.detail || payload?.message || 'Invalid credentials',
      };
    }
    return payload || { success: false, message: 'Login failed' };
  }

  static getAnalytics() {
    return this.fetch('/api/admin/analytics');
  }

  static getEntropyHistory(limit = 100) {
    return this.fetch(`/api/admin/entropy-history?limit=${limit}`);
  }

  static getLogs(limit = 100, type = null) {
    const qs = type ? `&traffic_type=${type}` : '';
    return this.fetch(`/api/admin/logs?limit=${limit}${qs}`);
  }

  static getReport() {
    return this.fetch('/api/admin/report');
  }

  static resetAnalytics() {
    return this.fetch('/api/admin/reset-analytics', { method: 'POST' });
  }

  static blockIP(ip) {
    return this.fetch(`/api/admin/ip/${ip}/block`, { method: 'POST' });
  }

  static unblockIP(ip) {
    return this.fetch(`/api/admin/ip/${ip}/unblock`, { method: 'POST' });
  }

  static getBlockedIPs() {
    return this.fetch('/api/admin/blocked-ips');
  }
}
