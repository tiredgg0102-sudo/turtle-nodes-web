import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  const u = Auth.user;
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Account <span class="gradient-text">Settings</span></h1>
      <p class="text-muted">Manage your profile.</p>
    </div>
    <div class="card p-6 max-w-2xl">
      <form id="settings-form" class="space-y-4">
        <div><label class="block text-sm text-muted mb-1.5">Email</label><input name="email" type="email" value="${C.escapeHtml(u.email)}" class="input" /></div>
        <div><label class="block text-sm text-muted mb-1.5">Username</label><input name="username" value="${C.escapeHtml(u.username)}" class="input" /></div>
        <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm">Save Changes</button>
      </form>
    </div>
  `;
  document.getElementById('settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await Api.patch('/users/me', { email: fd.get('email'), username: fd.get('username') });
      await Auth.load();
      window.toast('Settings saved', 'success');
    } catch (err) { window.toast(err.message, 'error'); }
  });
}
import { Auth } from '../auth.js';
