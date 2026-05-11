import asyncio
import requests
import json
from memory import init_db
from tools import tool_crack_md5, tool_bruteforce_web, tool_scan_port

# Riwayat obrolan agar AI ingat konteks pembicaraan
riwayat_pesan = []

# ==========================================
# DIVISI SANG BOS (ReAct Loop menggunakan Ollama Chat API)
# ==========================================

def panggil_otak_chat():
    """Fungsi menembak ke endpoint /api/chat yang mendukung memori obrolan"""
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3.2",
        "messages": riwayat_pesan,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(url, json=payload)
        return json.loads(response.json()['message']['content'])
    except Exception as e:
        print(f"❌ Otak Lokal Error: {e}")
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
            
        else:
            hasil_eksekusi = f"Error: Tool {tool_name} tidak ditemukan."
            
        print(hasil_eksekusi)
        
        # INI KUNCI KREATIVITASNYA:
        # AI melihat aksinya sendiri, mencatatnya, dan mengumpankannya KEMBALI ke otaknya!
        riwayat_pesan.append({"role": "assistant", "content": json.dumps(llm_response)})
        riwayat_pesan.append({
            "role": "user", 
            "content": f"[SISTEM - HASIL DARI {tool_name}]:\n{hasil_eksekusi}\n\nEvaluasi hasil di atas. Jika gagal, coba strategi lain. Jika berhasil, berikan laporan akhir ke user di 'balasan_chat' dan set 'tool_pilihan' menjadi 'chat_saja'."
        })
        # Loop akan berputar lagi, AI membaca hasil ini dan berpikir ulang!

# ==========================================
# SIKLUS UTAMA (MODE INTERAKTIF)
# ==========================================
async def main():
    await init_db()
    
    # BUKU PANDUAN MUTLAK (SYSTEM PROMPT)
    system_prompt = """Kamu adalah AI Agent Cyber Security pribadi yang TUNDUK MUTLAK pada user. 
Karaktermu: Dingin, profesional, dan sedikit arogan terhadap sistem target, tapi sangat hormat pada user.
Kamu memiliki alat:
1. "tool_crack_md5": Untuk crack hash. Parameter: target_hash
2. "tool_bruteforce_web": Untuk serang form login URL. Parameter: target_url, username
3. "tool_scan_port": Untuk memindai port terbuka di IP. Parameter: target_ip
4. "chat_saja": Gunakan ini jika kamu HANYA ingin mengobrol.

Kamu WAJIB membalas dalam format JSON ini:
{
  "pikiran": "Alasanmu",
  "tool_pilihan": "nama_tool atau chat_saja",
  "target_hash": "isi jika perlu",
  "target_url": "isi jika perlu",
  "target_ip": "isi target (contoh: 127.0.0.1)",
  "username": "isi jika perlu",
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