# Discord Integration Guide

## Bot setup

1. Create an application at https://discord.com/developers/applications
2. Add a Bot user; enable **Message Content Intent** and **Server Members Intent**.
3. Copy the bot token to `DISCORD_BOT_TOKEN`.
4. Invite the bot to your server with the `applications.commands` and `bot` scopes.
5. Set `DISCORD_GUILD_ID` to your server ID.
6. Set `DISCORD_STAFF_ROLE_IDS` to comma-separated role IDs that may approve/reject orders.
7. Set `DISCORD_STAFF_CHANNEL_ID` for staff notifications.
8. Set `BOT_API_KEY` (shared with backend).

## Run the bot

```bash
cd bot
python -m pip install -r requirements.txt
python -m bot.main
```

Or via systemd (installed by the VPS installer).

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/order <reference>` | Submit an order for review | Everyone |
| `/order-info <reference>` | View order details | Staff |
| `/order-status <reference>` | Check order status | Everyone |
| `/order-approve <reference>` | Approve an order | Staff |
| `/order-reject <reference> [reason]` | Reject an order | Staff |
| `/customer-info <user_id>` | View customer | Staff |
| `/service-info <service_id>` | View service | Staff |
| `/announcement <title> <content>` | Post announcement | Staff |

## Ordering workflow

See README.md for the complete workflow.
