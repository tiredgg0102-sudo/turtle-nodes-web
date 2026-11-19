# Administrator Guide

## Admin Dashboard

Access at `/#/admin` after logging in with an admin account.

### Modules

- **Dashboard** — real-time stats (customers, services, orders, tickets, failures).
- **Customers** — view, search, suspend/restore, manage roles.
- **Services** — view all provisioned services.
- **Orders** — view, filter, approve/reject, retry provisioning.
- **Hosting Plans** — create, edit, delete, enable/disable plans.
- **Pterodactyl Integration** — configure panel URL, API key, defaults; test connection.
- **Discord Integration** — view bot configuration status.
- **Tickets** — view, reply, assign, close/reopen.
- **Announcements** — publish updates to all customers.
- **Activity Logs** — audit trail of admin actions.
- **System Settings** — platform configuration overview.
- **Security** — security posture overview.
- **Jobs** — background job information.
- **Diagnostics** — health checks.

## Order approval workflow

1. Customer creates an order on the website.
2. Customer submits the order reference via Discord (`/order <reference>`).
3. Staff review and approve/reject via `/order-approve` or `/order-reject`, or via the admin dashboard.
4. Approved orders enter the provisioning queue.
5. The provisioning engine creates the service via Pterodactyl.
6. Customer receives a notification and the service appears in their dashboard.

## Security notes

- Never share the Application API key.
- Rotate `SECRET_KEY` and `ENCRYPTION_KEY` carefully (will invalidate sessions/encrypted data).
- Use HTTPS in production (`COOKIE_SECURE=true`).
- Review audit logs regularly.
