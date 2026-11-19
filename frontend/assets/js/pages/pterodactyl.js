import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = C.spinner();
  let connected = false;
  let servers = [];
  try {
    const res = await Api.get('/pterodactyl/client/servers');
    connected = res.connected;
    servers = res.servers || [];
  } catch {}

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Pterodactyl <span class="gradient-text">Connection</span></h1>
      <p class="text-muted">Connect your existing Pterodactyl account using your Client API key.</p>
    </div>

    <div class="card p-6 max-w-2xl mb-6">
      <h3 class="font-semibold mb-3">Connection Status</h3>
      ${connected ? `<div class="flex items-center gap-2 text-primary mb-4"><span class="w-2 h-2 bg-primary rounded-full"></span>Connected</div>` : `<div class="flex items-center gap-2 text-muted mb-4"><span class="w-2 h-2 bg-gray-500 rounded-full"></span>Not connected</div>`}
      <form id="connect-form" class="space-y-3">
        <div><label class="block text-sm text-muted mb-1.5">Panel URL</label><input name="panel_url" class="input" placeholder="https://panel.example.com" /></div>
        <div><label class="block text-sm text-muted mb-1.5">Client API Key</label><input name="client_api_key" type="password" class="input" placeholder="ptlc_..." /></div>
        <div class="flex gap-2">
          <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm">Connect</button>
          ${connected ? '<button type="button" id="revoke-btn" class="btn-danger px-4 py-2 rounded-lg text-sm">Revoke</button>' : ''}
        </div>
      </form>
    </div>

    ${connected ? `
      <div class="card p-6">
        <h3 class="font-semibold mb-4">Your Pterodactyl Servers</h3>
        ${servers.length === 0 ? C.emptyState('No servers found', 'Servers linked to your panel account will appear here.') : `
          <div class="space-y-3">
            ${servers.map(s => {
              const attrs = (s.attributes || s) ;
              return `<div class="p-4 rounded-lg bg-white/3 flex items-center justify-between">
                <div>
                  <div class="font-medium">${C.escapeHtml(attrs.name || 'Server')}</div>
                  <div class="text-xs text-muted">${C.escapeHtml(attrs.description || '')}</div>
                </div>
                <span class="badge badge-green">${C.escapeHtml(attrs.status || 'unknown')}</span>
              </div>`;
            }).join('')}
          </div>
        `}
      </div>
    ` : ''}
  `;

  document.getElementById('connect-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await Api.post('/pterodactyl/client/connect', {
        panel_url: fd.get('panel_url') || undefined,
        client_api_key: fd.get('client_api_key'),
      });
      window.toast('Connected successfully', 'success');
      render(container);
    } catch (err) { window.toast(err.message, 'error'); }
  });

  const revokeBtn = document.getElementById('revoke-btn');
  if (revokeBtn) revokeBtn.addEventListener('click', async () => {
    try {
      await Api.post('/pterodactyl/client/revoke', {});
      window.toast('Connection revoked', 'success');
      render(container);
    } catch (err) { window.toast(err.message, 'error'); }
  });
}
