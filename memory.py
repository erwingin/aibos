import aiosqlite

DB_NAME = "cyber_agent.db"

async def init_db():
    """Membangun buku catatan (database) jika belum ada."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Tabel untuk mencatat hasil cracking hash
        await db.execute('''
            CREATE TABLE IF NOT EXISTS hash_log (
                target_hash TEXT PRIMARY KEY,
                cracked_password TEXT,
                status TEXT
            )
        ''')
        # Tabel untuk mencatat memori/logika umum AI
        await db.execute('''
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kejadian TEXT,
                waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
    print("💾 Buku catatan (Database) berhasil disiapkan!")

# Fungsi bantuan untuk AI membaca memori hash
async def cek_memori_hash(target_hash):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT cracked_password FROM hash_log WHERE target_hash = ? AND status = 'SUCCESS'", (target_hash,))
        row = await cursor.fetchone()
        return row[0] if row else None