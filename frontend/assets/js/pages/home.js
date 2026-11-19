import { Api } from '../api.js';
import * as C from '../components.js';

export async function render(container) {
  let plans = [];
  try { plans = await Api.get('/plans?active_only=true'); } catch (e) { plans = []; }
  // Group by category is not available; fetch categories
  let categories = [];
  try { categories = []; } catch {}

  const featuredPlans = plans.slice(0, 6);

  container.innerHTML = `
    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div class="max-w-7xl mx-auto px-6 py-20 lg:py-28">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="fade-in">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs text-primary mb-6">
              <span class="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
              Next-generation hosting infrastructure
            </div>
            <h1 class="text-4xl lg:text-6xl font-black leading-tight mb-6">
              Premium Hosting<br/>
              <span class="gradient-text">Built for Scale</span>
            </h1>
            <p class="text-lg text-muted mb-8 max-w-xl">
              Deploy Minecraft servers, Discord bots, Python applications, and KVM VPS instances
              on enterprise-grade infrastructure. Unified dashboard, real-time control, and a
              community-driven ordering experience.
            </p>
            <div class="flex flex-wrap gap-3">
              <a href="#/plans" class="btn-primary px-6 py-3 rounded-xl">Explore Plans</a>
              <a href="#/register" class="btn-secondary px-6 py-3 rounded-xl">Get Started</a>
            </div>
            <div class="flex items-center gap-6 mt-10 text-sm text-muted">
              <div><span class="text-white font-bold text-2xl">99.9%</span><br/>Uptime SLA</div>
              <div><span class="text-white font-bold text-2xl">24/7</span><br/>Support</div>
              <div><span class="text-white font-bold text-2xl">Instant</span><br/>Provisioning</div>
            </div>
          </div>
          <div class="relative fade-in">
            <div class="glass rounded-3xl p-6 glow-pulse">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                <span class="ml-2 text-xs text-muted font-mono">server-console</span>
              </div>
              <pre class="font-mono text-xs text-green-400 leading-relaxed overflow-hidden">
[INFO] Starting Minecraft server...
[INFO] Loading mods: 47 mods found
[INFO] Preparing level "world"
[INFO] Done (4.2s)! For help, type "help"
> status
Server is running on 0.0.0.0:25565
Players: 0/50
TPS: 20.0
> _</pre>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Categories -->
    <section class="max-w-7xl mx-auto px-6 py-16">
      <div class="text-center mb-12">
        <h2 class="text-3xl lg:text-4xl font-bold mb-3">Hosting <span class="gradient-text">Categories</span></h2>
        <p class="text-muted max-w-2xl mx-auto">Choose the right hosting solution for your project. Every plan is configurable by our administrators.</p>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        ${[
          { icon: '⛏️', title: 'Minecraft Hosting', desc: 'Vanilla & modded Minecraft servers with instant setup.' },
          { icon: '🧩', title: 'Modded Minecraft', desc: 'Heavy modpacks with optimized JVM settings.' },
          { icon: '🤖', title: 'Discord Bot Hosting', desc: '24/7 Discord bots with auto-restart.' },
          { icon: '🐍', title: 'Python Bot Hosting', desc: 'Python applications and automation bots.' },
          { icon: '💻', title: 'KVM VPS Hosting', desc: 'Full root access virtual private servers.' },
          { icon: '☁️', title: 'Custom Services', desc: 'Administrator-defined hosting solutions.' },
        ].map(c => `
          <div class="card p-6">
            <div class="text-3xl mb-3">${c.icon}</div>
            <h3 class="font-semibold text-white mb-1">${C.escapeHtml(c.title)}</h3>
            <p class="text-sm text-muted">${C.escapeHtml(c.desc)}</p>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- Plans -->
    <section class="max-w-7xl mx-auto px-6 py-16">
      <div class="flex items-end justify-between mb-8 flex-wrap gap-4">
        <div>
          <h2 class="text-3xl lg:text-4xl font-bold mb-2">Available <span class="gradient-text">Plans</span></h2>
          <p class="text-muted">Live plans from the backend. Order through Discord.</p>
        </div>
        <a href="#/plans" class="btn-secondary px-4 py-2 rounded-lg text-sm">View All Plans →</a>
      </div>
      ${featuredPlans.length === 0 ? C.emptyState('No plans available yet', 'Administrators can create hosting plans from the admin dashboard.') : `
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          ${featuredPlans.map(p => planCard(p)).join('')}
        </div>
      `}
    </section>

    <!-- Features -->
    <section class="max-w-7xl mx-auto px-6 py-16">
      <div class="text-center mb-12">
        <h2 class="text-3xl lg:text-4xl font-bold mb-3">Why Choose <span class="gradient-text">Us</span></h2>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        ${[
          { icon: '⚡', title: 'Instant Provisioning', desc: 'Services go live within seconds of approval.' },
          { icon: '🔒', title: 'Secure by Design', desc: 'Encrypted credentials, RBAC, CSRF protection.' },
          { icon: '📊', title: 'Real Dashboard', desc: 'Live service status and resource usage.' },
          { icon: '💬', title: 'Discord Ordering', desc: 'Order and track via your Discord community.' },
        ].map(f => `
          <div class="card p-6 text-center">
            <div class="text-3xl mb-3">${f.icon}</div>
            <h3 class="font-semibold text-white mb-1">${C.escapeHtml(f.title)}</h3>
            <p class="text-sm text-muted">${C.escapeHtml(f.desc)}</p>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- Discord CTA -->
    <section class="max-w-7xl mx-auto px-6 py-16">
      <div class="glass rounded-3xl p-10 text-center glow-border">
        <h2 class="text-3xl font-bold mb-3">Join Our <span class="gradient-text">Discord</span> Community</h2>
        <p class="text-muted mb-6 max-w-xl mx-auto">All orders are processed through Discord. Get support, updates, and connect with other customers.</p>
        <a href="#/discord" class="btn-primary px-6 py-3 rounded-xl inline-block">Join Discord</a>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-white/5 mt-16">
      <div class="max-w-7xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted">
        <div>© ${new Date().getFullYear()} Hosting Platform. All rights reserved.</div>
        <div class="flex gap-6">
          <a href="#/" class="hover:text-white">Home</a>
          <a href="#/plans" class="hover:text-white">Plans</a>
          <a href="#/discord" class="hover:text-white">Discord</a>
        </div>
      </div>
    </footer>
  `;

  // Bind order buttons
  container.querySelectorAll('[data-order-plan]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const planId = btn.getAttribute('data-order-plan');
      if (!Auth.isAuthed) { window.location.hash = '#/login'; return; }
      try {
        const order = await Api.post('/orders', { plan_id: parseInt(planId) });
        window.location.hash = '#/orders';
        // Show order reference
        setTimeout(() => {}, 100);
        alert('Order created: ' + order.order_reference + '\\nContinue in Discord to submit for review.');
      } catch (e) { (window.toast || alert)(e.message); }
    });
  });
}

function planCard(p) {
  const resources = p.resources || {};
  return `
    <div class="card p-6 flex flex-col">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-bold text-lg text-white">${C.escapeHtml(p.name)}</h3>
        ${p.popular ? '<span class="badge badge-green">Popular</span>' : ''}
      </div>
      <p class="text-sm text-muted mb-4">${C.escapeHtml(p.short_description || p.description || '')}</p>
      <div class="text-3xl font-black mb-1">${C.formatMoney(p.price, p.currency)}<span class="text-sm text-muted font-normal">/${p.billing_cycle}</span></div>
      <ul class="text-sm text-muted space-y-1.5 my-4 flex-1">
        <li>💾 RAM: ${resources.ram_mb || 0} MB</li>
        <li>⚡ CPU: ${resources.cpu || 0}%</li>
        <li>🗄️ Storage: ${resources.storage_mb || 0} MB</li>
        ${(p.features || []).map(f => `<li>✓ ${C.escapeHtml(f)}</li>`).join('')}
      </ul>
      <button data-order-plan="${p.id}" class="btn-primary w-full py-2.5 rounded-xl text-sm mt-auto">Order Through Discord</button>
    </div>
  `;
}
