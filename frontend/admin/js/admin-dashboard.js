/* ═══════════════════════════════════════════════════════════
   Exposys Mart Admin — Dashboard Logic (Charts + Auto-refresh)
   ═══════════════════════════════════════════════════════════ */

let entropyChart = null;
let trafficTypeChart = null;
let distributionChart = null;
let topRoutesChart = null;
let refreshInterval = null;
let isRefreshInProgress = false;

document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('entropy-chart')) return;
  if (!localStorage.getItem('shopzone_admin_token')) return;

  initCharts();
  fetchAndUpdate();
  refreshInterval = setInterval(fetchAndUpdate, 3000);
  window.addEventListener('beforeunload', () => {
    if (refreshInterval) clearInterval(refreshInterval);
  });

  // Download report
  document.getElementById('download-csv-btn')?.addEventListener('click', () => downloadFile('/api/admin/report/csv'));
  document.getElementById('download-pdf-btn')?.addEventListener('click', () => downloadFile('/api/admin/report/pdf'));

  // Reset Analytics
  document.getElementById('reset-analytics-btn')?.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to reset all analytics data? This will clear the attack history and reset the detection engine baseline.')) return;
    
    const btn = document.getElementById('reset-analytics-btn');
    const originalContent = btn.innerHTML;
    
    try {
      btn.disabled = true;
      btn.style.opacity = '0.7';
      btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:-2px"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Resetting...';
      
      await AdminAPI.resetAnalytics();
      
      // Clear UI state immediately for instant feedback
      document.getElementById('status-badge').className = 'status-badge status-unknown';
      document.getElementById('status-badge').innerHTML = 'RESETTING...';
      document.getElementById('message-bar').className = 'message-bar message-unknown';
      document.getElementById('message-text').textContent = 'System reset successful. Rebuilding baseline...';
      
      // Clear KPI values
      ['kpi-requests', 'kpi-shoppers', 'kpi-ips', 'kpi-entropy', 'kpi-confidence', 'kpi-suspicious'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = id === 'kpi-entropy' ? '—' : '0';
      });

      // Fetch data immediately to update the dashboard
      await fetchAndUpdate();
    } catch (err) {
      console.error('Reset error:', err);
      alert('Failed to reset analytics: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.innerHTML = originalContent;
    }
  });

  // Handle IP Blocking clicks
  document.addEventListener('click', async (e) => {
    const blockBtn = e.target.closest('.block-ip-btn');
    if (!blockBtn) return;

    const ip = blockBtn.dataset.ip;
    if (!ip) return;

    if (!confirm(`Are you sure you want to PERMANENTLY block IP: ${ip}? All future requests from this IP will be rejected with a 403 Forbidden.`)) return;

    try {
      blockBtn.disabled = true;
      blockBtn.innerHTML = '<span class="loading-spinner"></span>';
      
      const result = await AdminAPI.blockIP(ip);
      if (result.success) {
        await fetchAndUpdate();
      }
    } catch (err) {
      console.error('Block error:', err);
      alert('Failed to block IP: ' + err.message);
      blockBtn.disabled = false;
      blockBtn.innerHTML = 'Block';
    }
  });

  // Handle IP Unblocking clicks
  document.addEventListener('click', async (e) => {
    const unblockBtn = e.target.closest('.unblock-ip-btn');
    if (!unblockBtn) return;

    const ip = unblockBtn.dataset.ip;
    if (!ip) return;

    try {
      unblockBtn.disabled = true;
      unblockBtn.innerHTML = '<span class="loading-spinner"></span>';
      
      const result = await AdminAPI.unblockIP(ip);
      if (result.success) {
        await fetchAndUpdate();
      }
    } catch (err) {
      console.error('Unblock error:', err);
      alert('Failed to unblock IP: ' + err.message);
      unblockBtn.disabled = false;
      unblockBtn.innerHTML = 'Unblock';
    }
  });
});

