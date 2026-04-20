/* ═══════════════════════════════════════════════════════════
   Exposys Mart Admin — Authentication
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  const isLoginPage = !!document.getElementById('login-form');
  const isDashboard = !!document.getElementById('entropy-chart');

  if (isLoginPage) {
    // If already logged in, redirect to dashboard
    if (localStorage.getItem('shopzone_admin_token')) {
      window.location.href = 'dashboard.html';
      return;
    }
    initLoginForm();
  }

  if (isDashboard) {
    // If not logged in, redirect to login
    if (!localStorage.getItem('shopzone_admin_token')) {
      window.location.href = 'login.html';
      return;
    }
    initLogout();
  }
});

function initLoginForm() {
  const form = document.getElementById('login-form');
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errEl.classList.remove('visible');

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    btn.disabled = true;
    btn.textContent = '⏳ Signing in...';

    try {
      const res = await AdminAPI.login(username, password);

      if (res.success && res.token) {
        localStorage.setItem('shopzone_admin_token', res.token);
        window.location.href = 'dashboard.html';
      } else {
        errEl.textContent = res.message || 'Invalid credentials';
        errEl.classList.add('visible');
      }
    } catch (err) {
      errEl.textContent = err?.message || 'Server connection failed. Is the backend running?';
      errEl.classList.add('visible');
    } finally {
      btn.disabled = false;
      btn.textContent = '🔐 Sign In';
    }
  });
}

function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (btn) {
    btn.addEventListener('click', () => {
      localStorage.removeItem('shopzone_admin_token');
      window.location.href = 'login.html';
    });
  }
}
