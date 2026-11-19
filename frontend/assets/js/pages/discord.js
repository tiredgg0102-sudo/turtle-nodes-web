import * as C from '../components.js';

export async function render(container) {
  container.innerHTML = `
    <div class="max-w-3xl mx-auto px-6 py-16 text-center">
      <div class="text-6xl mb-6">💬</div>
      <h1 class="text-4xl font-bold mb-4">Join Our <span class="gradient-text">Discord</span></h1>
      <p class="text-muted mb-8 max-w-xl mx-auto">All hosting orders are processed through our Discord server. Connect with staff, track your orders, and get support.</p>
      <div class="glass rounded-2xl p-8 mb-6">
        <h3 class="font-semibold mb-3">How ordering works</h3>
        <ol class="text-left text-sm text-muted space-y-2 max-w-md mx-auto">
          <li>1. Browse plans on the website.</li>
          <li>2. Click "Order Through Discord" on a plan.</li>
          <li>3. An order reference is created.</li>
          <li>4. Join our Discord and use <code class="text-primary">/order &lt;reference&gt;</code>.</li>
          <li>5. Staff review and approve your order.</li>
          <li>6. Your service is provisioned automatically.</li>
        </ol>
      </div>
      <a href="https://discord.gg/" target="_blank" rel="noopener" class="btn-primary px-8 py-3 rounded-xl inline-block">Open Discord</a>
    </div>
  `;
}
