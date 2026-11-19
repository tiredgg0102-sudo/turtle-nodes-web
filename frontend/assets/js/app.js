import { Auth } from './auth.js';
import { Api, toast } from './api.js';

window.toast = toast;
window.Auth = Auth;
import * as C from './components.js';

// Lazy page loaders
const pages = {
  home: () => import('./pages/home.js'),
  plans: () => import('./pages/plans.js'),
  login: () => import('./pages/login.js'),
  register: () => import('./pages/register.js'),
  dashboard: () => import('./pages/dashboard.js'),
  services: () => import('./pages/services.js'),
  orders: () => import('./pages/orders.js'),
  tickets: () => import('./pages/tickets.js'),
  settings: () => import('./pages/settings.js'),
  security: () => import('./pages/security.js'),
  pterodactyl: () => import('./pages/pterodactyl.js'),
  admin: () => import('./pages/admin.js'),
  announcements: () => import('./pages/announcements.js'),
  discord: () => import('./pages/discord.js'),
};

let currentRoute = '';

function parseRoute() {
  const hash = window.location.hash || '#/';
  const path = hash.replace(/^#/, '') || '/';
  return path;
}

const CUSTOMER_SIDEBAR = [
  { route: '/dashboard', label: 'Overview', icon: '🏠' },
  { route: '/services', label: 'My Services', icon: '🖥️' },
  { route: '/orders', label: 'Orders', icon: '📦' },
  { route: '/tickets', label: 'Tickets', icon: '🎫' },
  { route: '/announcements', label: 'Announcements', icon: '📢' },
  { route: '/pterodactyl', label: 'Pterodactyl', icon: '🎮' },
  { route: '/settings', label: 'Settings', icon: '⚙️' },
  { route: '/security', label: 'Security', icon: '🔐' },
];

const ADMIN_SIDEBAR = [
  { route: '/admin', label: 'Dashboard', icon: '📊' },
  { route: '/admin/customers', label: 'Customers', icon: '👥' },
  { route: '/admin/services', label: 'Services', icon: '🖥️' },
  { route: '/admin/orders', label: 'Orders', icon: '📦' },
  { route: '/admin/plans', label: 'Hosting Plans', icon: '📋' },
  { route: '/admin/pterodactyl', label: 'Pterodactyl', icon: '🎮' },
  { route: '/admin/discord', label: 'Discord', icon: '💬' },
  { route: '/admin/tickets', label: 'Tickets', icon: '🎫' },
  { route: '/admin/announcements', label: 'Announcements', icon: '📢' },
  { route: '/admin/logs', label: 'Activity Logs', icon: '📜' },
  { route: '/admin/settings', label: 'Settings', icon: '⚙️' },
  { route: '/admin/security', label: 'Security', icon: '🔐' },
  { route: '/admin/jobs', label: 'Jobs', icon: '🔧' },
  { route: '/admin/diagnostics', label: 'Diagnostics', icon: '🩺' },
];

async function render() {
  const app = document.getElementById('app');
  const path = parseRoute();
  if (path === currentRoute) return;
  currentRoute = path;

  // Public routes
  const publicRoutes = ['/', '/plans', '/discord', '/login', '/register'];
  const isPublic = publicRoutes.includes(path) || path.startsWith('/plans');

  if (!Auth.isAuthed && !isPublic) {
    window.location.hash = '#/login';
    return;
  }

  // Navbar for public pages
  if (isPublic && !Auth.isAuthed) {
    app.innerHTML = C.navbar() + `<main id="page-content" class="min-h-screen"></main>`;
  } else if (path.startsWith('/admin')) {
    app.innerHTML = C.layout('Admin', ADMIN_SIDEBAR, path, `<div id="page-content">${C.spinner()}</div>`);
  } else if (path.startsWith('/dashboard') || path === '/services' || path === '/orders' || path === '/tickets' || path === '/announcements' || path === '/pterodactyl' || path === '/settings' || path === '/security') {
    app.innerHTML = C.layout('Dashboard', CUSTOMER_SIDEBAR, path, `<div id="page-content">${C.spinner()}</div>`);
  } else {
    app.innerHTML = C.navbar() + `<main id="page-content" class="min-h-screen"></main>`;
  }

  // Wire logout
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', async () => { await Auth.logout(); window.location.hash = '#/'; render(); });

  const container = document.getElementById('page-content');
  if (!container) return;

  try {
    await routePage(path, container);
  } catch (e) {
    console.error(e);
    container.innerHTML = `<div class="text-red-400 p-6">Error: ${C.escapeHtml(e.message || e)}</div>`;
  }
}

async function routePage(path, container) {
  // Home
  if (path === '/') {
    const m = await pages.home();
    await m.render(container);
    return;
  }
  if (path === '/plans') {
    const m = await pages.plans();
    await m.render(container, {});
    return;
  }
  if (path === '/login') {
    const m = await pages.login();
    await m.render(container);
    return;
  }
  if (path === '/register') {
    const m = await pages.register();
    await m.render(container);
    return;
  }
  if (path === '/discord') {
    const m = await pages.discord();
    await m.render(container);
    return;
  }
  // Customer
  if (path === '/dashboard') {
    const m = await pages.dashboard();
    await m.render(container);
    return;
  }
  if (path === '/services') {
    const m = await pages.services();
    await m.render(container);
    return;
  }
  if (path === '/orders') {
    const m = await pages.orders();
    await m.render(container);
    return;
  }
  if (path === '/tickets') {
    const m = await pages.tickets();
    await m.render(container);
    return;
  }
  if (path === '/announcements') {
    const m = await pages.announcements();
    await m.render(container, { scope: 'customer' });
    return;
  }
  if (path === '/pterodactyl') {
    const m = await pages.pterodactyl();
    await m.render(container);
    return;
  }
  if (path === '/settings') {
    const m = await pages.settings();
    await m.render(container);
    return;
  }
  if (path === '/security') {
    const m = await pages.security();
    await m.render(container);
    return;
  }
  // Admin
  if (path === '/admin' || path.startsWith('/admin')) {
    const m = await pages.admin();
    await m.render(container, path);
    return;
  }
  container.innerHTML = `<div class="text-center py-20"><h2 class="text-2xl font-bold">404</h2><p class="text-muted mt-2">Page not found</p></div>`;
}

window.addEventListener('hashchange', () => { currentRoute = ''; render(); });

Auth.onChange(() => { currentRoute = ''; render(); });

(async () => {
  await Auth.load();
  render();
})();
