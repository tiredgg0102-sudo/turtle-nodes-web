# API Reference

Base URL: `/api/v1`. Authentication via HttpOnly cookie (`access_token`) + CSRF header (`X-CSRF-TOKEN`) for state-changing requests. Bot endpoints use `X-Bot-Key` header.

## Health

- `GET /api/health` — public health check
- `GET /api/v1/system/health` — admin diagnostics

## Auth

- `POST /api/v1/auth/register` — register
- `POST /api/v1/auth/login` — login
- `POST /api/v1/auth/logout` — logout
- `GET /api/v1/auth/me` — current user
- `POST /api/v1/auth/refresh` — refresh token

## Users

- `GET /api/v1/users` (admin)
- `GET /api/v1/users/{id}`
- `PATCH /api/v1/users/me`
- `PATCH /api/v1/users/{id}/role` (admin)
- `PATCH /api/v1/users/{id}/status` (admin)

## Plans

- `GET /api/v1/plans` (optional `?active_only=true`)
- `GET /api/v1/plans/{id}`
- `POST /api/v1/plans` (admin)
- `PATCH /api/v1/plans/{id}` (admin)
- `DELETE /api/v1/plans/{id}` (admin)

## Categories

- `GET /api/v1/categories`
- `POST /api/v1/categories` (admin)
- `PATCH /api/v1/categories/{id}` (admin)
- `DELETE /api/v1/categories/{id}` (admin)

## Orders

- `POST /api/v1/orders` — create order
- `GET /api/v1/orders` — list (own or all for staff)
- `GET /api/v1/orders/{id}`
- `PATCH /api/v1/orders/{id}/review` (staff) — approve/reject
- `PATCH /api/v1/orders/{id}/status` (admin)

## Services

- `GET /api/v1/services`
- `GET /api/v1/services/{id}`
- `POST /api/v1/services/{id}/power` — start/stop/restart

## Tickets

- `POST /api/v1/tickets`
- `GET /api/v1/tickets`
- `GET /api/v1/tickets/{id}`
- `GET /api/v1/tickets/{id}/messages`
- `POST /api/v1/tickets/{id}/messages`
- `PATCH /api/v1/tickets/{id}` (staff)

## Announcements

- `GET /api/v1/announcements`
- `POST /api/v1/announcements` (staff)
- `PATCH /api/v1/announcements/{id}` (staff)

## Pterodactyl

- `GET/POST/PATCH /api/v1/pterodactyl/config` (admin)
- `POST /api/v1/pterodactyl/config/test` (admin)
- `GET /api/v1/pterodactyl/*` (admin) — panel resources
- `POST /api/v1/pterodactyl/client/connect` — connect customer account
- `POST /api/v1/pterodactyl/client/revoke`
- `GET /api/v1/pterodactyl/client/servers`
- `GET /api/v1/pterodactyl/client/servers/{id}`
- `GET /api/v1/pterodactyl/client/servers/{id}/resources`
- `POST /api/v1/pterodactyl/client/servers/{id}/power`

## Notifications

- `GET /api/v1/notifications`
- `POST /api/v1/notifications/{id}/read`

## Admin

- `GET /api/v1/admin/overview`
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/recent-activities`

## Discord

- `GET /api/v1/discord/config` (admin)

## Bot (X-Bot-Key)

- `GET /api/v1/bot/orders/{reference}`
- `GET /api/v1/bot/orders?status=`
- `POST /api/v1/bot/orders/{reference}/approve`
- `POST /api/v1/bot/orders/{reference}/reject`
- `GET /api/v1/bot/customers/{id}`
- `GET /api/v1/bot/customers/by-discord/{discord_id}`
- `GET /api/v1/bot/services/{id}`
