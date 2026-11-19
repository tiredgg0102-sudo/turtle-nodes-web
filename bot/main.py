"""Discord ordering bot entry point."""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import discord
from discord import app_commands
from discord.ext import commands

from bot.services.api_client import BackendClient

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
STAFF_ROLE_IDS = [int(x) for x in os.getenv("DISCORD_STAFF_ROLE_IDS", "").split(",") if x.strip().isdigit()]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
backend = BackendClient()


def is_staff(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    return any(r.id in STAFF_ROLE_IDS for r in member.roles)


@bot.event
async def on_ready():
    print(f"Bot ready as {bot.user} (ID: {bot.user.id})")
    if DISCORD_GUILD_ID:
        guild = discord.Object(id=int(DISCORD_GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"Synced commands to guild {DISCORD_GUILD_ID}")
    else:
        await bot.tree.sync()
        print("Synced global commands")


# ---------- /order ----------
@bot.tree.command(name="order", description="Submit an order using your order reference")
@app_commands.describe(reference="Your order reference from the website (e.g. HO-ABC123)")
async def order(interaction: discord.Interaction, reference: str):
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend.get_order(reference)
    except Exception as e:
        await interaction.followup.send(f"❌ Could not find order `{reference}`. Make sure the reference is correct.", ephemeral=True)
        return
    order = data["order"]
    customer = data.get("customer")
    embed = discord.Embed(title=f"Order {order['order_reference']}", color=discord.Color.blue())
    embed.add_field(name="Status", value=order["status"], inline=True)
    embed.add_field(name="Price", value=f"{order['total_price']} {order['currency']}", inline=True)
    if customer:
        embed.add_field(name="Customer", value=f"{customer['username']} ({customer['email']})", inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)
    # Notify staff channel if configured
    staff_channel_id = os.getenv("DISCORD_STAFF_CHANNEL_ID")
    if staff_channel_id:
        channel = bot.get_channel(int(staff_channel_id))
        if channel:
            await channel.send(f"🆕 Order submitted for review: `{reference}` by {customer['username'] if customer else 'unknown'}")


# ---------- /order-info ----------
@bot.tree.command(name="order-info", description="View order details (staff only)")
@app_commands.describe(reference="Order reference")
async def order_info(interaction: discord.Interaction, reference: str):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend.get_order(reference)
    except Exception as e:
        await interaction.followup.send(f"❌ Order not found: {reference}", ephemeral=True)
        return
    order = data["order"]
    customer = data.get("customer")
    embed = discord.Embed(title=f"Order {order['order_reference']}", color=discord.Color.gold())
    embed.add_field(name="Status", value=order["status"], inline=True)
    embed.add_field(name="Price", value=f"{order['total_price']} {order['currency']}", inline=True)
    embed.add_field(name="Created", value=order["created_at"], inline=False)
    if customer:
        embed.add_field(name="Customer", value=f"{customer['username']} ({customer['email']})", inline=False)
        if customer.get("discord_id"):
            embed.add_field(name="Discord ID", value=customer["discord_id"], inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)


# ---------- /order-status ----------
@bot.tree.command(name="order-status", description="Check the status of an order")
@app_commands.describe(reference="Order reference")
async def order_status(interaction: discord.Interaction, reference: str):
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend.get_order(reference)
    except Exception:
        await interaction.followup.send(f"❌ Order not found: {reference}", ephemeral=True)
        return
    await interaction.followup.send(f"Order `{reference}` status: **{data['order']['status']}**", ephemeral=True)


# ---------- /order-approve ----------
@bot.tree.command(name="order-approve", description="Approve an order (staff only)")
@app_commands.describe(reference="Order reference")
async def order_approve(interaction: discord.Interaction, reference: str):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        result = await backend.approve_order(reference)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to approve: {e}", ephemeral=True)
        return
    await interaction.followup.send(f"✅ Order `{reference}` approved. Provisioning started.", ephemeral=True)


# ---------- /order-reject ----------
@bot.tree.command(name="order-reject", description="Reject an order (staff only)")
@app_commands.describe(reference="Order reference", reason="Reason for rejection")
async def order_reject(interaction: discord.Interaction, reference: str, reason: str = "No reason provided"):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        result = await backend.reject_order(reference, reason)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to reject: {e}", ephemeral=True)
        return
    await interaction.followup.send(f"❌ Order `{reference}` rejected. Reason: {reason}", ephemeral=True)


# ---------- /customer-info ----------
@bot.tree.command(name="customer-info", description="View customer info (staff only)")
@app_commands.describe(user_id="Customer user ID")
async def customer_info(interaction: discord.Interaction, user_id: int):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend.get_customer(user_id)
    except Exception as e:
        await interaction.followup.send(f"❌ Customer not found.", ephemeral=True)
        return
    embed = discord.Embed(title=f"Customer {data['username']}", color=discord.Color.green())
    embed.add_field(name="Email", value=data["email"], inline=True)
    embed.add_field(name="Role", value=data["role"], inline=True)
    embed.add_field(name="Status", value=data["status"], inline=True)
    embed.add_field(name="Discord ID", value=data.get("discord_id") or "—", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)


# ---------- /service-info ----------
@bot.tree.command(name="service-info", description="View service info (staff only)")
@app_commands.describe(service_id="Service ID")
async def service_info(interaction: discord.Interaction, service_id: int):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        data = await backend.get_service(service_id)
    except Exception as e:
        await interaction.followup.send(f"❌ Service not found.", ephemeral=True)
        return
    embed = discord.Embed(title=f"Service {data['name']}", color=discord.Color.purple())
    embed.add_field(name="Status", value=data["status"], inline=True)
    embed.add_field(name="Server ID", value=str(data.get("pterodactyl_server_id") or "—"), inline=True)
    embed.add_field(name="RAM", value=f"{data['resources']['ram_mb']} MB", inline=True)
    await interaction.followup.send(embed=embed, ephemeral=True)


# ---------- /announcement ----------
@bot.tree.command(name="announcement", description="Post an announcement (staff only)")
@app_commands.describe(title="Title", content="Content")
async def announcement(interaction: discord.Interaction, title: str, content: str):
    if not is_staff(interaction.user):
        await interaction.response.send_message("❌ Staff only.", ephemeral=True)
        return
    await interaction.response.send_message(f"📢 **{title}**\n{content}")


def main():
    if not DISCORD_BOT_TOKEN:
        print("DISCORD_BOT_TOKEN not set. Bot will not start.")
        return
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
