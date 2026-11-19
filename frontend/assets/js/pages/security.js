import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = `
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1">Account <span class="gradient-text">Security</span></h1>
      <p class="text-muted">Manage your account security.</p>
    </div>
    <div class="card p-6 max-w-2xl space-y-4">
      <div>
        <h3 class="font-semibold mb-1">Password</h3>
        <p class="text-sm text-muted mb-3">Password changes are handled via secure password reset flow. Contact support if needed.</p>
      </div>
      <div>
        <h3 class="font-semibold mb-1">Sessions</h3>
        <p class="text-sm text-muted">Your session is secured with HttpOnly, Secure cookies and CSRF protection.</p>
      </div>
      <div>
        <h3 class="font-semibold mb-1">Login History</h3>
        <p class="text-sm text-muted">Login history tracking is enabled on the backend.</p>
      </div>
    </div>
  `;
}