// ── Chart Initialization ──────────────────────────────────
function initCharts() {
  const defaultFont = { family: "'Inter', sans-serif", size: 11 };
  Chart.defaults.font = defaultFont;

  // Entropy Trend
  const ctx1 = document.getElementById('entropy-chart').getContext('2d');
  entropyChart = new Chart(ctx1, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Entropy',
          data: [],
          borderColor: '#4F46E5',
          backgroundColor: 'rgba(79,70,229,0.08)',
          fill: true,
          tension: 0.4,
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 5,
        },
        {
          label: 'Threshold',
          data: [],
          borderColor: '#EF4444',
          borderDash: [6, 4],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
        },
        {
          label: 'Baseline',
          data: [],
          borderColor: '#10B981',
          borderDash: [3, 3],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, padding: 16 } },
        tooltip: {
          backgroundColor: 'rgba(26,29,46,0.95)',
          titleFont: { weight: '600' },
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 10, color: '#A1A5B7' } },
        y: { grid: { color: 'rgba(226,232,240,0.5)' }, ticks: { color: '#A1A5B7' } },
      },
    },
  });

  // Traffic Type Doughnut
  const ctx2 = document.getElementById('traffic-type-chart').getContext('2d');
  trafficTypeChart = new Chart(ctx2, {
    type: 'doughnut',
    data: {
      labels: ['Normal', 'Attack'],
      datasets: [{
        data: [1, 0],
        backgroundColor: ['#10B981', '#EF4444'],
        borderWidth: 0,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16 } },
        tooltip: {
          backgroundColor: 'rgba(26,29,46,0.95)',
          padding: 12,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `${ctx.label}: ${ctx.raw.toLocaleString()} requests`,
          },
        },
      },
    },
  });

  // Distribution Bar
  const ctx3 = document.getElementById('distribution-chart').getContext('2d');
  distributionChart = new Chart(ctx3, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Requests',
        data: [],
        backgroundColor: 'rgba(79,70,229,0.7)',
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(26,29,46,0.95)',
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#A1A5B7', maxRotation: 45 } },
        y: { grid: { color: 'rgba(226,232,240,0.5)' }, ticks: { color: '#A1A5B7' } },
      },
    },
  });

  // Top Routes Bar
  const ctx4 = document.getElementById('top-routes-chart').getContext('2d');
  topRoutesChart = new Chart(ctx4, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Hits',
        data: [],
        backgroundColor: 'rgba(239,68,68,0.7)',
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(26,29,46,0.95)',
          padding: 12,
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#A1A5B7' } },
        y: { grid: { color: 'rgba(226,232,240,0.5)' }, ticks: { color: '#A1A5B7' } },
      },
    },
  });
}

// ── Data Fetching & Update ────────────────────────────────
async function fetchAndUpdate() {
  if (isRefreshInProgress) return;
  isRefreshInProgress = true;

  try {
    const data = await AdminAPI.getAnalytics();
    updateKPIs(data || {});
    updateStatusBadge(data || {});
    updateMessageBar(data || {});
    updateEntropyChart(data || {});
    updateTrafficTypeChart(data || {});
    updateDistributionChart(data || {});
    updateTopRoutesChart(data || {});
    updateSuspiciousTable(data || {});
    updateAttacksTable(data || {});
    updateSessionsTable(data || {});
    updateLivePackets(data || {});
    
    // Fetch and update dedicated blocked table
    const blockedData = await AdminAPI.getBlockedIPs();
    updateBlockedTable(blockedData || {});
    
    updateRefreshTime();
  } catch (err) {
    console.error('Dashboard fetch error:', err);
  } finally {
    isRefreshInProgress = false;
  }
}

function updateKPIs(data) {
  const totalRequests = toNumber(data.total_requests);
  const activeShoppers = toNumber(data.active_shoppers);
  const uniqueIps = toNumber(data.unique_ips);
  const entropyScore = toNumber(data.entropy_score);
  const attackConfidence = toNumber(data.attack_confidence);
  const suspiciousCount = toArray(data.suspicious_ips).length;

  setText('kpi-requests', totalRequests.toLocaleString());
  setText('kpi-shoppers', activeShoppers.toString());
  setText('kpi-ips', uniqueIps.toString());
  setText('kpi-entropy', entropyScore.toFixed(4));
  setText('kpi-confidence', `${attackConfidence}%`);
  setText('kpi-suspicious', suspiciousCount.toString());
}

