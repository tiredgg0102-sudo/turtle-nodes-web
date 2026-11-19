import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container, opts = {}) {
  container.innerHTML = C.spinner();
  let plans = [];
  try { plans = await Api.get('/plans?active_only=true'); } catch (e) { plans = []; }

  container.innerHTML = `
    <div class="max-w-7xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">Hosting <span class="gradient-text">Plans</span></h1>
        <p class="text-muted">All plans are retrieved live from the backend. Order through Discord.</p>
      </div>
      ${plans.length === 0 ? C.emptyState('No plans available', 'Administrators can create plans from the admin dashboard.') : `
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          ${plans.map(p => `
            <div class="card p-6 flex flex-col">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-bold text-lg text-white">${C.escapeHtml(p.name)}</h3>
                ${p.popular ? '<span class="badge badge-green">Popular</span>' : (p.featured ? '<span class="badge badge-cyan">Featured</span>' : '')}
              </div>
              <p class="text-sm text-muted mb-4 flex-1">${C.escapeHtml(p.short_description || p.description || '')}</p>
              <div class="text-3xl font-black mb-4">${C.formatMoney(p.price, p.currency)}<span class="text-sm text-muted font-normal">/${p.billing_cycle}</span></div>
              <ul class="text-sm text-muted space-y-1.5 mb-4">
                <li>💾 RAM: ${p.resources.ram_mb} MB</li>
                <li>⚡ CPU: ${p.resources.cpu}%</li>
                <li>🗄️ Storage: ${p.resources.storage_mb} MB</li>
                <li>💿 Disk: ${p.resources.disk_mb} MB</li>
                ${(p.features || []).map(f => `<li>✓ ${C.escapeHtml(f)}</li>`).join('')}
              </ul>
              <div class="text-xs text-muted mb-3">${C.escapeHtml(p.available ? 'Available' : 'Unavailable')}</div>
              <button data-order-plan="${p.id}" class="btn-primary w-full py-2.5 rounded-xl text-sm" ${p.available ? '' : 'disabled'}>Order Through Discord</button>
            </div>
          `).join('')}
        </div>
      `}
    </div>
  `;

  container.querySelectorAll('[data-order-plan]').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!Auth.isAuthed) { window.location.hash = '#/login'; return; }
      try {
        const order = await Api.post('/orders', { plan_id: parseInt(btn.getAttribute('data-order-plan')) });
        window.toast('Order created: ' + order.order_reference, 'success');
        window.location.hash = '#/orders';
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}
import { Auth } from '../auth.js';
