# Troubleshooting

## Backend won't start

- Check `.env` exists and `SECRET_KEY`/`ENCRYPTION_KEY` are set.
- Run `python -m alembic upgrade head` to ensure DB schema is up to date.
- Check logs: `journalctl -u hosting-platform -n 50`.

## Database errors

- Delete `hosting.db` and re-run migrations (dev only): `rm hosting.db && python -m alembic upgrade head && python -m app.scripts.seed`.

## Pterodactyl connection fails

- Verify panel URL is reachable and uses HTTPS.
- Verify Application API key has required permissions.
- Check firewall/network.

## Discord bot not responding

- Verify `DISCORD_BOT_TOKEN` and `DISCORD_GUILD_ID`.
- Ensure slash commands are synced (bot logs "Synced commands").
- Check `BOT_API_KEY` matches between bot and backend.

## Provisioning fails

- Check Pterodactyl integration is configured and tested.
- Verify default node/location/nest/egg IDs are valid.
- Review provisioning logs in the database (`provisioning_logs` table).
- Retry from the admin orders page.

## CSRF errors

- Ensure frontend sends `X-CSRF-TOKEN` header matching the `csrf_token` cookie.
- Cookies must be sent with `credentials: 'include'`.

## Rate limiting

- Auth endpoints are rate-limited per IP. Wait 60 seconds and retry.
