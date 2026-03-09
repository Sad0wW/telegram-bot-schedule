from typing import Optional

import aiosqlite
import logging

db: Optional[aiosqlite.Connection] = None

async def init_db():
    global db

    db = await aiosqlite.connect("./database.db")
    await db.execute("PRAGMA foreign_keys = ON;")

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            grade_id INTEGER NOT NULL,
            is_admin INTEGER DEFAULT 0 NOT NULL,
            FOREIGN KEY(grade_id) REFERENCES grades(id) ON DELETE CASCADE
        );
                           
        INSERT INTO grades(name) SELECT *
        FROM (VALUES 
            ('-'), ('1А'), ('1Б'), ('1В'), ('1Г'), 
            ('2А'), ('2Б'), ('2В'), ('2Г'),
            ('3А'), ('3Б'), ('3В'), ('3Г'),
            ('4А'), ('4Б'), ('4В'), ('4Г'),
            ('5А'), ('5Б'), ('5В'), ('5Г'), ('5Д'),
            ('6А'), ('6Б'), ('6В'), ('6Г'),
            ('7А'), ('7Б'), ('7В'), ('7Г'),
            ('8А'), ('8Б'), ('8В'), ('8Г'),
            ('9А'), ('9Б'), ('9В'), ('9Г'),
            ('10А'), ('10Б'), ('11А'), ('11Б')
        )
        WHERE NOT EXISTS (SELECT 1 FROM grades);
    """)

    await db.commit()

    logging.info("Database initialized")

    return db

async def close_db():
    global db

    if db:
        await db.close()

def get_db() -> aiosqlite.Connection:
    return db

async def is_registered(id: int) -> bool:
    user = await db.execute("SELECT * FROM users WHERE id = ?", (id,))
    return True if (await user.fetchone()) else False

async def is_admin(id: int) -> bool:
    user_cur = await db.execute("SELECT is_admin FROM users WHERE id = ?", (id,))
    user_rows = await user_cur.fetchone()

    return user_rows and user_rows[0] == 1

async def is_root(id: int) -> bool:
    user_cur = await db.execute("SELECT rowid FROM users WHERE id = ?", (id,))
    user_rows = await user_cur.fetchone()

    return True if user_rows and user_rows[0] == 1 else False