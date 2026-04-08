from datetime import datetime, timezone


def apply_decay(pet, now: datetime) -> dict:
    last = pet["last_interaction"]
    if last:
        last_dt = datetime.fromisoformat(last)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        hours = (now - last_dt).total_seconds() / 3600
    else:
        hours = 0

    hunger = pet["hunger"]
    happiness = pet["happiness"]

    hunger = min(100, hunger + round(hours * 5))
    happiness_decay = 3 if hunger > 50 else 1
    happiness = max(0, happiness - round(hours * happiness_decay))

    return {
        "hunger": hunger,
        "happiness": happiness,
        "level": pet["level"],
        "xp": pet["xp"],
        "health": pet["health"],
        "pet_name": pet["pet_name"],
    }


def apply_feed(pet: dict) -> dict:
    return {**pet, "hunger": max(0, pet["hunger"] - 30), "xp": pet["xp"] + 10}


def apply_play(pet: dict) -> dict:
    return {**pet, "happiness": min(100, pet["happiness"] + 20), "xp": pet["xp"] + 15}


def apply_pet(pet: dict) -> dict:
    return {**pet, "happiness": min(100, pet["happiness"] + 10), "xp": pet["xp"] + 5}


def check_levelup(pet: dict) -> tuple[int, int]:
    xp = pet["xp"]
    level = pet["level"]
    while xp >= 100:
        xp -= 100
        level += 1
    return level, xp


def stat_bar(value: int, maximum: int = 100, length: int = 10) -> str:
    filled = round(value / maximum * length)
    return "█" * filled + "░" * (length - filled)
