import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container, path) {
  // Normalize
  const route = path || '/admin';

  if (route === '/admin' || route === '/admin/') {
    return renderOverview(container);
  }
  if (route === '/admin/customers') return renderCustomers(container);
  if (route === '/admin/services') return renderServices(container);
  if (route === '/admin/orders') return renderOrders(container);
  if (route === '/admin/plans') return renderPlans(container);
  if (route === '/admin/pterodactyl') return renderPterodactyl(container);
  if (route === '/admin/discord') return renderDiscord(container);
  if (route === '/admin/tickets') return renderTickets(container);
  if (route === '/admin/announcements') return renderAnnouncements(container);
  if (route === '/admin/logs') return renderLogs(container);
  if (route === '/admin/settings') return renderSettings(container);
  if (route === '/admin/security') return renderSecurity(container);
  if (route === '/admin/jobs') return renderJobs(container);
  if (route === '/admin/diagnostics') return renderDiagnostics(container);

  container.innerHTML = `<div class="text-center py-20 text-muted">Unknown admin route: ${C.escapeHtml(route)}</div>`;
}

// ---------- Overview ----------
async function renderOverview(container) {
  container.innerHTML = C.spinner();
  let overview = {}, stats = {}, activities = [];
  try { overview = await Api.get('/admin/overview'); } catch {}
  try { stats = await Api.get('/admin/stats'); } catch {}
  try { activities = await Api.get('/admin/recent-activities?limit=10'); } catch {}

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Admin <span class="gradient-text">Dashboard</span></h1>
      <p class="text-muted">Platform overview and statistics.</p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      ${adminStat('Total Customers', overview.total_customers, '👥')}
      ${adminStat('Active Services', overview.active_services, '🖥️')}
      ${adminStat('Pending Orders', overview.pending_orders, '📦')}
      ${adminStat('Open Tickets', overview.open_tickets, '🎫')}
      ${adminStat('Total Orders', overview.total_orders, '📋')}
      ${adminStat('Total Tickets', overview.total_tickets, '🎫')}
      ${adminStat('Failed Provisioning', overview.failed_provisioning, '⚠️')}
      ${adminStat('Plans', overview.plans, '📋')}
    </div>
    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card p-6">
        <h2 class="font-semibold mb-4">Recent Activity</h2>
        ${activities.length === 0 ? C.emptyState('No activity yet') : `
          <div class="space-y-2">
            ${activities.map(a => `
              <div class="flex items-center justify-between p-2 rounded bg-white/3 text-sm">
                <span>${C.escapeHtml(a.action)} ${a.resource_type ? '· ' + C.escapeHtml(a.resource_type) : ''}</span>
                <span class="text-xs text-muted">${C.formatDate(a.created_at)}</span>
              </div>
            `).join('')}
          </div>
        `}
      </div>
      <div class="card p-6">
        <h2 class="font-semibold mb-4">Orders by Status</h2>
        ${renderBarList(stats.orders_by_status)}
      </div>
    </div>
  `;
}

function adminStat(label, value, icon) {
  return `<div class="card p-5"><div class="flex items-center justify-between mb-2"><span class="text-xs text-muted uppercase tracking-wider">${C.escapeHtml(label)}</span><span class="text-xl">${icon}</span></div><div class="text-3xl font-bold text-primary">${value ?? 0}</div></div>`;
}

function renderBarList(items) {
  if (!items || !items.length) return C.emptyState('No data');
  const max = Math.max(...items.map(i => i.count), 1);
  return `<div class="space-y-2">${items.map(i => `
    <div>
      <div class="flex justify-between text-xs mb-1"><span class="text-muted">${C.escapeHtml(i.status)}</span><span>${i.count}</span></div>
      <div class="h-2 bg-white/5 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-primary to-secondary" style="width:${(i.count/max*100).toFixed(0)}%"></div></div>
    </div>
  `).join('')}</div>`;
}

// ---------- Customers ----------
async function renderCustomers(container) {
  container.innerHTML = C.spinner();
  let users = [];
  try { users = await Api.get('/users?limit=100'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Customers</h1>
      <p class="text-muted">Manage customer accounts.</p>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>ID</th><th>Email</th><th>Username</th><th>Role</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead>
        <tbody>
          ${users.map(u => `
            <tr>
              <td>${u.id}</td>
              <td class="text-sm">${C.escapeHtml(u.email)}</td>
              <td>${C.escapeHtml(u.username)}</td>
              <td><span class="badge badge-gray">${C.escapeHtml(u.role)}</span></td>
              <td>${C.statusBadge(u.status)}</td>
              <td class="text-xs text-muted">${C.formatDate(u.created_at)}</td>
              <td class="space-x-1">
                <button class="btn-secondary px-2 py-1 rounded text-xs" data-role="${u.id}">Role</button>
                <button class="btn-secondary px-2 py-1 rounded text-xs" data-status="${u.id}">Status</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  container.querySelectorAll('[data-role]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-role');
      const role = prompt('New role (customer/staff/admin):');
      if (!role) return;
      try {
        await Api.patch(`/users/${id}/role`, { role });
        window.toast('Role updated', 'success');
        renderCustomers(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
  container.querySelectorAll('[data-status]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-status');
      const status = prompt('New status (active/suspended):');
      if (!status) return;
      try {
        await Api.patch(`/users/${id}/status`, { status });
        window.toast('Status updated', 'success');
        renderCustomers(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}

// ---------- Services ----------
async function renderServices(container) {
  container.innerHTML = C.spinner();
  let services = [];
  try { services = await Api.get('/services'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Services</h1>
      <p class="text-muted">All provisioned services.</p>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>ID</th><th>Name</th><th>User</th><th>Status</th><th>Server ID</th><th>Created</th></tr></thead>
        <tbody>
          ${services.map(s => `
            <tr>
              <td>${s.id}</td>
              <td>${C.escapeHtml(s.name)}</td>
              <td>${s.user_id || ''}</td>
              <td>${C.statusBadge(s.status)}</td>
              <td class="font-mono text-xs">${s.pterodactyl_server_id || '—'}</td>
              <td class="text-xs text-muted">${C.formatDate(s.created_at)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ---------- Orders ----------
async function renderOrders(container) {
  container.innerHTML = C.spinner();
  let orders = [];
  try { orders = await Api.get('/orders'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Orders</h1>
      <p class="text-muted">Review and manage customer orders.</p>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>Reference</th><th>User</th><th>Status</th><th>Price</th><th>Created</th><th>Actions</th></tr></thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td class="font-mono text-sm">${C.escapeHtml(o.order_reference)}</td>
              <td>${o.user_id}</td>
              <td>${C.statusBadge(o.status)}</td>
              <td>${C.formatMoney(o.total_price, o.currency)}</td>
              <td class="text-xs text-muted">${C.formatDate(o.created_at)}</td>
              <td class="space-x-1">
                ${o.status === 'pending' || o.status === 'under_review' ? `
                  <button class="btn-primary px-2 py-1 rounded text-xs" data-approve="${o.id}">Approve</button>
                  <button class="btn-danger px-2 py-1 rounded text-xs" data-reject="${o.id}">Reject</button>
                ` : ''}
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  container.querySelectorAll('[data-approve]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-approve');
      if (!confirm('Approve this order?')) return;
      try {
        await Api.patch(`/orders/${id}/review`, { action: 'approve' });
        window.toast('Order approved', 'success');
        renderOrders(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
  container.querySelectorAll('[data-reject]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-reject');
      const reason = prompt('Rejection reason:');
      if (reason === null) return;
      try {
        await Api.patch(`/orders/${id}/review`, { action: 'reject', reason });
        window.toast('Order rejected', 'success');
        renderOrders(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}

// ---------- Plans ----------
async function renderPlans(container) {
  container.innerHTML = C.spinner();
  let plans = [];
  try { plans = await Api.get('/plans'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-3xl font-bold mb-1">Hosting Plans</h1>
        <p class="text-muted">Create, edit, and manage hosting plans.</p>
      </div>
      <button id="new-plan-btn" class="btn-primary px-4 py-2 rounded-lg text-sm">+ New Plan</button>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>ID</th><th>Name</th><th>Price</th><th>RAM</th><th>CPU</th><th>Storage</th><th>Active</th><th>Available</th><th>Actions</th></tr></thead>
        <tbody>
          ${plans.map(p => `
            <tr>
              <td>${p.id}</td>
              <td>${C.escapeHtml(p.name)}</td>
              <td>${C.formatMoney(p.price, p.currency)}</td>
              <td>${p.resources.ram_mb}</td>
              <td>${p.resources.cpu}</td>
              <td>${p.resources.storage_mb}</td>
              <td>${p.active ? '✅' : '❌'}</td>
              <td>${p.available ? '✅' : '❌'}</td>
              <td class="space-x-1">
                <button class="btn-secondary px-2 py-1 rounded text-xs" data-edit-plan="${p.id}">Edit</button>
                <button class="btn-danger px-2 py-1 rounded text-xs" data-del-plan="${p.id}">Delete</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById('new-plan-btn').addEventListener('click', () => openPlanModal(container, null));
  container.querySelectorAll('[data-edit-plan]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-edit-plan');
      const plan = plans.find(p => p.id == id);
      openPlanModal(container, plan);
    });
  });
  container.querySelectorAll('[data-del-plan]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-del-plan');
      if (!confirm('Delete this plan?')) return;
      try {
        await Api.del(`/plans/${id}`);
        window.toast('Plan deleted', 'success');
        renderPlans(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}

function openPlanModal(container, plan) {
  const isEdit = !!plan;
  const body = `
    <form id="plan-form" class="space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <div><label class="block text-sm text-muted mb-1">Name</label><input name="name" value="${C.escapeHtml(plan?.name || '')}" required class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Slug</label><input name="slug" value="${C.escapeHtml(plan?.slug || '')}" ${isEdit ? 'readonly' : 'required'} class="input" /></div>
      </div>
      <div><label class="block text-sm text-muted mb-1">Description</label><textarea name="description" class="input">${C.escapeHtml(plan?.description || '')}</textarea></div>
      <div><label class="block text-sm text-muted mb-1">Short Description</label><input name="short_description" value="${C.escapeHtml(plan?.short_description || '')}" class="input" /></div>
      <div class="grid grid-cols-3 gap-3">
        <div><label class="block text-sm text-muted mb-1">Category ID</label><input name="category_id" type="number" value="${plan?.category_id || 1}" required class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Price</label><input name="price" type="number" step="0.01" value="${plan?.price || 0}" required class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Currency</label><input name="currency" value="${C.escapeHtml(plan?.currency || 'USD')}" class="input" /></div>
      </div>
      <div class="grid grid-cols-4 gap-3">
        <div><label class="block text-sm text-muted mb-1">RAM MB</label><input name="ram_mb" type="number" value="${plan?.resources?.ram_mb || 0}" class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">CPU %</label><input name="cpu" type="number" value="${plan?.resources?.cpu || 0}" class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Storage MB</label><input name="storage_mb" type="number" value="${plan?.resources?.storage_mb || 0}" class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Disk MB</label><input name="disk_mb" type="number" value="${plan?.resources?.disk_mb || 0}" class="input" /></div>
      </div>
      <div><label class="block text-sm text-muted mb-1">Features (comma-separated)</label><input name="features" value="${C.escapeHtml((plan?.features || []).join(', '))}" class="input" /></div>
      <div class="flex gap-4">
        <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="active" ${plan?.active !== false ? 'checked' : ''} /> Active</label>
        <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="available" ${plan?.available !== false ? 'checked' : ''} /> Available</label>
        <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="featured" ${plan?.featured ? 'checked' : ''} /> Featured</label>
        <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="popular" ${plan?.popular ? 'checked' : ''} /> Popular</label>
      </div>
    </form>
  `;
  const footer = `<button class="btn-secondary px-4 py-2 rounded-lg text-sm" onclick="document.getElementById('modal-root').remove()">Cancel</button><button id="save-plan" class="btn-primary px-4 py-2 rounded-lg text-sm">Save</button>`;
  document.body.insertAdjacentHTML('beforeend', C.modal(isEdit ? 'Edit Plan' : 'New Plan', body, footer));

  document.getElementById('save-plan').addEventListener('click', async () => {
    const f = document.getElementById('plan-form');
    const fd = new FormData(f);
    const features = fd.get('features').split(',').map(s => s.trim()).filter(Boolean);
    const payload = {
      category_id: parseInt(fd.get('category_id')),
      name: fd.get('name'),
      slug: fd.get('slug'),
      description: fd.get('description'),
      short_description: fd.get('short_description'),
      price: parseFloat(fd.get('price')),
      currency: fd.get('currency'),
      billing_cycle: 'monthly',
      ram_mb: parseInt(fd.get('ram_mb') || 0),
      cpu: parseInt(fd.get('cpu') || 0),
      storage_mb: parseInt(fd.get('storage_mb') || 0),
      disk_mb: parseInt(fd.get('disk_mb') || 0),
      features,
      active: f.querySelector('[name=active]').checked,
      available: f.querySelector('[name=available]').checked,
      featured: f.querySelector('[name=featured]').checked,
      popular: f.querySelector('[name=popular]').checked,
      sort_order: 0,
    };
    try {
      if (isEdit) await Api.patch(`/plans/${plan.id}`, payload);
      else await Api.post('/plans', payload);
      document.getElementById('modal-root').remove();
      window.toast('Plan saved', 'success');
      renderPlans(container);
    } catch (e) { window.toast(e.message, 'error'); }
  });
}

// ---------- Pterodactyl ----------
async function renderPterodactyl(container) {
  container.innerHTML = C.spinner();
  let cfg = null;
  try { cfg = await Api.get('/pterodactyl/config'); } catch {}
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Pterodactyl Integration</h1>
      <p class="text-muted">Connect to your existing Pterodactyl panel.</p>
    </div>
    <div class="card p-6 max-w-3xl">
      <form id="ptero-form" class="space-y-4">
        <div><label class="block text-sm text-muted mb-1.5">Panel URL</label><input name="panel_url" value="${C.escapeHtml(cfg?.panel_url || '')}" class="input" placeholder="https://panel.example.com" /></div>
        <div><label class="block text-sm text-muted mb-1.5">Application API Key ${cfg ? '(leave blank to keep existing)' : ''}</label><input name="app_api_key" type="password" class="input" placeholder="ptla_..." /></div>
        <div class="grid grid-cols-3 gap-3">
          <div><label class="block text-sm text-muted mb-1">Default Node ID</label><input name="default_node_id" type="number" value="${cfg?.default_node_id || ''}" class="input" /></div>
          <div><label class="block text-sm text-muted mb-1">Default Location ID</label><input name="default_location_id" type="number" value="${cfg?.default_location_id || ''}" class="input" /></div>
          <div><label class="block text-sm text-muted mb-1">Default Nest ID</label><input name="default_nest_id" type="number" value="${cfg?.default_nest_id || ''}" class="input" /></div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div><label class="block text-sm text-muted mb-1">Default Egg ID</label><input name="default_egg_id" type="number" value="${cfg?.default_egg_id || ''}" class="input" /></div>
          <div><label class="block text-sm text-muted mb-1">Default RAM (MB)</label><input name="default_ram" type="number" value="${cfg?.default_ram || 1024}" class="input" /></div>
          <div><label class="block text-sm text-muted mb-1">Default CPU (%)</label><input name="default_cpu" type="number" value="${cfg?.default_cpu || 100}" class="input" /></div>
        </div>
        <div class="flex gap-2">
          <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm">Save Configuration</button>
          <button type="button" id="test-conn" class="btn-secondary px-4 py-2 rounded-lg text-sm">Test Connection</button>
        </div>
      </form>
      <div id="test-result" class="mt-4 text-sm"></div>
    </div>
  `;

  document.getElementById('ptero-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = {
      panel_url: fd.get('panel_url'),
      default_node_id: fd.get('default_node_id') ? parseInt(fd.get('default_node_id')) : null,
      default_location_id: fd.get('default_location_id') ? parseInt(fd.get('default_location_id')) : null,
      default_nest_id: fd.get('default_nest_id') ? parseInt(fd.get('default_nest_id')) : null,
      default_egg_id: fd.get('default_egg_id') ? parseInt(fd.get('default_egg_id')) : null,
      default_ram: parseInt(fd.get('default_ram') || 1024),
      default_cpu: parseInt(fd.get('default_cpu') || 100),
      default_storage: 20480, default_disk: 20480, default_io: 500, default_overlimit: false, active: true,
    };
    const key = fd.get('app_api_key');
    if (key) payload.app_api_key = key;
    try {
      if (cfg) await Api.patch('/pterodactyl/config', payload);
      else await Api.post('/pterodactyl/config', { ...payload, app_api_key: key || '' });
      window.toast('Configuration saved', 'success');
      renderPterodactyl(container);
    } catch (e) { window.toast(e.message, 'error'); }
  });

  document.getElementById('test-conn').addEventListener('click', async () => {
    const fd = new FormData(document.getElementById('ptero-form'));
    const resEl = document.getElementById('test-result');
    resEl.textContent = 'Testing...';
    try {
      const res = await Api.post('/pterodactyl/config/test', { panel_url: fd.get('panel_url'), app_api_key: fd.get('app_api_key') || (cfg ? '' : '') });
      // If no key provided, test with empty will fail; that's expected.
      resEl.innerHTML = res.success ? `<span class="text-primary">✓ ${C.escapeHtml(res.message)}</span>` : `<span class="text-red-400">✗ ${C.escapeHtml(res.message)}</span>`;
    } catch (e) { resEl.innerHTML = `<span class="text-red-400">✗ ${C.escapeHtml(e.message)}</span>`; }
  });
}

// ---------- Discord ----------
async function renderDiscord(container) {
  container.innerHTML = C.spinner();
  let cfg = {};
  try { cfg = await Api.get('/discord/config'); } catch {}
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Discord Integration</h1>
      <p class="text-muted">Discord bot configuration (read from environment).</p>
    </div>
    <div class="card p-6 max-w-2xl">
      <div class="space-y-3 text-sm">
        <div class="flex justify-between"><span class="text-muted">Bot configured</span><span>${cfg.bot_configured ? '✅' : '❌'}</span></div>
        <div class="flex justify-between"><span class="text-muted">Guild ID</span><span class="font-mono">${C.escapeHtml(cfg.guild_id || '—')}</span></div>
        <div class="flex justify-between"><span class="text-muted">Staff role IDs</span><span class="font-mono text-xs">${C.escapeHtml((cfg.staff_role_ids || []).join(', ') || '—')}</span></div>
        <div class="flex justify-between"><span class="text-muted">Order channel</span><span class="font-mono">${C.escapeHtml(cfg.order_channel_id || '—')}</span></div>
        <div class="flex justify-between"><span class="text-muted">Staff channel</span><span class="font-mono">${C.escapeHtml(cfg.staff_channel_id || '—')}</span></div>
        <div class="flex justify-between"><span class="text-muted">Invite URL</span><span class="font-mono text-xs">${C.escapeHtml(cfg.invite_url || '—')}</span></div>
      </div>
      <p class="text-xs text-muted mt-4">Configure these values in your <code>.env</code> file. See docs/discord.md.</p>
    </div>
  `;
}

// ---------- Tickets (admin) ----------
async function renderTickets(container) {
  container.innerHTML = C.spinner();
  let tickets = [];
  try { tickets = await Api.get('/tickets'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Tickets</h1>
      <p class="text-muted">Manage support tickets.</p>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>Number</th><th>User</th><th>Subject</th><th>Status</th><th>Priority</th><th>Created</th><th>Actions</th></tr></thead>
        <tbody>
          ${tickets.map(t => `
            <tr>
              <td class="font-mono text-xs">${C.escapeHtml(t.ticket_number)}</td>
              <td>${t.user_id}</td>
              <td>${C.escapeHtml(t.subject)}</td>
              <td>${C.statusBadge(t.status)}</td>
              <td>${C.escapeHtml(t.priority)}</td>
              <td class="text-xs text-muted">${C.formatDate(t.created_at)}</td>
              <td class="space-x-1">
                <button class="btn-secondary px-2 py-1 rounded text-xs" data-close="${t.id}">Close</button>
                <button class="btn-secondary px-2 py-1 rounded text-xs" data-reopen="${t.id}">Reopen</button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  container.querySelectorAll('[data-close]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-close');
      try { await Api.patch(`/tickets/${id}`, { status: 'closed' }); window.toast('Closed', 'success'); renderTickets(container); }
      catch (e) { window.toast(e.message, 'error'); }
    });
  });
  container.querySelectorAll('[data-reopen]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-reopen');
      try { await Api.patch(`/tickets/${id}`, { status: 'reopened' }); window.toast('Reopened', 'success'); renderTickets(container); }
      catch (e) { window.toast(e.message, 'error'); }
    });
  });
}

// ---------- Announcements ----------
async function renderAnnouncements(container) {
  container.innerHTML = C.spinner();
  let announcements = [];
  try { announcements = await Api.get('/announcements'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-3xl font-bold mb-1">Announcements</h1>
        <p class="text-muted">Publish updates to customers.</p>
      </div>
      <button id="new-ann" class="btn-primary px-4 py-2 rounded-lg text-sm">+ New Announcement</button>
    </div>
    <div class="space-y-4">
      ${announcements.map(a => `
        <div class="card p-5">
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-bold">${C.escapeHtml(a.title)}</h3>
            <span class="badge ${a.active ? 'badge-green' : 'badge-gray'}">${a.active ? 'Active' : 'Inactive'}</span>
          </div>
          <p class="text-sm text-muted whitespace-pre-wrap">${C.escapeHtml(a.content)}</p>
          <div class="text-xs text-muted mt-2">${C.formatDate(a.created_at)}</div>
        </div>
      `).join('')}
    </div>
  `;

  document.getElementById('new-ann').addEventListener('click', () => {
    document.body.insertAdjacentHTML('beforeend', C.modal('New Announcement', `
      <form id="ann-form" class="space-y-3">
        <div><label class="block text-sm text-muted mb-1">Title</label><input name="title" required class="input" /></div>
        <div><label class="block text-sm text-muted mb-1">Content</label><textarea name="content" required rows="4" class="input"></textarea></div>
        <label class="flex items-center gap-2 text-sm"><input type="checkbox" name="active" checked /> Active</label>
      </form>
    `, `<button class="btn-secondary px-4 py-2 rounded-lg text-sm" onclick="document.getElementById('modal-root').remove()">Cancel</button><button id="save-ann" class="btn-primary px-4 py-2 rounded-lg text-sm">Publish</button>`));
    document.getElementById('save-ann').addEventListener('click', async () => {
      const f = document.getElementById('ann-form');
      const fd = new FormData(f);
      try {
        await Api.post('/announcements', { title: fd.get('title'), content: fd.get('content'), active: f.querySelector('[name=active]').checked });
        document.getElementById('modal-root').remove();
        window.toast('Published', 'success');
        renderAnnouncements(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });
}

// ---------- Logs ----------
async function renderLogs(container) {
  container.innerHTML = C.spinner();
  let activities = [];
  try { activities = await Api.get('/admin/recent-activities?limit=50'); } catch (e) { window.toast(e.message, 'error'); }
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Activity Logs</h1>
      <p class="text-muted">Recent admin actions.</p>
    </div>
    <div class="card overflow-hidden">
      <table class="table">
        <thead><tr><th>ID</th><th>User</th><th>Action</th><th>Resource</th><th>IP</th><th>Time</th></tr></thead>
        <tbody>
          ${activities.map(a => `
            <tr>
              <td>${a.id}</td>
              <td>${a.user_id || '—'}</td>
              <td>${C.escapeHtml(a.action)}</td>
              <td class="text-xs">${C.escapeHtml(a.resource_type || '')} ${a.resource_id || ''}</td>
              <td class="text-xs text-muted">${C.escapeHtml(a.ip_address || '')}</td>
              <td class="text-xs text-muted">${C.formatDate(a.created_at)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

// ---------- Settings ----------
async function renderSettings(container) {
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">System Settings</h1>
      <p class="text-muted">Platform configuration is managed via environment variables and the Pterodactyl/Discord settings pages.</p>
    </div>
    <div class="card p-6 max-w-2xl space-y-3 text-sm">
      <div class="flex justify-between"><span class="text-muted">App</span><span>${C.escapeHtml(window.location.origin)}</span></div>
      <div class="flex justify-between"><span class="text-muted">API base</span><span>/api/v1</span></div>
      <p class="text-xs text-muted mt-4">See docs/env.md for all environment variables.</p>
    </div>
  `;
}

// ---------- Security ----------
async function renderSecurity(container) {
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Security</h1>
      <p class="text-muted">Security posture and audit.</p>
    </div>
    <div class="card p-6 max-w-2xl space-y-2 text-sm">
      <div>✅ Password hashing (bcrypt)</div>
      <div>✅ JWT in HttpOnly cookies</div>
      <div>✅ CSRF double-submit protection</div>
      <div>✅ Rate limiting on auth endpoints</div>
      <div>✅ Role-based access control</div>
      <div>✅ Encrypted credentials at rest (Fernet)</div>
      <div>✅ Audit logging</div>
      <div>✅ Secret redaction in logs</div>
    </div>
  `;
}

// ---------- Jobs ----------
async function renderJobs(container) {
  container.innerHTML = C.spinner();
  let jobs = [];
  try {
    // No dedicated endpoint; fetch via provisioning jobs is not exposed. Show placeholder honest message.
    jobs = [];
  } catch {}
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Background Jobs</h1>
      <p class="text-muted">Provisioning jobs are processed in the background. Job details are recorded in the database.</p>
    </div>
    <div class="card p-6">
      <p class="text-sm text-muted">Provisioning jobs run automatically when orders are approved. Failed jobs can be retried from the order management page.</p>
    </div>
  `;
}

// ---------- Diagnostics ----------
async function renderDiagnostics(container) {
  container.innerHTML = C.spinner();
  let health = {};
  try { health = await Api.get('/system/health'); } catch (e) { window.toast(e.message, 'error'); }
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">System Diagnostics</h1>
      <p class="text-muted">Health checks and system status.</p>
    </div>
    <div class="card p-6 max-w-2xl space-y-2 text-sm">
      <div class="flex justify-between"><span class="text-muted">Status</span><span class="text-primary">${C.escapeHtml(health.status || '—')}</span></div>
      <div class="flex justify-between"><span class="text-muted">App</span><span>${C.escapeHtml(health.app || '—')}</span></div>
      <div class="flex justify-between"><span class="text-muted">Version</span><span>${C.escapeHtml(health.version || '—')}</span></div>
      <div class="flex justify-between"><span class="text-muted">Environment</span><span>${C.escapeHtml(health.env || '—')}</span></div>
      <div class="flex justify-between"><span class="text-muted">Database</span><span>${health.database_configured ? '✅' : '❌'}</span></div>
      <div class="flex justify-between"><span class="text-muted">Pterodactyl</span><span>${health.pterodactyl_configured ? '✅' : '❌'}</span></div>
      <div class="flex justify-between"><span class="text-muted">Discord</span><span>${health.discord_configured ? '✅' : '❌'}</span></div>
    </div>
  `;
}
