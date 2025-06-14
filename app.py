from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

app = Flask(__name__)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(os.environ.get("SHEET_NAME", "Catatan Keuangan")).sheet1

def parse_message(text):
    parts = text.strip().split()
    if len(parts) >= 3 and parts[0].lower() in ['pengeluaran', 'pemasukan']:
        kategori = parts[0].capitalize()
        try:
            jumlah = int(parts[1])
        except ValueError:
            return None
        keterangan = " ".join(parts[2:])
        return kategori, jumlah, keterangan
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message")
    sender = data.get("sender")

    result = parse_message(message)
    if result:
        kategori, jumlah, keterangan = result
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.append_row([waktu, kategori, jumlah, keterangan, sender])
        return {"reply": f"✅ Dicatat: {kategori} {jumlah} - {keterangan}"}, 200
    return {"reply": "❌ Format salah. Contoh: pengeluaran 10000 makan siang"}, 200

@app.route("/", methods=["GET"])
def home():
    return "Bot WA Keuangan Aktif 🚀"
if __name__ == "__main__":
    app.run(debug=True)

