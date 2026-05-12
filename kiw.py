import hashlib
import time
import multiprocessing
import queue
from curl_cffi import requests

# --- KONFIGURASI HEADER ---
HEADERS = {
    "authority": "api.rpow2.com",
    "accept": "*/*",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": "_ga=GA1.1.1944944012.1778383972; cf_clearance=mUnLplPPxlT5QRPchRW8fo4cKDowYMA1Tdm0OEmmzVY-1778568097-1.2.1.1-UEtK_7zxb8045CD4gQ6JGGdF_c8pe328ahy5V4HbvbvFSd9UVj6ACOhurSHgWgC_F66X.3kCQrLFISrIsP7SSqcQPqsapE0XEL7mJLUHvkNhiVwIDlkdOy_nHdyDzHmOQQlgLbEPxgFnQU7mvoy5hJxFN3hwRIHZctgm5fZ6lWbj83qUlztxXa2Zk5DfjPGqfY8r..xC.kGverooED2ABi7K_tvAZtntZbCrs4QMlxeaWcspl1GkXhvnHFqztVeRZgleHHPFMYD0w4qKnV8FJv71dGHOqbwV1sT6GxoMtzJP9w3xkqKM6.a8ZTSoEsv1AbH7ZwqF3OR9RkiGnrYHTw; _ga_3PG48F0MCP=GS2.1.s1778568098$o4$g1$t1778568218$j59$l0$h0; rpow_session=eyJlbWFpbCI6ImRlZnJpbW9pdG8yMDAxQGdtYWlsLmNvbSIsImV4cCI6MTc4MTE2MTU1M30.6uE82v3umm10WTBEAY7ln5jtV78H42qRgFW0JqBy2uA", 
    "origin": "https://rpow2.com",
    "referer": "https://rpow2.com/",
    "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}

def check_balance(session):
    print("\n[4] Mengecek Informasi Saldo (/me)...")
    try:
        resp = session.get("https://api.rpow2.com/me", timeout=45)
        
        if resp.status_code == 200:
            data = resp.json()
            balance_base = int(data.get("balance_base_units", 0))
            daily_remaining_base = int(data.get("daily_remaining_base_units", 0))
            
            balance_rpow = balance_base / 1_000_000_000
            daily_remaining_rpow = daily_remaining_base / 1_000_000_000
            
            print(f"[+] Total Saldo Saat Ini : {balance_rpow:.2f} RPOW")
            print(f"[+] Sisa Kuota Harian    : {daily_remaining_rpow:.2f} RPOW")
            
            return daily_remaining_base
        else:
            print(f"[-] Gagal mengecek saldo. Status: {resp.status_code}")
            return None
    except Exception as e:
        print(f"[-] Error saat mengecek saldo: {e}")
        return None

# --- FUNGSI WORKER UNTUK SETIAP CORE CPU ---
def mine_worker(core_id, num_cores, nonce_prefix, difficulty_bits, stop_event, result_queue):
    raw_prefix = bytes.fromhex(nonce_prefix)
    nonce = core_id  # Titik mulai berbeda untuk setiap core (0, 1, 2, 3)
    
    # Loop selama event 'stop' belum dipicu oleh core lain
    while not stop_event.is_set():
        # Mengeksekusi batch 50.000 nonce sebelum mengecek status stop_event
        # (Agar CPU tidak berat mengecek event terus-menerus)
        for _ in range(50000):
            nonce_bytes = nonce.to_bytes(8, byteorder='little')
            buffer = raw_prefix + nonce_bytes
            hash_bytes = hashlib.sha256(buffer).digest()
            
            tz = 0
            for byte in reversed(hash_bytes):
                if byte == 0:
                    tz += 8
                else:
                    tz += (byte & -byte).bit_length() - 1
                    break
                    
            # Jika ketemu, kirim hasilnya ke queue dan paksa keluar
            if tz >= difficulty_bits:
                result_queue.put(nonce)
                stop_event.set()
                return
                
            # Lompat sesuai jumlah core (misal 4 core: 0 -> 4 -> 8)
            nonce += num_cores

# --- FUNGSI MANAJER MULTIPROCESSING ---
def solve_pow_multicore(nonce_prefix, difficulty_bits, timeout_seconds=120):
    num_cores = multiprocessing.cpu_count()
    print(f"[*] Mulai Mining... Menggunakan {num_cores} Core CPU.")
    print(f"[*] Target: {difficulty_bits} bit nol (Timeout: {timeout_seconds}s)")
    
    # Antrian hasil dan sinyal berhenti antar core
    result_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()
    processes = []
    
    start_time = time.time()
    
    # Menjalankan worker di masing-masing core
    for i in range(num_cores):
        p = multiprocessing.Process(
            target=mine_worker, 
            args=(i, num_cores, nonce_prefix, difficulty_bits, stop_event, result_queue)
        )
        p.start()
        processes.append(p)
        
    solution_nonce = None
    
    try:
        # Menunggu jawaban dari queue maksimal selama timeout_seconds
        solution_nonce = result_queue.get(timeout=timeout_seconds)
        elapsed = time.time() - start_time
        print(f"\n[+] Ditemukan Nonce: {solution_nonce}")
        print(f"[+] Waktu Eksekusi : {elapsed:.2f} detik (Kecepatan Naik Drastis!)")
        
    except queue.Empty: # Jika lewat dari batas waktu
        print(f"\n[!] TIMEOUT ({timeout_seconds}s)! Pencarian terlalu lama, challenge di-skip.")
        
    finally:
        # Apapun yang terjadi (ketemu/timeout), hentikan semua core
        stop_event.set()
        for p in processes:
            p.join()
            
    return str(solution_nonce) if solution_nonce is not None else None

def run_auto_miner(session):
    print("\n[1] Meminta Challenge Baru...")
    try:
        resp_chal = session.post("https://api.rpow2.com/challenge", json={}, timeout=45)
        
        if resp_chal.status_code != 200:
            print(f"[-] Gagal dapat challenge. Code: {resp_chal.status_code}")
            print(f"[-] Response: {resp_chal.text}")
            return None
            
        challenge_data = resp_chal.json()
        
    except Exception as e:
        print(f"[-] Error request challenge: {e}")
        return None

    c_id = challenge_data['challenge_id']
    prefix = challenge_data['nonce_prefix']
    diff = challenge_data['difficulty_bits']
    
    print("\n[2] Eksekusi Proof of Work...")
    # Panggil fungsi multicore yang baru
    solution_nonce = solve_pow_multicore(prefix, diff)
    
    if solution_nonce is None:
        return "skip"
    
    print("\n[3] Mengirim hasil ke server (/mint)...")
    payload = {
        "challenge_id": c_id,
        "solution_nonce": solution_nonce
    }
    
    try:
        resp_mint = session.post("https://api.rpow2.com/mint", json=payload, timeout=45)
        
        if resp_mint.status_code == 200:
            print("[✓] SUKSES! Token berhasil di-mint.")
            return check_balance(session)
        else:
            print(f"[-] Response Error ({resp_mint.status_code}): {resp_mint.text}")
            return None
            
    except Exception as e:
        print(f"[-] Error saat minting: {e}")
        return None

def main_loop():
    session = requests.Session(impersonate="chrome110")
    session.headers.update(HEADERS)
    
    print("=== MEMULAI BOT TUYUL RPOW (MODE MULTI-CORE) ===")
    
    sisa_kuota = check_balance(session)
    if sisa_kuota is not None and sisa_kuota <= 0:
        print("\n[!] Kuota harian sudah habis sejak awal. Bot dihentikan.")
        return

    siklus = 1
    while True:
        print(f"\n{'='*40}")
        print(f"[*] SIKLUS MINING KE-{siklus}")
        print(f"{'='*40}")
        
        sisa_kuota = run_auto_miner(session)
        
        if sisa_kuota == "skip":
            print("\n[*] Langsung memuat ulang siklus berikutnya...")
            siklus += 1
            continue
        
        if sisa_kuota is not None and sisa_kuota <= 0:
            print("\n[!] Kuota harian telah mencapai batas maksimum (0).")
            print("[!] Menidurkan bot tuyul untuk hari ini...")
            break
            
        print("\n[*] Menunggu 10 detik sebelum siklus berikutnya...")
        time.sleep(10)
        siklus += 1

if __name__ == "__main__":
    # Penting: Baris freeze_support() berguna jika Anda menjalankan ini di Windows suatu saat nanti
    multiprocessing.freeze_support()
    main_loop()