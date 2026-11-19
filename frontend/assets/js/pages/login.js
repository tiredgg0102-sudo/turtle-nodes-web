import { Auth } from '../auth.js';
import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = `
    <div class="min-h-screen flex items-center justify-center px-6 py-12">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <div class="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-glow mb-4">
            <svg class="w-7 h-7 text-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <h1 class="text-2xl font-bold">Welcome Back</h1>
          <p class="text-muted text-sm mt-1">Sign in to your account</p>
        </div>
        <div class="glass rounded-2xl p-8">
          <form id="login-form" class="space-y-4">
            <div>
              <label class="block text-sm text-muted mb-1.5">Email</label>
              <input type="email" name="email" required class="input" placeholder="you@example.com" />
            </div>
            <div>
              <label class="block text-sm text-muted mb-1.5">Password</label>
              <input type="password" name="password" required class="input" placeholder="••••••••" />
            </div>
            <button type="submit" class="btn-primary w-full py-3 rounded-xl font-semibold">Sign In</button>
          </form>
          <div class="text-center text-sm text-muted mt-6">
            Don't have an account? <a href="#/register" class="text-primary hover:underline">Register</a>
          </div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const btn = e.target.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Signing in...';
    try {
      await Auth.login(fd.get('email'), fd.get('password'));
      window.toast('Welcome back!', 'success');
      window.location.hash = '#/dashboard';
    } catch (err) {
      window.toast(err.message || 'Login failed', 'error');
    } finally {
      btn.disabled = false; btn.textContent = 'Sign In';
    }
  });
}
