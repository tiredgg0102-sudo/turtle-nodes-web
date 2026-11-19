import { Auth } from './auth.js';

export function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

export function statusBadge(status) {
  const map = {
    active: 'badge-green', approved: 'badge-green', completed: 'badge-green',
    pending: 'badge-yellow', under_review: 'badge-yellow', provisioning: 'badge-cyan',
    rejected: 'badge-red', failed: 'badge-red', cancelled: 'badge-red',
    suspended: 'badge-red', offline: 'badge-gray', open: 'badge-yellow',
    in_progress: 'badge-cyan', closed: 'badge-gray', reopened: 'badge-yellow',
  };
  const cls = map[status] || 'badge-gray';
  return `<span class="badge ${cls}"><span class="w-1.5 h-1.5 rounded-full bg-current"></span>${escapeHtml(status)}</span>`;
}

export function formatDate(d) {
  if (!d) return '—';
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

export function formatMoney(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount || 0);
}

export function spinner() {
  return `<div class="flex items-center justify-center py-12"><div class="spinner w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full"></div></div>`;
}

export function emptyState(title, subtitle = '') {
  return `<div class="text-center py-16 fade-in">
    <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/5 flex items-center justify-center">
      <svg class="w-8 h-8 text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293L9.293 13.293A1 1 0 008.586 13H6"/></svg>
    </div>
    <h3 class="text-lg font-semibold text-white mb-1">${escapeHtml(title)}</h3>
    <p class="text-sm text-muted">${escapeHtml(subtitle)}</p>
  </div>`;
}

export function sidebar(items, active) {
  return `<aside class="w-64 shrink-0 glass-strong border-r border-white/5 min-h-screen sticky top-0 hidden lg:flex flex-col">
    <div class="p-5 border-b border-white/5">
      <a href="#/" class="flex items-center gap-2">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-glow">
          <svg class="w-5 h-5 text-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        </div>
        <span class="font-bold text-lg gradient-text-green">Hosting</span>
      </a>
    </div>
    <nav class="flex-1 p-3 space-y-1 overflow-y-auto">
      ${items.map(it => `
        <a href="#${it.route}" class="sidebar-link ${active === it.route ? 'active' : ''}">
          <span class="text-lg">${it.icon}</span>
          <span>${escapeHtml(it.label)}</span>
        </a>
      `).join('')}
    </nav>
    <div class="p-3 border-t border-white/5">
      <button id="logout-btn" class="sidebar-link w-full text-left text-red-400 hover:text-red-300">
        <span class="text-lg">🚪</span><span>Logout</span>
      </button>
    </div>
  </aside>`;
}

export function topbar(title) {
  const u = Auth.user;
  return `<header class="sticky top-0 z-40 glass-strong border-b border-white/5 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <button id="mobile-menu-btn" class="lg:hidden text-muted hover:text-white">☰</button>
      <h1 class="text-xl font-semibold">${escapeHtml(title)}</h1>
    </div>
    <div class="flex items-center gap-4">
      <button id="notif-btn" class="relative text-muted hover:text-white transition">
        🔔
        <span id="notif-dot" class="hidden absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full"></span>
      </button>
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-bg font-bold text-sm">
          ${(u && u.username ? u.username[0].toUpperCase() : '?')}
        </div>
        <span class="text-sm text-muted hidden sm:block">${escapeHtml(u ? u.username : '')}</span>
      </div>
    </div>
  </header>`;
}

export function layout(title, sidebarItems, activeRoute, content) {
  return `
    <div class="flex min-h-screen">
      ${sidebar(sidebarItems, activeRoute)}
      <div class="flex-1 flex flex-col min-w-0">
        ${topbar(title)}
        <main class="flex-1 p-6 fade-in">
          ${content}
        </main>
      </div>
    </div>
  `;
}

export function modal(title, bodyHtml, footerHtml = '') {
  return `
    <div class="modal-backdrop" id="modal-root">
      <div class="modal">
        <div class="p-6 border-b border-white/5 flex items-center justify-between">
          <h2 class="text-lg font-semibold">${escapeHtml(title)}</h2>
          <button onclick="document.getElementById('modal-root').remove()" class="text-muted hover:text-white text-xl">&times;</button>
        </div>
        <div class="p-6">${bodyHtml}</div>
        ${footerHtml ? `<div class="p-6 border-t border-white/5 flex justify-end gap-3">${footerHtml}</div>` : ''}
      </div>
    </div>
  `;
}

export function navbar() {
  const u = Auth.user;
  return `
    <nav class="sticky top-0 z-50 glass-strong border-b border-white/5">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <a href="#/" class="flex items-center gap-2">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-glow">
            <svg class="w-5 h-5 text-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <span class="font-bold text-lg gradient-text-green">Hosting Platform</span>
        </a>
        <div class="hidden md:flex items-center gap-6 text-sm">
          <a href="#/" class="text-muted hover:text-white transition">Home</a>
          <a href="#/plans" class="text-muted hover:text-white transition">Plans</a>
          <a href="#/discord" class="text-muted hover:text-white transition">Discord</a>
        </div>
        <div class="flex items-center gap-3">
          ${u ? `
            <a href="#/dashboard" class="btn-secondary px-4 py-2 rounded-lg text-sm">Dashboard</a>
            ${Auth.isAdmin ? `<a href="#/admin" class="btn-primary px-4 py-2 rounded-lg text-sm">Admin</a>` : ''}
          ` : `
            <a href="#/login" class="text-muted hover:text-white transition text-sm">Login</a>
            <a href="#/register" class="btn-primary px-4 py-2 rounded-lg text-sm">Get Started</a>
          `}
        </div>
      </div>
    </nav>
  `;
}
