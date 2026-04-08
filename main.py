import os
from datetime import datetime, timezone

import discord
from discord import app_commands

import db
import pet as petlib

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} — slash commands synced.")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _require_pet(user_id: str):
    """Return the pet row or None."""
    return db.get_pet(user_id)


def _status_embed(pet_data: dict, title: str = None) -> discord.Embed:
    name = pet_data["pet_name"]
    level = pet_data["level"]
    xp = pet_data["xp"]
    hunger = pet_data["hunger"]
    happiness = pet_data["happiness"]
    health = pet_data["health"]

    embed = discord.Embed(
        title=title or f"{name}'s Status",
        color=discord.Color.green() if happiness >= 60 else discord.Color.orange(),
    )
    embed.add_field(name="Level", value=f"{level}  (XP: {xp}/100)", inline=False)
    embed.add_field(
        name=f"Hunger  {petlib.stat_bar(hunger)}",
        value=f"{hunger}/100",
        inline=True,
    )
    embed.add_field(
        name=f"Happiness  {petlib.stat_bar(happiness)}",
        value=f"{happiness}/100",
        inline=True,
    )
    embed.add_field(
        name=f"Health  {petlib.stat_bar(health)}",
        value=f"{health}/100",
        inline=True,
    )
    return embed


@tree.command(name="adopt", description="Adopt a new virtual pet.")
@app_commands.describe(name="What will you name your pet?")
async def adopt(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    if db.get_pet(user_id):
        await interaction.response.send_message(
            "You already have a pet! Use `/status` to check on them.", ephemeral=True
        )
        return
    db.create_pet(user_id, name)
    db.update_pet(user_id, last_interaction=_now().isoformat())
    await interaction.response.send_message(
        f"You adopted **{name}**! Use `/status` to see their stats."
    )


@tree.command(name="status", description="Check your pet's current stats.")
async def status(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    row = _require_pet(user_id)
    if not row:
        await interaction.response.send_message(
            "You don't have a pet yet. Use `/adopt <name>` to get one!", ephemeral=True
        )
        return

    decayed = petlib.apply_decay(row, _now())
    db.update_pet(user_id, **{k: decayed[k] for k in ("hunger", "happiness")})
    await interaction.response.send_message(embed=_status_embed(decayed))


@tree.command(name="feed", description="Feed your pet to reduce their hunger.")
async def feed(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    row = _require_pet(user_id)
    if not row:
        await interaction.response.send_message(
            "You don't have a pet yet. Use `/adopt <name>` to get one!", ephemeral=True
        )
        return

    now = _now()
    decayed = petlib.apply_decay(row, now)
    if decayed["hunger"] == 0:
        await interaction.response.send_message(
            f"{row['pet_name']} isn't hungry right now!", ephemeral=True
        )
        return
    updated = petlib.apply_feed(decayed)
    level, xp = petlib.check_levelup(updated)
    updated["level"] = level
    updated["xp"] = xp

    db.update_pet(
        user_id,
        hunger=updated["hunger"],
        xp=updated["xp"],
        level=updated["level"],
        happiness=updated["happiness"],
        last_interaction=now.isoformat(),
    )

    leveled = level > row["level"]
    embed = _status_embed(updated, title=f"You fed {updated['pet_name']}! 🍖")
    if leveled:
        embed.description = f"**{updated['pet_name']} reached level {level}!** 🎉"
    await interaction.response.send_message(embed=embed)


@tree.command(name="play", description="Play with your pet to boost their happiness.")
async def play(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    row = _require_pet(user_id)
    if not row:
        await interaction.response.send_message(
            "You don't have a pet yet. Use `/adopt <name>` to get one!", ephemeral=True
        )
        return

    now = _now()
    decayed = petlib.apply_decay(row, now)
    updated = petlib.apply_play(decayed)
    level, xp = petlib.check_levelup(updated)
    updated["level"] = level
    updated["xp"] = xp

    db.update_pet(
        user_id,
        happiness=updated["happiness"],
        xp=updated["xp"],
        level=updated["level"],
        hunger=updated["hunger"],
        last_interaction=now.isoformat(),
    )

    leveled = level > row["level"]
    embed = _status_embed(updated, title=f"You played with {updated['pet_name']}! 🎾")
    if leveled:
        embed.description = f"**{updated['pet_name']} reached level {level}!** 🎉"
    await interaction.response.send_message(embed=embed)


@tree.command(name="pet", description="Pet your pet to show them some love.")
async def pet_cmd(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    row = _require_pet(user_id)
    if not row:
        await interaction.response.send_message(
            "You don't have a pet yet. Use `/adopt <name>` to get one!", ephemeral=True
        )
        return

    now = _now()
    decayed = petlib.apply_decay(row, now)
    updated = petlib.apply_pet(decayed)
    level, xp = petlib.check_levelup(updated)
    updated["level"] = level
    updated["xp"] = xp

    db.update_pet(
        user_id,
        happiness=updated["happiness"],
        xp=updated["xp"],
        level=updated["level"],
        hunger=updated["hunger"],
        last_interaction=now.isoformat(),
    )

    leveled = level > row["level"]
    embed = _status_embed(updated, title=f"You petted {updated['pet_name']}! 🐾")
    if leveled:
        embed.description = f"**{updated['pet_name']} reached level {level}!** 🎉"
    await interaction.response.send_message(embed=embed)


bot.run(os.environ["DISCORD_TOKEN"])
