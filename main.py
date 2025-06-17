# === main.py ===
import os
import random
import io
import time
import requests
from PIL import Image
from telebot import TeleBot
from stats import load_stats, save_stats

TOKEN = '7981979424:AAHnX_Hbb1M3XTz7lv9fOWXbvfMRH-SeBZc'
bot = TeleBot(TOKEN)

MERGED_DIR = 'merged_photos'
os.makedirs(MERGED_DIR, exist_ok=True)

ANIMAL_DATA = {
    "images/dugong.jpg": "Dugong pemalas yang disayang semua orang 😴💙",
    "images/monyet.jpg": "Monyet, Kadang jadi monyet lebih bahagia daripada jadi orang dewasa",
    "images/singa.jpg": "Singa berani yang tak pernah mundur 🔥",
    "images/llama.jpg": "Llama yang suka ngeludah kalau kesel 🤭",
    "images/kambing.jpg": "Kambing kalem yang suka ngunyah rumput sambil bengong 🌾",
    "images/kuda.jpg": "Kuda, Selalu bergerak maju, seperti kuda di padang luas 🐎",
    "images/tupai.jpg": "Tupai lincah yang nggak bisa diam, selalu aktif ke sana kemari ⚡",
    "images/anjing.jpg": "Anjing penjaga yang siap pasang badan buat yang dicintai 🔥",
    "images/capung.jpg": "Seperti capung, kamu hadir sebentar tapi selalu meninggalkan kesan 🌟",
    "images/katak.jpg": "Katak paling rame di rawa—udah kayak MC kondangan 🐸🔊",
    "images/buaya.jpg": "Buaya darat kelas kakap—tampang tenang, tapi DM-nya rame"
    "images/ular.jpg": "Ular pendiam yang cuma gigit kalau kamu mulai duluan 🐍"
    "images/burhan.jpg": "Burung Hantu, Tahu segalanya, tapi gak semua harus dijawab... bijak ya"
}

def get_random_animal_image():
    path = random.choice(list(ANIMAL_DATA.keys()))
    caption = ANIMAL_DATA[path]
    return path, caption

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    print("📅 Menerima foto dari pengguna...")
    user_id = str(message.from_user.id)

    file_info = bot.get_file(message.photo[-1].file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
    response = requests.get(file_url)
    user_img = Image.open(io.BytesIO(response.content))

    animal_path, caption = get_random_animal_image()
    animal_img = Image.open(animal_path)
    animal_name = os.path.basename(animal_path)

    user_img = user_img.resize((300, 300))
    animal_img = animal_img.resize((300, 300))
    combined = Image.new('RGB', (600, 300))
    combined.paste(user_img, (0, 0))
    combined.paste(animal_img, (300, 0))

    timestamp = int(time.time())
    filename = f'combined_{timestamp}.jpg'
    save_path = os.path.join(MERGED_DIR, filename)
    combined.save(save_path)

    final_caption = f"📸 Seandainya kamu hewan, kamu akan menjadi:\n\n{caption}"
    bot.send_photo(message.chat.id, combined, caption=final_caption)

    bot.send_poll(
        chat_id=message.chat.id,
        question="Menurut kamu hewan ini cocok nggak?",
        options=["👍 Cocok", "👎 Nggak cocok"],
        is_anonymous=True
    )

    stats = load_stats()
    stats['total_images'] += 1
    stats['users'][user_id] = stats['users'].get(user_id, 0) + 1
    stats['animal_count'][animal_name] = stats['animal_count'].get(animal_name, 0) + 1
    save_stats(stats)

    update_local_gallery()

@bot.message_handler(commands=['statistik'])
def show_stats(message):
    stats = load_stats()
    total = stats['total_images']
    users = len(stats['users'])
    
    if stats['animal_count']:
        most_common = max(stats['animal_count'].items(), key=lambda x: x[1])
        rarest = min(stats['animal_count'].items(), key=lambda x: x[1])
        common_text = f"{most_common[0].split('.')[0]} ({most_common[1]}x)"
        rare_text = f"{rarest[0].split('.')[0]} ({rarest[1]}x)"
    else:
        common_text = rare_text = "Belum ada"

    msg = (
        f"📊 Statistik Penggunaan:\n\n"
        f"🖼️ Total gambar dibuat: {total}\n"
        f"👥 Jumlah pengguna unik: {users}\n"
        f"🔥 Hewan paling sering muncul: {common_text}\n"
        f"🧄 Hewan paling langka: {rare_text}"
    )
    bot.send_message(message.chat.id, msg)

def update_local_gallery():
    images = sorted(os.listdir(MERGED_DIR), reverse=True)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Galeri Gabungan Foto</title>
    <meta charset=\"UTF-8\">
    <link href=\"https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/css/lightbox.min.css\" rel=\"stylesheet\">
    <style>
        body { font-family: sans-serif; text-align: center; background: #f8f9fa; padding: 20px; }
        .gallery-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }
        .gallery-item img { width: 300px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
<h1>Galeri Foto Gabungan</h1>
<div class=\"gallery-container\">
""")
        for img in images:
            f.write(f'''
    <div class="gallery-item">
        <a href="merged_photos/{img}" data-lightbox="gallery">
            <img src="merged_photos/{img}" alt="{img}">
        </a>
    </div>
''')
        f.write("""</div>
<script src=\"https://cdnjs.cloudflare.com/ajax/libs/lightbox2/2.11.4/js/lightbox.min.js\"></script>
</body>
</html>""")

if __name__ == "__main__":
    print("🤖 Bot Telegram aktif...")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"🔥 Error saat menjalankan bot: {e}")
