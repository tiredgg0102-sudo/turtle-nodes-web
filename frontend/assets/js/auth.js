import { Api } from './api.js';

let _user = null;
let _listeners = [];

export const Auth = {
  get user() { return _user; },
  get isAuthed() { return !!_user; },
  get isAdmin() { return _user && (_user.role === 'admin' || _user.role === 'staff'); },
  onChange(cb) { _listeners.push(cb); },
  notify() { _listeners.forEach(cb => cb(_user)); },
  async load() {
    try { _user = await Api.get('/auth/me'); }
    catch { _user = null; }
    this.notify();
    return _user;
  },
  async login(email, password) {
    const res = await Api.post('/auth/login', { email, password });
    _user = res.user || await Api.get('/auth/me');
    this.notify();
    return _user;
  },
  async register(email, username, password) {
    await Api.post('/auth/register', { email, username, password });
    _user = await Api.get('/auth/me');
    this.notify();
    return _user;
  },
  async logout() {
    try { await Api.post('/auth/logout', {}); } catch {}
    _user = null;
    this.notify();
  },
};
