import asyncio
import requests
import json
from memory import init_db
from tools import tool_crack_md5, tool_bruteforce_web, tool_scan_port, tool_baca_panduan, tool_analisis_keamanan, tool_eksekusi_python

# Riwayat obrolan agar AI ingat konteks pembicaraan
riwayat_pesan = []

# ==========================================
# DIVISI SANG BOS (ReAct Loop menggunakan Ollama Chat API)
# ==========================================

def panggil_otak_chat():
    url = "https://cautious-eureka-5vq7w4q45q9w2v5p4-11434.app.github.dev/api/chat" # Tetap gunakan URL Anda
    
    payload = {
        "model": "llama3.2",
        "messages": riwayat_pesan,
        "stream": True,  # <--- 1. UBAH INI JADI TRUE
        "format": "json"
    }
    
    try:
        # 2. Tambahkan stream=True di sini agar Python tidak menunggu sampai selesai
        response = requests.post(url, json=payload, stream=True)
        
        if response.status_code != 200:
            print(f"🚨 [KONEKSI GAGAL]: {response.status_code} - {response.text}")
            return None

        teks_lengkap = ""
        # 3. Menangkap potongan data kata-demi-kata agar GitHub tidak Timeout
        for baris in response.iter_lines():
            if baris:
                data = json.loads(baris)
                if "error" in data:
                    print(f"\n🚨 [OLLAMA ERROR]: {data['error']}")
                    return None
                
                potongan_teks = data.get("message", {}).get("content", "")
                teks_lengkap += potongan_teks
                
        # 4. Setelah AI selesai berpikir sepenuhnya, jadikan JSON
        return json.loads(teks_lengkap)
        
    except Exception as e:
        print(f"❌ Python Parsing Error: {e}")
        return None

async def siklus_agen(input_user: str):
    # Masukkan perintah Anda ke riwayat ingatan AI
    riwayat_pesan.append({"role": "user", "content": input_user})
    
    # LOOP KREATIVITAS (ReAct): AI bisa berpikir berkali-kali sebelum membalas Anda
    while True:
        print("🧠 [SANG BOS]: Sedang berpikir...")
        llm_response = panggil_otak_chat()
        
        if not llm_response:
            break
            
        pikiran = llm_response.get("pikiran", "")
        tool_name = llm_response.get("tool_pilihan", "chat_saja")
        balasan = llm_response.get("balasan_chat", "")
        
        # 1. Tampilkan apa yang sedang dipikirkan AI (Monolog Internal)
        print(f"💭 [PIKIRAN]: {pikiran}")
        
        # 2. Jika AI hanya ingin ngobrol (tidak pakai tool)
        if tool_name == "chat_saja":
            print(f"🤖 [SANG BOS]: {balasan}")
            # Simpan balasan ini ke ingatan AI, lalu HENTIKAN loop karena misi selesai
            riwayat_pesan.append({"role": "assistant", "content": json.dumps(llm_response)})
            break
            
        # 3. Jika AI memutuskan menggunakan Tool
        print(f"⚙️ [MEMANGGIL ALAT]: {tool_name}")
        hasil_eksekusi = ""
        
        if tool_name == "tool_crack_md5":
            target = llm_response.get("target_hash", "")
            words = ["admin", "12345", "password", "jamal123", "rahasia", "1"]
            hasil_eksekusi = await tool_crack_md5(target, words)
            
        elif tool_name == "tool_bruteforce_web":
            target_url = llm_response.get("target_url", "")
            username = llm_response.get("username", "admin") 
            words = ["admin", "12345", "password", "jamal123", "rahasia", "1"]
            hasil_eksekusi = await tool_bruteforce_web(target_url, username, words)

        elif tool_name == "tool_scan_port":
            target_ip = llm_response.get("target_ip", "")
            hasil_eksekusi = await tool_scan_port(target_ip)

        elif tool_name == "tool_analisis_keamanan":
            target_url = llm_response.get("target_url", "")
            hasil_eksekusi = await tool_analisis_keamanan(target_url)

        elif tool_name == "tool_eksekusi_python":
            kode_python = llm_response.get("kode_python", "")
            hasil_eksekusi = await tool_eksekusi_python(kode_python)

        elif tool_name == "tool_baca_panduan":
            pertanyaan = llm_response.get("pertanyaan", "")
            hasil_eksekusi = await tool_baca_panduan(pertanyaan)
            
        else:
            hasil_eksekusi = f"Error: Tool {tool_name} tidak ditemukan."
            
        print(hasil_eksekusi)
        
        # LOGIKA BARU: Mencegah Information Overload!
        # Jika teksnya lebih dari 500 karakter, kita potong agar AI tidak pingsan membacanya.
        if len(hasil_eksekusi) > 500:
            hasil_laporan_ke_bos = hasil_eksekusi[:500] + "\n\n... [TEKS DIPOTONG KARENA TERLALU PANJANG] ..."
        else:
            hasil_laporan_ke_bos = hasil_eksekusi

        # Memasukkan ingatan ke AI
        riwayat_pesan.append({"role": "assistant", "content": json.dumps(llm_response)})
        riwayat_pesan.append({
            "role": "user", 
            "content": f"[SISTEM - HASIL DARI {tool_name}]:\n{hasil_laporan_ke_bos}\n\nEvaluasi hasil di atas. Jika gagal, coba strategi lain. Jika berhasil, berikan laporan akhir ke user di 'balasan_chat' dan set 'tool_pilihan' menjadi 'chat_saja'."
        })
        # Loop akan berputar lagi, AI membaca hasil ini dan berpikir ulang!

