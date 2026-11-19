import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = C.spinner();
  let services = [], orders = [], tickets = [], announcements = [];
  try { services = await Api.get('/services'); } catch {}
  try { orders = await Api.get('/orders'); } catch {}
  try { tickets = await Api.get('/tickets'); } catch {}
  try { announcements = await Api.get('/announcements'); } catch {}

  const activeServices = services.filter(s => s.status === 'active').length;
  const pendingOrders = orders.filter(o => o.status === 'pending' || o.status === 'under_review').length;
  const openTickets = tickets.filter(t => t.status === 'open' || t.status === 'reopened').length;

  container.innerHTML = `
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-1">Welcome back, <span class="gradient-text">${C.escapeHtml(Auth.user ? Auth.user.username : '')}</span></h1>
      <p class="text-muted">Here's an overview of your account.</p>
    </div>

    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      ${statCard('Active Services', activeServices, '🖥️', 'primary')}
      ${statCard('Pending Orders', pendingOrders, '📦', 'secondary')}
      ${statCard('Open Tickets', openTickets, '🎫', 'accent')}
      ${statCard('Total Orders', orders.length, '📋', 'muted')}
    </div>

    <div class="grid lg:grid-cols-2 gap-6 mb-8">
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-semibold">Recent Services</h2>
          <a href="#/services" class="text-xs text-primary hover:underline">View all</a>
        </div>
        ${services.length === 0 ? C.emptyState('No services yet', 'Order a plan to get started.') : `
          <div class="space-y-3">
            ${services.slice(0,5).map(s => `
              <div class="flex items-center justify-between p-3 rounded-lg bg-white/3">
                <div>
                  <div class="font-medium text-sm">${C.escapeHtml(s.name)}</div>
                  <div class="text-xs text-muted">${C.formatDate(s.created_at)}</div>
                </div>
                ${C.statusBadge(s.status)}
              </div>
            `).join('')}
          </div>
        `}
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-semibold">Recent Orders</h2>
          <a href="#/orders" class="text-xs text-primary hover:underline">View all</a>
        </div>
        ${orders.length === 0 ? C.emptyState('No orders yet', 'Browse plans to place an order.') : `
          <div class="space-y-3">
            ${orders.slice(0,5).map(o => `
              <div class="flex items-center justify-between p-3 rounded-lg bg-white/3">
                <div>
                  <div class="font-medium text-sm font-mono">${C.escapeHtml(o.order_reference)}</div>
                  <div class="text-xs text-muted">${C.formatDate(o.created_at)}</div>
                </div>
                ${C.statusBadge(o.status)}
              </div>
            `).join('')}
          </div>
        `}
      </div>
    </div>

    ${announcements.length > 0 ? `
      <div class="card p-6">
        <h2 class="font-semibold mb-4">📢 Announcements</h2>
        <div class="space-y-3">
          ${announcements.slice(0,3).map(a => `
            <div class="p-4 rounded-lg bg-white/3 border-l-2 border-primary">
              <div class="font-medium text-sm">${C.escapeHtml(a.title)}</div>
              <div class="text-xs text-muted mt-1">${C.escapeHtml(a.content)}</div>
            </div>
          `).join('')}
        </div>
      </div>
    ` : ''}
  `;

  // quick actions
}

function statCard(label, value, icon, color) {
  return `
    <div class="card p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-muted uppercase tracking-wider">${C.escapeHtml(label)}</span>
        <span class="text-xl">${icon}</span>
      </div>
      <div class="text-3xl font-bold text-${color === 'muted' ? 'muted' : color}">${value}</div>
    </div>
  `;
}
import { Auth } from '../auth.js';
