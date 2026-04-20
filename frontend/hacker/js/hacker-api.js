/* ═══════════════════════════════════════════════════════════
   PHANTOM — Hacker API Client (JWT Authenticated)
   ═══════════════════════════════════════════════════════════ */

const HACKER_API = window.location.port === '8000' || window.location.port === ''
  ? `${window.location.protocol}//${window.location.hostname}${window.location.port ? ':' + window.location.port : ''}`
  : 'http://localhost:8000';

class HackerAPI {
  static getToken() {
    return localStorage.getItem('phantom_token') || '';
  }

  static isLoggedIn() {
    return !!this.getToken();
  }

  static logout() {
    localStorage.removeItem('phantom_token');
    localStorage.removeItem('phantom_user');
    window.location.href = 'login.html';
  }

  static async fetch(url, options = {}) {
    const token = this.getToken();
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 15000);

    try {
      const res = await fetch(`${HACKER_API}${url}`, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...(options.headers || {}),
        },
      });
      clearTimeout(id);

      if (res.status === 401 || res.status === 403) {
        this.logout();
        throw new Error('Unauthorized — please login again');
      }

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    } catch (err) {
      clearTimeout(id);
      if (err.name === 'AbortError') throw new Error('Timed out');
      throw err;
    }
  }

  static launchPreset(type) {
    return this.fetch(`/api/attack/preset/${type}`, { method: 'POST' });
  }

  static launchCustom(config) {
    return this.fetch('/api/attack/custom', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  static getPresets() {
    return this.fetch('/api/attack/presets');
  }

  static getLogs() {
    return this.fetch('/api/attack/logs');
  }

  static resetAll() {
    return this.fetch('/simulate/reset', { method: 'POST' });
  }

  static healthCheck() {
    return this.fetch('/health');
  }
}
