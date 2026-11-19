import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = C.spinner();
  let services = [];
  try { services = await Api.get('/services'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">My <span class="gradient-text">Services</span></h1>
      <p class="text-muted">Your purchased hosting services.</p>
    </div>
    ${services.length === 0 ? C.emptyState('No services yet', 'Order a plan to get started.') : `
      <div class="grid gap-5">
        ${services.map(s => `
          <div class="card p-6">
            <div class="flex flex-wrap items-start justify-between gap-4 mb-4">
              <div>
                <h3 class="font-bold text-lg">${C.escapeHtml(s.name)}</h3>
                <p class="text-xs text-muted">Created ${C.formatDate(s.created_at)}</p>
              </div>
              ${C.statusBadge(s.status)}
            </div>
            <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
              <div><span class="text-muted">RAM:</span> ${s.resources.ram_mb} MB</div>
              <div><span class="text-muted">CPU:</span> ${s.resources.cpu}%</div>
              <div><span class="text-muted">Storage:</span> ${s.resources.storage_mb} MB</div>
              <div><span class="text-muted">Node:</span> ${C.escapeHtml(s.node || '—')}</div>
              <div><span class="text-muted">IP:</span> ${C.escapeHtml(s.ip_address || '—')}</div>
              <div><span class="text-muted">Port:</span> ${s.port || '—'}</div>
              <div><span class="text-muted">Pterodactyl ID:</span> ${s.pterodactyl_server_id || '—'}</div>
              <div><span class="text-muted">Expires:</span> ${C.formatDate(s.expires_at)}</div>
            </div>
            ${s.pterodactyl_server_id ? `
              <div class="flex gap-2 mt-4">
                <button class="btn-secondary px-3 py-1.5 rounded-lg text-xs" data-power="${s.id}" data-signal="start">Start</button>
                <button class="btn-secondary px-3 py-1.5 rounded-lg text-xs" data-power="${s.id}" data-signal="stop">Stop</button>
                <button class="btn-secondary px-3 py-1.5 rounded-lg text-xs" data-power="${s.id}" data-signal="restart">Restart</button>
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>
    `}
  `;

  container.querySelectorAll('[data-power]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const sid = btn.getAttribute('data-power');
      const signal = btn.getAttribute('data-signal');
      try {
        await Api.post(`/services/${sid}/power`, { action: signal });
        window.toast(`${signal} requested`, 'info');
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}
