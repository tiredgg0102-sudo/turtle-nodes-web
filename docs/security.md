# Security Audit

## Controls implemented

- **Password hashing**: bcrypt with configurable rounds (default 12). Never plaintext.
- **Authentication**: JWT access tokens in HttpOnly, Secure, SameSite cookies. 7-day expiry.
- **CSRF**: Double-submit cookie pattern on all state-changing endpoints.
- **Authorization**: Role-based (customer/staff/admin), enforced server-side on every request.
- **Rate limiting**: In-memory sliding window on login/register per IP.
- **Input validation**: Pydantic schemas on all endpoints.
- **SQL injection**: SQLAlchemy ORM with parameterized queries.
- **XSS**: React/Vanilla rendering escapes; Jinja not used for user content.
- **Credential encryption**: Fernet (symmetric) for Pterodactyl keys, Discord tokens, customer client API keys at rest.
- **Secret redaction**: Logging filter redacts secret-looking keys.
- **Audit logging**: Admin actions recorded with user, action, resource, IP.
- **Customer isolation**: Customers can only access their own services/orders/tickets.
- **Bot auth**: Dedicated `X-Bot-Key` header; bot key stored in env, never in frontend.

## Verified

- Cross-customer access returns 403.
- Frontend-only authorization is not trusted.
- API keys are never returned in full after saving (masked).
- No fake integration success reported.

## Recommendations for production

- Use PostgreSQL instead of SQLite.
- Enable HTTPS and `COOKIE_SECURE=true`.
- Run behind a firewall; expose only 80/443.
- Rotate `SECRET_KEY`/`ENCRYPTION_KEY` only with a migration plan.
- Enable email verification (`EMAIL_VERIFICATION_REQUIRED=true`).
- Configure SMTP for password reset emails.
- Set up regular database backups.
- Monitor audit logs and failed provisioning jobs.
