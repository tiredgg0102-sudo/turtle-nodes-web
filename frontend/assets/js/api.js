// API client with cookie-based auth + CSRF double-submit
const API_BASE = '/api/v1';

function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}

async function api(path, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (!['GET','HEAD','OPTIONS'].includes(method)) {
    const csrf = getCookie('csrf_token');
    if (csrf) headers['X-CSRF-TOKEN'] = csrf;
  }
  const res = await fetch(API_BASE + path, {
    credentials: 'include',
    ...options,
    method,
    headers,
    body: options.body ? (typeof options.body === 'string' ? options.body : JSON.stringify(options.body)) : undefined,
  });
  let data = null;
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) {
    try { data = await res.json(); } catch { data = null; }
  } else {
    data = await res.text();
  }
  if (!res.ok) {
    const err = new Error((data && data.message) || `HTTP ${res.status}`);
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

export const Api = {
  get: (p) => api(p),
  post: (p, b) => api(p, { method: 'POST', body: b }),
  patch: (p, b) => api(p, { method: 'PATCH', body: b }),
  put: (p, b) => api(p, { method: 'PUT', body: b }),
  del: (p) => api(p, { method: 'DELETE' }),
};

export function toast(message, type = 'info') {
  const c = document.getElementById('toast-container');
  if (!c) return;
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = message;
  c.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; setTimeout(() => el.remove(), 300); }, 3500);
}