# ==========================================
# SIKLUS UTAMA (MODE INTERAKTIF)
# ==========================================
async def main():
    await init_db()
    
    system_prompt = """Kamu adalah AI Agent Cyber Security pribadi yang TUNDUK MUTLAK pada user. 
Karaktermu: Dingin, profesional, dan sedikit arogan terhadap sistem target, tapi sangat hormat pada user.
Kamu memiliki alat:
1. "tool_crack_md5": Untuk crack hash. Parameter: target_hash
2. "tool_bruteforce_web": Untuk serang web. Parameter: target_url, username
3. "tool_scan_port": Untuk memindai IP. Parameter: target_ip
4. "tool_baca_panduan": Untuk mencari tahu trik, password default, atau kerentanan jika kamu kebingungan. Parameter: pertanyaan
5. "tool_analisis_keamanan": Untuk melakukan audit keamanan pada URL target. Parameter: target_url
6. "tool_eksekusi_python": Untuk MENULIS dan MENJALANKAN kodemu sendiri. Parameter: kode_python (HANYA BERISI STRING KODE MURNI, TANPA TANDA KUTIP MARKDOWN/BACKTICK).
7. "chat_saja": Gunakan jika misi selesai atau hanya ingin ngobrol.


Kamu WAJIB membalas dalam format JSON ini:
{
  "pikiran": "Alasanmu",
  "tool_pilihan": "nama_tool atau chat_saja",
  "target_hash": "isi jika perlu",
  "target_url": "isi jika perlu",
  "target_ip": "isi jika perlu",
  "username": "isi jika perlu",
  "pertanyaan": "isi pertanyaan untuk dicari di panduan (HANYA jika memilih tool_baca_panduan)",
  "target_url": "isi jika perlu",
  "kode_python": "isi dengan kodemu di sini (ingat gunakan escape character \n untuk baris baru) jika menggunakan tool_eksekusi_python",
  "balasan_chat": "Pesanmu untuk Bos"
}"""

    # Injeksi karakter ke ingatan pertama
    riwayat_pesan.append({"role": "system", "content": system_prompt})
    
    print("\n" + "="*50)
    print("🤖 AI AGENT CYBER SECURITY AKTIF (ReAct Mode)")
    print("Ketik 'exit' untuk mematikan sistem.")
    print("="*50 + "\n")
    
    while True:
        try:
            perintah_user = input("👤 [ANDA]: ")
            if perintah_user.lower() in ['exit', 'quit']:
                print("👋 Mematikan agen...")
                break
            if not perintah_user.strip(): continue
                
            await siklus_agen(perintah_user)
            print("-" * 50)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asyncio.run(main())