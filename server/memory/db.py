"""SQLite 存储：对话记录、订单、画像缓存。

只存必要字段，**不存手机号、Token、收货地址等个人信息**。
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


class DB:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def _init(self):
        with self._conn() as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT,
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    order_id TEXT,
                    store_name TEXT,
                    items TEXT,
                    amount REAL,
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS profile (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_msg_session ON messages(session_id);
                """
            )

    # ---------------- 对话

    def add_message(self, session_id: str, role: str, content: str):
        with self._conn() as c:
            c.execute(
                "INSERT INTO messages(session_id, role, content, created_at)"
                " VALUES (?,?,?,?)",
                (session_id, role, content, time.time()),
            )

    def get_messages(self, session_id: str, limit: int = 12) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT role, content FROM messages WHERE session_id=?"
                " ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def clear_messages(self, session_id: str):
        with self._conn() as c:
            c.execute("DELETE FROM messages WHERE session_id=?", (session_id,))

    # ---------------- 订单

    def save_order(self, session_id: str, order_id: str, store_name: str,
                   items: list[str], amount: float | None):
        with self._conn() as c:
            c.execute(
                "INSERT INTO orders(session_id, order_id, store_name, items, amount,"
                " created_at) VALUES (?,?,?,?,?,?)",
                (session_id, order_id, store_name, json.dumps(items, ensure_ascii=False),
                 amount, time.time()),
            )

    # ---------------- 画像缓存

    def set_profile(self, key: str, value):
        with self._conn() as c:
            c.execute(
                "INSERT INTO profile(k, v, updated_at) VALUES (?,?,?)"
                " ON CONFLICT(k) DO UPDATE SET v=excluded.v, updated_at=excluded.updated_at",
                (key, json.dumps(value, ensure_ascii=False), time.time()),
            )

    def get_profile(self, key: str, max_age: float = 1800):
        with self._conn() as c:
            row = c.execute("SELECT v, updated_at FROM profile WHERE k=?", (key,)).fetchone()
        if not row:
            return None
        if max_age and time.time() - row["updated_at"] > max_age:
            return None
        return json.loads(row["v"])
