import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container, opts = {}) {
  container.innerHTML = C.spinner();
  let announcements = [];
  try { announcements = await Api.get('/announcements'); } catch (e) { window.toast(e.message, 'error'); }

  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📢 <span class="gradient-text">Announcements</span></h1>
      <p class="text-muted">Latest updates from the team.</p>
    </div>
    ${announcements.length === 0 ? C.emptyState('No announcements', 'Check back later.') : `
      <div class="space-y-4">
        ${announcements.map(a => `
          <div class="card p-6">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-bold text-lg">${C.escapeHtml(a.title)}</h3>
              <span class="text-xs text-muted">${C.formatDate(a.published_at || a.created_at)}</span>
            </div>
            <div class="text-sm text-muted whitespace-pre-wrap">${C.escapeHtml(a.content)}</div>
          </div>
        `).join('')}
      </div>
    `}
  `;
}
