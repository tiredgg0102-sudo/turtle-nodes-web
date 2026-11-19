# Pterodactyl Integration Guide

## Application API (admin)

1. In Pterodactyl, go to **Admin → Application API**.
2. Create a new API key with the required permissions (users, servers, nodes, locations, nests, eggs).
3. Set `PTERODACTYL_URL` to your panel URL (e.g. `https://panel.example.com`).
4. Set `PTERODACTYL_APP_API_KEY` to the key.
5. Or configure via Admin Dashboard → Pterodactyl Integration → Test Connection.

The Application API key is stored encrypted at rest and never exposed to the frontend.

## Client API (customer)

Customers connect their own Client API key from their dashboard:
1. In Pterodactyl, go to **Account → API Credentials**.
2. Create a new API key.
3. In the Hosting Platform dashboard → Pterodactyl Connection, paste the key and panel URL.

The key is stored encrypted per-customer and used to power start/stop/restart and view server info.

## Provisioning

When an order is approved, the provisioning engine uses the Application API to create a server on the configured default node/location/nest/egg with the plan's resources. KVM VPS hosting requires a separate KVM provider (not included by default — Pterodactyl cannot provision KVM VMs).

## Supported operations

Application API: list users/servers/nodes/locations/nests/eggs, create/suspend/unsuspend/delete servers.
Client API: account info, list servers, server details, resources, power actions, console.
