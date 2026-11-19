import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = C.spinner();
  let orders = [];
  try { orders = await Api.get('/orders'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">My <span class="gradient-text">Orders</span></h1>
      <p class="text-muted">Track your order status and history.</p>
    </div>
    ${orders.length === 0 ? C.emptyState('No orders yet', 'Browse plans to place an order.') : `
      <div class="card overflow-hidden">
        <table class="table">
          <thead><tr>
            <th>Reference</th><th>Status</th><th>Price</th><th>Created</th><th>Completed</th>
          </tr></thead>
          <tbody>
            ${orders.map(o => `
              <tr>
                <td class="font-mono text-sm">${C.escapeHtml(o.order_reference)}</td>
                <td>${C.statusBadge(o.status)}</td>
                <td>${C.formatMoney(o.total_price, o.currency)}</td>
                <td class="text-sm text-muted">${C.formatDate(o.created_at)}</td>
                <td class="text-sm text-muted">${C.formatDate(o.completed_at)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `}
  `;
}