function updateStatusBadge(data) {
  const badge = document.getElementById('status-badge');
  if (!badge) return;

  const map = {
    'NORMAL': { cls: 'status-normal', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:-2px"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', text: 'NORMAL' },
    'DDOS_ATTACK': { cls: 'status-attack', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:-2px"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>', text: 'ATTACK DETECTED' },
    'INSUFFICIENT_DATA': { cls: 'status-unknown', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;vertical-align:-2px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>', text: 'BUILDING BASELINE' },
  };

  const info = map[data.status] || map['INSUFFICIENT_DATA'];
  badge.className = `status-badge ${info.cls}`;
  badge.innerHTML = `${info.icon} ${info.text}`;
}

function updateMessageBar(data) {
  const bar = document.getElementById('message-bar');
  const text = document.getElementById('message-text');
  if (!bar || !text) return;

  text.textContent = data.message || 'No analytics message available.';

  bar.className = 'message-bar';
  if (data.status === 'NORMAL') bar.classList.add('message-normal');
  else if (data.status === 'DDOS_ATTACK') bar.classList.add('message-attack');
  else bar.classList.add('message-unknown');
}

function updateEntropyChart(data) {
  if (!entropyChart) return;

  const history = toArray(data.entropy_history).slice(-40);
  const labels = history.map(h => toTimestampLabel(h.timestamp));

  entropyChart.data.labels = labels;
  entropyChart.data.datasets[0].data = history.map(h => toNumber(h.entropy));
  entropyChart.data.datasets[1].data = history.map(h => toNumber(h.threshold));
  entropyChart.data.datasets[2].data = history.map(h => toNumber(h.baseline));
  entropyChart.update('none');
}

function updateTrafficTypeChart(data) {
  if (!trafficTypeChart) return;

  const breakdown = data.normal_vs_attack || {};
  trafficTypeChart.data.datasets[0].data = [
    toNumber(breakdown.normal),
    toNumber(breakdown.attack),
  ];
  trafficTypeChart.update('none');
}

function updateDistributionChart(data) {
  if (!distributionChart) return;

  const dist = toArray(data.traffic_distribution).slice(0, 15);
  distributionChart.data.labels = dist.map(d => d.ip || 'Unknown');
  distributionChart.data.datasets[0].data = dist.map(d => toNumber(d.requests ?? d.count));

  // Color suspicious IPs in red
  const susIps = new Set(toArray(data.suspicious_ips).map(s => s.ip));
  distributionChart.data.datasets[0].backgroundColor = dist.map(d =>
    susIps.has(d.ip) ? 'rgba(239,68,68,0.7)' : 'rgba(79,70,229,0.7)'
  );

  distributionChart.update('none');
}

function updateTopRoutesChart(data) {
  if (!topRoutesChart) return;
  const routes = toArray(data.top_attacked_endpoints);

  topRoutesChart.data.labels = routes.map(r => r.endpoint || 'Unknown');
  topRoutesChart.data.datasets[0].data = routes.map(r => toNumber(r.total_requests));
  topRoutesChart.update('none');
}

function updateSuspiciousTable(data) {
  const tbody = document.getElementById('suspicious-tbody');
  const empty = document.getElementById('suspicious-empty');
  if (!tbody) return;

  const suspiciousIps = toArray(data.suspicious_ips);
  if (suspiciousIps.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = suspiciousIps.slice(0, 10).map((s, i) => {
    const riskScore = toNumber(s.risk_score);
    const risk = riskScore >= 70 ? 'high' : riskScore >= 40 ? 'medium' : 'low';
    const isBlocked = s.is_blocked || false;
    
    return `
      <tr>
        <td>${i + 1}</td>
        <td style="font-family: var(--font-mono); font-size: 0.78rem;">${escapeHtml(s.ip || '-')}</td>
        <td>${toNumber(s.requests).toLocaleString()}</td>
        <td><span class="risk-badge risk-${risk}">${risk.toUpperCase()}</span></td>
        <td>
          ${isBlocked 
            ? '<span class="status-pill blocked">Blocked</span>' 
            : `<button class="btn-action block-ip-btn" data-ip="${s.ip}" title="Blacklist this IP">Block</button>`}
        </td>
      </tr>
    `;
  }).join('');
}

function updateAttacksTable(data) {
  const tbody = document.getElementById('attacks-tbody');
  const empty = document.getElementById('attacks-empty');
  if (!tbody) return;

  const attackEvents = toArray(data.attack_events);
  if (attackEvents.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = attackEvents.slice(0, 10).map(a => {
    const time = a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : '--';
    return `
      <tr>
        <td style="font-size: 0.78rem;">${time}</td>
        <td><span class="type-badge type-attack">${escapeHtml(a.preset_type || '-')}</span></td>
        <td>${toNumber(a.num_ips)}</td>
        <td>${toNumber(a.total_requests).toLocaleString()}</td>
        <td style="color: var(--green); font-weight: 600;">${escapeHtml(a.status || '-')}</td>
      </tr>
    `;
  }).join('');
}

function updateSessionsTable(data) {
  const tbody = document.getElementById('sessions-tbody');
  const empty = document.getElementById('sessions-empty');
  if (!tbody) return;

  const sessions = toArray(data.recent_sessions);
  if (sessions.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = sessions.slice(0, 10).map(s => `
    <tr>
      <td style="font-family: var(--font-mono); font-size: 0.75rem;">${escapeHtml(s.session_id || '-')}</td>
      <td style="font-family: var(--font-mono); font-size: 0.75rem;">${escapeHtml(s.ip || '-')}</td>
      <td>${toNumber(s.pages_visited)}</td>
      <td>${toNumber(s.total_interactions)}</td>
      <td>${toNumber(s.duration_min)}m</td>
      <td><span class="type-badge ${s.is_active ? 'type-normal' : ''}">${s.is_active ? 'Active' : 'Ended'}</span></td>
    </tr>
  `).join('');
}

function updateRefreshTime() {
  const el = document.getElementById('last-refresh');
  if (el) el.textContent = new Date().toLocaleTimeString();
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function toArray(value) {
  return Array.isArray(value) ? value : [];
}

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function toTimestampLabel(timestamp) {
  if (!timestamp) return '--:--:--';
  const t = new Date(timestamp);
  if (Number.isNaN(t.getTime())) return '--:--:--';
  return t.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ── Report Download ───────────────────────────────────────
async function downloadFile(path) {
  try {
    const token = localStorage.getItem('shopzone_admin_token');
    const response = await fetch(`${ADMIN_API_BASE}${path}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    
    let filename = path.includes('csv') ? 'traffic_report.csv' : 'security_report.pdf';
    const disposition = response.headers.get('Content-Disposition');
    if (disposition && disposition.indexOf('filename=') !== -1) {
      const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
      const matches = filenameRegex.exec(disposition);
      if (matches != null && matches[1]) { 
        filename = matches[1].replace(/['"]/g, '');
      }
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download error:', err);
    alert('Failed to download report.');
  }
}

function updateAttacksTable(data) {
  const tbody = document.getElementById('attacks-tbody');
  const empty = document.getElementById('attacks-empty');
  if (!tbody) return;

  const attackEvents = toArray(data.attack_events);
  if (attackEvents.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = attackEvents.slice(0, 10).map(a => {
    const time = a.timestamp ? new Date(a.timestamp).toLocaleTimeString() : '--';
    return `
      <tr>
        <td style="font-size: 0.78rem;">${time}</td>
        <td><span class="type-badge type-attack">${escapeHtml(a.preset_type || '-')}</span></td>
        <td>${toNumber(a.num_ips)}</td>
        <td>${toNumber(a.total_requests).toLocaleString()}</td>
        <td style="color: var(--green); font-weight: 600;">${escapeHtml(a.status || '-')}</td>
      </tr>
    `;
  }).join('');
}

function updateSessionsTable(data) {
  const tbody = document.getElementById('sessions-tbody');
  const empty = document.getElementById('sessions-empty');
  if (!tbody) return;

  const sessions = toArray(data.recent_sessions);
  if (sessions.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = sessions.slice(0, 10).map(s => `
    <tr>
      <td style="font-family: var(--font-mono); font-size: 0.75rem;">${escapeHtml(s.session_id || '-')}</td>
      <td style="font-family: var(--font-mono); font-size: 0.75rem;">${escapeHtml(s.ip || '-')}</td>
      <td>${toNumber(s.pages_visited)}</td>
      <td>${toNumber(s.total_interactions)}</td>
      <td>${toNumber(s.duration_min)}m</td>
      <td><span class="type-badge ${s.is_active ? 'type-normal' : ''}">${s.is_active ? 'Active' : 'Ended'}</span></td>
    </tr>
  `).join('');
}

function updateBlockedTable(data) {
  const tbody = document.getElementById('blocked-tbody');
  const empty = document.getElementById('blocked-empty');
  if (!tbody) return;

  const blockedIps = toArray(data.blocked_ips);
  if (blockedIps.length === 0) {
    tbody.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }

  if (empty) empty.style.display = 'none';

  tbody.innerHTML = blockedIps.map(b => {
    const time = b.blocked_at ? new Date(b.blocked_at).toLocaleString() : '--';
    return `
      <tr>
        <td style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--red); font-weight: 600;">${escapeHtml(b.ip || '-')}</td>
        <td style="font-size: 0.75rem;">${time}</td>
        <td>
          <button class="btn-action unblock-ip-btn" data-ip="${b.ip}" style="border-color: var(--green); color: var(--green);">Unblock</button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── Live Packets Feed (Postman Style) ─────────────────────
const METHOD_COLORS = {
  'GET': '#10B981', 'POST': '#3B82F6', 'PUT': '#F59E0B', 'DELETE': '#EF4444'
};

function updateLivePackets(data) {
  const container = document.getElementById('packets-container');
  const empty = document.getElementById('packets-empty');
  if (!container) return;

  const recentRequests = toArray(data.recent_requests).slice(0, 30);
  const suspiciousIps = new Set(toArray(data.suspicious_ips).map(s => s.ip));
  const packetRows = recentRequests.map((request) => {
    const trafficType = (request.traffic_type || '').toLowerCase();
    const ip = request.ip || '-';
    const isAttack = trafficType === 'attack';
    const isSus = suspiciousIps.has(ip) || isAttack;
    const status = isAttack
      ? { code: 429, text: 'Rate Limited', color: '#F97316' }
      : { code: 200, text: 'OK', color: '#10B981' };
    const requestCount = Math.max(1, toNumber(request.request_count));
    const responseTime = isAttack
      ? Math.min(1200, 50 + requestCount * 2)
      : Math.min(600, 20 + requestCount * 3);
    const method = (request.method || 'GET').toUpperCase();

    return {
      time: toTimestampLabel(request.timestamp),
      method,
      endpoint: request.endpoint || '/',
      ip,
      status,
      responseTime,
      isSus,
      type: isAttack ? 'attack' : 'normal',
    };
  });

  if (packetRows.length === 0) {
    container.innerHTML = '';
    if (empty) empty.style.display = 'block';
    return;
  }
  if (empty) empty.style.display = 'none';

  container.innerHTML = packetRows.map((pkt, i) => `
    <div class="packet-row ${pkt.isSus ? 'packet-suspicious' : ''}" style="animation-delay:${i * 0.03}s">
      <span class="packet-time">${pkt.time}</span>
      <span class="packet-method" style="background:${METHOD_COLORS[pkt.method] || '#64748B'}20;color:${METHOD_COLORS[pkt.method] || '#64748B'};border:1px solid ${METHOD_COLORS[pkt.method] || '#64748B'}40;">${escapeHtml(pkt.method)}</span>
      <span class="packet-endpoint">${escapeHtml(pkt.endpoint)}</span>
      <span class="packet-ip ${pkt.isSus ? 'packet-ip-sus' : ''}">${escapeHtml(pkt.ip)}</span>
      <span class="packet-status" style="color:${pkt.status.color};">${pkt.status.code} ${pkt.status.text}</span>
      <span class="packet-time-ms">${pkt.responseTime}ms</span>
      <span class="packet-type-badge ${pkt.type}">${pkt.type}</span>
    </div>
  `).join('');
}
