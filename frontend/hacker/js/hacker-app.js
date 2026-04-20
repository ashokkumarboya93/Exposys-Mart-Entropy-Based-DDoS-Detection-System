/* ═══════════════════════════════════════════════════════════
   PHANTOM — Hacker Application Logic v2
   Web3 Dark Theme • Attack Animations • Counter Effects
   ═══════════════════════════════════════════════════════════ */

const attackLogs = [];
let totalAttacksLaunched = 0;
let totalRequestsSent = 0;

document.addEventListener('DOMContentLoaded', () => {
  // ── Auth Gate (double-check after inline head gate) ────
  if (!HackerAPI.isLoggedIn()) {
    window.location.replace('login.html');
    return;
  }

  // Reveal page with fade-in
  document.body.classList.add('authenticated');

  checkTarget();
  initPresets();
  initCustomAttack();
  initActions();
  loadExistingLogs();
  initSmoothScroll();
});

// ── Smooth Scroll for Anchor Links ───────────────────────
function initSmoothScroll() {
  document.querySelectorAll('.nav-links a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

// ── Animated Counter ─────────────────────────────────────
function animateCounter(element, endValue, duration = 800, prefix = '', suffix = '') {
  const startValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(startValue + (endValue - startValue) * eased);
    element.textContent = prefix + current.toLocaleString() + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      // Pop animation
      element.style.transform = 'scale(1.15)';
      setTimeout(() => { element.style.transform = 'scale(1)'; }, 150);
    }
  }

  requestAnimationFrame(update);
}

// ── Update Stats Bar ─────────────────────────────────────
function updateStatsBar() {
  const attacksEl = document.getElementById('stat-attacks-count');
  const reqsEl = document.getElementById('stat-total-reqs');

  if (attacksEl) animateCounter(attacksEl, totalAttacksLaunched);
  if (reqsEl) animateCounter(reqsEl, totalRequestsSent);
}

// ── Target Health Check ──────────────────────────────────
async function checkTarget() {
  const statusEl = document.getElementById('stat-status');
  const badgeEl = document.getElementById('target-status-text');
  try {
    await HackerAPI.healthCheck();
    if (statusEl) statusEl.innerHTML = '<span style="color: var(--green);">ONLINE</span>';
    if (badgeEl) { badgeEl.textContent = 'ONLINE'; badgeEl.style.color = 'var(--green)'; }
  } catch {
    if (statusEl) statusEl.innerHTML = '<span style="color: var(--red);">OFFLINE</span>';
    if (badgeEl) { badgeEl.textContent = 'OFFLINE'; badgeEl.style.color = 'var(--red)'; }
  }
}

// ── Attack Animation ─────────────────────────────────────
function showAttackAnimation() {
  const overlay = document.getElementById('attack-overlay');
  if (!overlay) return;

  overlay.classList.add('active');

  // Add grid flash lines
  for (let i = 0; i < 6; i++) {
    const line = document.createElement('div');
    line.className = `attack-grid-line ${Math.random() > 0.5 ? 'h' : 'v'}`;
    line.style.cssText = Math.random() > 0.5
      ? `top: ${Math.random() * 100}%; animation-delay: ${i * 0.1}s;`
      : `left: ${Math.random() * 100}%; animation-delay: ${i * 0.1}s;`;
    overlay.appendChild(line);
  }

  // Screen flash
  document.body.style.transition = 'background 0.1s';
  document.body.style.background = '#1a0000';
  setTimeout(() => { document.body.style.background = '#000000'; }, 100);

  setTimeout(() => {
    overlay.classList.remove('active');
    overlay.querySelectorAll('.attack-grid-line').forEach(l => l.remove());
  }, 2000);
}

// ── Preset Attacks ───────────────────────────────────────
function initPresets() {
  document.querySelectorAll('.launch-btn[data-preset]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const preset = btn.dataset.preset;
      await launchAttack('preset', preset, btn);
    });
  });
}

