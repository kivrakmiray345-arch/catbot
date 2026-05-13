"""
db.py — PostgreSQL database layer for Cat Bot.

Tables
------
users      : user_id, xp, level, coins, pity_counter, last_catch_time,
             daily (ISO timestamp), work (ISO timestamp)
inventory  : id (serial), user_id, cat_id, cat_name, rarity, caught_at
cats       : cat_id (serial), name, rarity, emoji

Connection is managed via a single asyncpg pool stored in the module-level
variable `pool`.  Call `init_db()` once during bot startup.
"""

import os
import asyncpg

pool: asyncpg.Pool | None = None


# ── Pool / init ───────────────────────────────────────────────────────────────

async def init_db() -> None:
    """Create the connection pool and ensure all tables exist."""
    global pool
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set! "
            "Add it in your Railway service Variables tab."
        )
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)
    await _create_tables()
    await _seed_cats()


async def _create_tables() -> None:
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       BIGINT PRIMARY KEY,
                xp            INTEGER     NOT NULL DEFAULT 0,
                level         INTEGER     NOT NULL DEFAULT 1,
                coins         INTEGER     NOT NULL DEFAULT 100,
                pity_counter  INTEGER     NOT NULL DEFAULT 0,
                last_catch_time TIMESTAMPTZ,
                daily         TEXT,
                work          TEXT
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id        SERIAL PRIMARY KEY,
                user_id   BIGINT      NOT NULL,
                cat_id    INTEGER     NOT NULL,
                cat_name  TEXT        NOT NULL,
                rarity    TEXT        NOT NULL,
                caught_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cats (
                cat_id  SERIAL PRIMARY KEY,
                name    TEXT NOT NULL,
                rarity  TEXT NOT NULL,
                emoji   TEXT NOT NULL
            );
        """)


async def _seed_cats() -> None:
    """Insert default cats if the table is empty."""
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM cats")
        if count and count > 0:
            return
        cats = [
            # Common
            ("Pamuk",      "Common", "🐱"),
            ("Tekir",      "Common", "🐈"),
            ("Minnoş",     "Common", "😺"),
            ("Boncuk",     "Common", "🐾"),
            ("Sarman",     "Common", "🐱"),
            ("Karabaş",    "Common", "🐈‍⬛"),
            ("Pamukcuk",   "Common", "😸"),
            ("Tüylü",      "Common", "🐱"),
            # Rare
            ("Gümüş",      "Rare",   "✨"),
            ("Kristal",    "Rare",   "💎"),
            ("Şimşek",     "Rare",   "⚡"),
            ("Fırtına",    "Rare",   "🌩️"),
            ("Ay Işığı",   "Rare",   "🌙"),
            # Epic
            ("Ejderha",    "Epic",   "🐉"),
            ("Efsane",     "Epic",   "👑"),
            ("Kozmik",     "Epic",   "🌌"),
        ]
        await conn.executemany(
            "INSERT INTO cats (name, rarity, emoji) VALUES ($1, $2, $3)",
            cats,
        )


# ── User helpers ──────────────────────────────────────────────────────────────

async def get_user(user_id: int) -> asyncpg.Record:
    """Return the user row, creating it with defaults if it doesn't exist."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )
        if row is None:
            await conn.execute(
                """
                INSERT INTO users (user_id, xp, level, coins, pity_counter,
                                   last_catch_time, daily, work)
                VALUES ($1, 0, 1, 100, 0, NULL, NULL, NULL)
                ON CONFLICT (user_id) DO NOTHING
                """,
                user_id,
            )
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
    return row


async def update_user(user_id: int, **kwargs) -> None:
    """Update arbitrary columns on the users table."""
    if not kwargs:
        return
    sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(kwargs))
    values = list(kwargs.values())
    async with pool.acquire() as conn:
        await conn.execute(
            f"UPDATE users SET {sets} WHERE user_id = $1",
            user_id, *values,
        )


