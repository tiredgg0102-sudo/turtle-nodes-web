import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = C.spinner();
  let tickets = [];
  try { tickets = await Api.get('/tickets'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6 flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="text-3xl font-bold mb-1">Support <span class="gradient-text">Tickets</span></h1>
        <p class="text-muted">Get help from our team.</p>
      </div>
      <button id="new-ticket-btn" class="btn-primary px-4 py-2 rounded-lg text-sm">+ New Ticket</button>
    </div>
    ${tickets.length === 0 ? C.emptyState('No tickets', 'Create a ticket to contact support.') : `
      <div class="grid gap-4">
        ${tickets.map(t => `
          <div class="card p-5 cursor-pointer" data-ticket="${t.id}">
            <div class="flex items-center justify-between mb-2">
              <div class="font-mono text-sm text-muted">${C.escapeHtml(t.ticket_number)}</div>
              ${C.statusBadge(t.status)}
            </div>
            <h3 class="font-semibold">${C.escapeHtml(t.subject)}</h3>
            <div class="text-xs text-muted mt-1">${C.escapeHtml(t.category)} · ${C.escapeHtml(t.priority)} · ${C.formatDate(t.created_at)}</div>
          </div>
        `).join('')}
      </div>
    `}
  `;

  document.getElementById('new-ticket-btn').addEventListener('click', () => {
    document.body.insertAdjacentHTML('beforeend', C.modal('New Ticket', `
      <form id="ticket-form" class="space-y-4">
        <div><label class="block text-sm text-muted mb-1.5">Subject</label><input name="subject" required class="input" /></div>
        <div><label class="block text-sm text-muted mb-1.5">Category</label>
          <select name="category" class="input">
            <option value="general">General</option>
            <option value="billing">Billing</option>
            <option value="technical">Technical</option>
            <option value="abuse">Abuse</option>
          </select>
        </div>
        <div><label class="block text-sm text-muted mb-1.5">Priority</label>
          <select name="priority" class="input">
            <option value="normal">Normal</option>
            <option value="low">Low</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div><label class="block text-sm text-muted mb-1.5">Message</label><textarea name="message" required rows="4" class="input"></textarea></div>
      </form>
    `, `<button class="btn-secondary px-4 py-2 rounded-lg text-sm" onclick="document.getElementById('modal-root').remove()">Cancel</button><button id="submit-ticket" class="btn-primary px-4 py-2 rounded-lg text-sm">Submit</button>`));
    document.getElementById('submit-ticket').addEventListener('click', async () => {
      const f = document.getElementById('ticket-form');
      const fd = new FormData(f);
      try {
        await Api.post('/tickets', {
          subject: fd.get('subject'),
          category: fd.get('category'),
          priority: fd.get('priority'),
          message: fd.get('message'),
        });
        document.getElementById('modal-root').remove();
        window.toast('Ticket created', 'success');
        render(container);
      } catch (e) { window.toast(e.message, 'error'); }
    });
  });

  container.querySelectorAll('[data-ticket]').forEach(el => {
    el.addEventListener('click', async () => {
      const id = el.getAttribute('data-ticket');
      await viewTicket(id, container);
    });
  });
}

async function viewTicket(id, container) {
  container.innerHTML = C.spinner();
  const ticket = await Api.get(`/tickets/${id}`);
  const messages = await Api.get(`/tickets/${id}/messages`);
  container.innerHTML = `
    <div class="mb-4">
      <button id="back-tickets" class="text-muted hover:text-white text-sm">← Back to tickets</button>
    </div>
    <div class="card p-6 mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="font-mono text-sm text-muted">${C.escapeHtml(ticket.ticket_number)}</span>
        ${C.statusBadge(ticket.status)}
      </div>
      <h2 class="text-xl font-bold mb-1">${C.escapeHtml(ticket.subject)}</h2>
      <div class="text-xs text-muted">${C.escapeHtml(ticket.category)} · ${C.escapeHtml(ticket.priority)} · ${C.formatDate(ticket.created_at)}</div>
    </div>
    <div class="space-y-3 mb-6">
      ${messages.map(m => `
        <div class="card p-4 ${m.is_internal ? 'border-yellow-500/30' : ''}">
          <div class="text-xs text-muted mb-1">${m.is_internal ? '🔒 Internal note' : (m.staff_id ? 'Staff' : 'You')} · ${C.formatDate(m.created_at)}</div>
          <div class="text-sm whitespace-pre-wrap">${C.escapeHtml(m.message)}</div>
        </div>
      `).join('')}
    </div>
    <div class="card p-4">
      <textarea id="reply-msg" rows="3" class="input mb-3" placeholder="Write a reply..."></textarea>
      <button id="reply-btn" class="btn-primary px-4 py-2 rounded-lg text-sm">Reply</button>
    </div>
  `;
  document.getElementById('back-tickets').addEventListener('click', () => render(container));
  document.getElementById('reply-btn').addEventListener('click', async () => {
    const msg = document.getElementById('reply-msg').value;
    if (!msg.trim()) return;
    try {
      await Api.post(`/tickets/${id}/messages`, { message: msg });
      window.toast('Reply sent', 'success');
      viewTicket(id, container);
    } catch (e) { window.toast(e.message, 'error'); }
  });
}