async function launchAttack(type, presetOrConfig, btn) {
  const originalHTML = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;animation:spin 1s linear infinite"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg> ATTACKING...`;

  // Add CSS spin animation
  const styleEl = document.createElement('style');
  styleEl.textContent = '@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}';
  document.head.appendChild(styleEl);

  showAttackAnimation();
  addLog('pending', `Initiating ${type === 'preset' ? presetOrConfig.toUpperCase() : 'CUSTOM'} attack sequence...`, '...');

  try {
    let result;
    if (type === 'preset') {
      result = await HackerAPI.launchPreset(presetOrConfig);
    } else {
      result = await HackerAPI.launchCustom(presetOrConfig);
    }

    totalAttacksLaunched++;
    totalRequestsSent += result.total_requests;
    updateStatsBar();

    const msg = `${result.preset_type.toUpperCase()} complete — ${result.num_ips} IPs × ${result.waves_completed} wave(s) = ${result.total_requests.toLocaleString()} requests`;
    addLog('success', msg, result.total_requests.toLocaleString());

    showStatus(
      true,
      `Attack Completed: ${result.preset_type.toUpperCase()}`,
      `Attack ID: ${result.attack_id.substring(0, 12)}...\n` +
      `Source IPs: ${result.num_ips} (rotating subnets)\n` +
      `Total Requests: ${result.total_requests.toLocaleString()}\n` +
      `Waves Completed: ${result.waves_completed}\n` +
      `Duration: ${result.duration_ms}ms\n` +
      `IP Addresses: ${result.ips_used.slice(0, 5).join(', ')}${result.ips_used.length > 5 ? '...' : ''}`
    );

  } catch (err) {
    addLog('error', `Attack failed: ${err.message}`, '0');
    showStatus(false, 'Attack Failed', `Error: ${err.message}\n\nEnsure the backend is running on port 8000.`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHTML;
    styleEl.remove();
  }
}

// ── Custom Attack ────────────────────────────────────────
function initCustomAttack() {
  const ipsInput = document.getElementById('custom-ips');
  const rpiInput = document.getElementById('custom-rpi');
  const wavesInput = document.getElementById('custom-waves');
  const delayInput = document.getElementById('custom-delay');

  function updateSummary() {
    const ips = parseInt(ipsInput.value) || 0;
    const rpi = parseInt(rpiInput.value) || 0;
    const waves = parseInt(wavesInput.value) || 1;
    const delay = parseInt(delayInput.value) || 0;

    const total = ips * rpi * waves;
    const duration = (waves - 1) * delay / 1000;

    const totalEl = document.getElementById('custom-total');
    const durationEl = document.getElementById('custom-duration');

    if (totalEl) animateCounter(totalEl, total, 300);
    if (durationEl) durationEl.textContent = `~${duration.toFixed(1)}s`;
  }

  [ipsInput, rpiInput, wavesInput, delayInput].forEach(input => {
    if (input) input.addEventListener('input', updateSummary);
  });

  document.getElementById('custom-launch-btn')?.addEventListener('click', async () => {
    const config = {
      num_ips: parseInt(ipsInput.value) || 5,
      requests_per_ip: parseInt(rpiInput.value) || 300,
      waves: parseInt(wavesInput.value) || 1,
      wave_delay_ms: parseInt(delayInput.value) || 0,
    };

    const btn = document.getElementById('custom-launch-btn');
    await launchAttack('custom', config, btn);
  });
}

// ── Actions ──────────────────────────────────────────────
function initActions() {
  document.getElementById('reset-btn')?.addEventListener('click', async () => {
    const btn = document.getElementById('reset-btn');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    try {
      await HackerAPI.resetAll();
      addLog('success', 'All target data reset successfully', '—');
      showStatus(true, 'Reset Complete', 'All traffic data and detection state have been cleared on the target server.');
      totalAttacksLaunched = 0;
      totalRequestsSent = 0;
      updateStatsBar();
    } catch (err) {
      addLog('error', `Reset failed: ${err.message}`, '—');
    } finally {
      btn.disabled = false;
      btn.innerHTML = originalHTML;
    }
  });

  document.getElementById('clear-logs-btn')?.addEventListener('click', () => {
    attackLogs.length = 0;
    renderLogs();
  });
}

// ── Logging ──────────────────────────────────────────────
function addLog(type, message, count) {
  const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  attackLogs.unshift({ time, type, message, count });
  if (attackLogs.length > 50) attackLogs.pop();
  renderLogs();
}

function renderLogs() {
  const body = document.getElementById('logs-body');
  const empty = document.getElementById('logs-empty');
  if (!body) return;

  if (attackLogs.length === 0) {
    body.innerHTML = '';
    if (empty) { empty.style.display = 'block'; body.appendChild(empty); }
    return;
  }

  if (empty) empty.style.display = 'none';

  body.innerHTML = attackLogs.map(log => `
    <div class="log-entry">
      <span class="log-time">${log.time}</span>
      <span class="log-type ${log.type}">${log.type.toUpperCase()}</span>
      <span class="log-message">${log.message}</span>
      <span class="log-count">${log.count}</span>
    </div>
  `).join('');
}

async function loadExistingLogs() {
  try {
    const data = await HackerAPI.getLogs();
    const logs = data.data?.logs || data.logs || [];
    if (logs.length > 0) {
      logs.slice(0, 10).forEach(log => {
        const time = log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '--:--';
        attackLogs.push({
          time,
          type: log.status === 'completed' ? 'success' : 'error',
          message: `${log.preset_type.toUpperCase()} — ${log.num_ips} IPs, ${log.total_requests.toLocaleString()} reqs`,
          count: log.total_requests.toLocaleString(),
        });
        totalAttacksLaunched++;
        totalRequestsSent += log.total_requests;
      });
      renderLogs();
      updateStatsBar();
    }
  } catch { /* ignore */ }
}

// ── Status Feedback ──────────────────────────────────────
function showStatus(success, title, detail) {
  const el = document.getElementById('attack-status');
  const titleEl = document.getElementById('status-title');
  const detailEl = document.getElementById('status-detail');
  if (!el) return;

  el.className = `attack-status visible ${success ? 'success' : 'error'}`;

  const icon = success
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2" style="width:18px;height:18px"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="var(--red)" stroke-width="2" style="width:18px;height:18px"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>';

  titleEl.innerHTML = icon + ' ' + title;
  titleEl.style.color = success ? 'var(--green)' : 'var(--red)';
  detailEl.textContent = detail;

  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