async def get_coins(user_id: int) -> int:
    row = await get_user(user_id)
    return row["coins"]


async def add_coins(user_id: int, amount: int) -> int:
    """Add (or subtract) coins; returns new balance."""
    async with pool.acquire() as conn:
        await get_user(user_id)          # ensure row exists
        new_bal = await conn.fetchval(
            "UPDATE users SET coins = coins + $2 WHERE user_id = $1 RETURNING coins",
            user_id, amount,
        )
    return new_bal


# ── XP / Level helpers ────────────────────────────────────────────────────────

def xp_needed(level: int) -> int:
    """XP required to reach the *next* level from `level`."""
    return level * 100


async def add_xp(user_id: int, amount: int) -> tuple[int, int, bool]:
    """
    Add XP to a user.  Returns (new_xp, new_level, leveled_up).
    Handles multi-level jumps.
    """
    row = await get_user(user_id)
    xp = row["xp"] + amount
    level = row["level"]
    leveled_up = False

    while xp >= xp_needed(level):
        xp -= xp_needed(level)
        level += 1
        leveled_up = True

    await update_user(user_id, xp=xp, level=level)
    return xp, level, leveled_up


# ── Catch cooldown ────────────────────────────────────────────────────────────

async def get_last_catch(user_id: int):
    row = await get_user(user_id)
    return row["last_catch_time"]


async def set_last_catch(user_id: int, ts) -> None:
    await update_user(user_id, last_catch_time=ts)


# ── Pity counter ──────────────────────────────────────────────────────────────

async def get_pity(user_id: int) -> int:
    row = await get_user(user_id)
    return row["pity_counter"]


async def increment_pity(user_id: int) -> int:
    async with pool.acquire() as conn:
        await get_user(user_id)
        new_val = await conn.fetchval(
            "UPDATE users SET pity_counter = pity_counter + 1 "
            "WHERE user_id = $1 RETURNING pity_counter",
            user_id,
        )
    return new_val


async def reset_pity(user_id: int) -> None:
    await update_user(user_id, pity_counter=0)


# ── Inventory helpers ─────────────────────────────────────────────────────────

async def add_to_inventory(user_id: int, cat_id: int, cat_name: str, rarity: str) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO inventory (user_id, cat_id, cat_name, rarity) VALUES ($1, $2, $3, $4)",
            user_id, cat_id, cat_name, rarity,
        )


async def get_inventory(user_id: int, offset: int = 0, limit: int = 5):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT cat_name, rarity, caught_at FROM inventory "
            "WHERE user_id = $1 ORDER BY caught_at DESC LIMIT $2 OFFSET $3",
            user_id, limit, offset,
        )
    return rows


async def get_inventory_count(user_id: int) -> int:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM inventory WHERE user_id = $1", user_id
        )


async def get_rarity_breakdown(user_id: int) -> dict:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT rarity, COUNT(*) AS cnt FROM inventory "
            "WHERE user_id = $1 GROUP BY rarity",
            user_id,
        )
    return {r["rarity"]: r["cnt"] for r in rows}


# ── Cat catalogue helpers ─────────────────────────────────────────────────────

async def get_cats_by_rarity(rarity: str):
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT cat_id, name, emoji FROM cats WHERE rarity = $1", rarity
        )


# ── Legacy JSON migration ─────────────────────────────────────────────────────

async def migrate_json(json_data: dict) -> None:
    """
    One-time migration: import users from the old veriler.json format.
    Existing DB rows are left untouched (ON CONFLICT DO NOTHING).
    """
    async with pool.acquire() as conn:
        for user_id_str, info in json_data.items():
            try:
                uid = int(user_id_str)
            except ValueError:
                continue
            await conn.execute(
                """
                INSERT INTO users (user_id, coins, daily, work)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO NOTHING
                """,
                uid,
                info.get("para", 100),
                info.get("daily"),
                info.get("work"),
            )
