import pickle
import os
import random
import requests
from playwright.sync_api import sync_playwright
import time

# Menentukan path folder tempat script berada (ImageDownloader)
script_folder_path = os.path.dirname(os.path.realpath(__file__))

# Menentukan path ke file cookie yang berada dalam folder yang sama dengan skrip utama
cookies_folder_path = script_folder_path  # Cookie berada di folder yang sama dengan script utama

# Menyusun path ke file lainnya
gambar_folder_path = os.path.join(script_folder_path, 'Gambar')

# Memastikan folder Gambar ada, jika tidak, buat folder tersebut
if not os.path.exists(gambar_folder_path):
    os.makedirs(gambar_folder_path)

# File Gambar.txt untuk menyimpan path gambar yang diunduh
gambar_txt_path = os.path.join(script_folder_path, "Gambar.txt")

# Memastikan file Gambar.txt ada
if not os.path.exists(gambar_txt_path):
    with open(gambar_txt_path, "w") as f:
        f.write("Daftar Path Gambar:\n")  # Header

def download_images():
    # Memulai Playwright dan membuka browser
    with sync_playwright() as p:
        print("Bismillahirrahmanirrahim")
        browser = p.chromium.launch(headless=True)  # Atur headless=True jika tidak ingin menampilkan browser
        page = browser.new_page()

        # Pilih file .pkl secara acak dari folder cookies (folder yang sama dengan skrip)
        cookies_files = [f for f in os.listdir(cookies_folder_path) if f.endswith(".pkl")]
        if cookies_files:
            random_cookie_file = random.choice(cookies_files)
            cookies_file_path = os.path.join(cookies_folder_path, random_cookie_file)            
            print(f"Menggunakan cookie file: {random_cookie_file}")
            # Memuat cookie dari file .pkl
            with open(cookies_file_path, "rb") as cookies_file:
                cookies = pickle.load(cookies_file)
                for cookie in cookies:
                    # Periksa domain cookie dan pastikan sesuai dengan URL yang sedang dibuka
                    if 'domain' in cookie and cookie['domain'] != '.pinterest.com':
                        cookie['domain'] = '.pinterest.com'  # Perbaiki domain cookie jika perlu
                    page.context.add_cookies([cookie])

            # Refresh halaman untuk menerapkan cookie
            page.reload()
            time.sleep(3)  # Tunggu beberapa detik agar halaman memuat dengan cookies

        # Meminta input keyword dari pengguna
        keyword = input("Mau cari gambar apa tuan?: ").strip()

        # Encode keyword untuk URL (ganti spasi dengan %20)
        encoded_keyword = keyword.replace(" ", "%20")

        # Membuka URL Pinterest dengan keyword yang dimasukkan
        search_url = f"https://pinterest.com/search/pins/?q={encoded_keyword}&rs=typed"
        page.goto(search_url)
        time.sleep(3)  # Tunggu sebentar untuk memastikan halaman terbuka

        # Input jumlah gambar yang ingin diunduh
        jumlah_gambar = int(input("Mau download berapa gambar tuan?: ").strip())
        gambar_terunduh = 0  # Variabel untuk menghitung gambar yang sudah diunduh

        # Mengatur scroll dan download gambar
        previous_height = page.evaluate("document.body.scrollHeight")
        while gambar_terunduh < jumlah_gambar:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Tunggu beberapa detik untuk memuat gambar
            current_height = page.evaluate("document.body.scrollHeight")
            
            # Jika sudah tidak ada perubahan pada tinggi halaman, scroll lebih lanjut
            if current_height == previous_height and gambar_terunduh < jumlah_gambar:
                break
            
            previous_height = current_height

            # Setelah scroll, download gambar yang sudah muncul
            img_elements = page.query_selector_all("div[role='listitem']")

            for item in img_elements:
                if gambar_terunduh >= jumlah_gambar:
                    break  # Stop jika jumlah gambar yang diunduh sudah mencapai target

                # Cek jika elemen memiliki dua gambar (src)
                img_tags = item.query_selector_all("img")
                
                if img_tags:
                    img_url = img_tags[0].get_attribute("src")  # Ambil src dari gambar pertama
                    if img_url:
                        try:
                            # Ambil ekstensi file gambar (misalnya .jpg)
                            img_extension = img_url.split('.')[-1]
                            img_name = f"image_{gambar_terunduh + 1}_{random.randint(1, 1000)}.{img_extension}"
                            img_path = os.path.join(gambar_folder_path, img_name)

                            # Download gambar dan simpan ke folder
                            response = requests.get(img_url)
                            with open(img_path, "wb") as f:
                                f.write(response.content)
                            print(f"Gambar {img_name} berhasil diunduh.")

                            # Menyimpan path gambar ke dalam Gambar.txt
                            with open(gambar_txt_path, "a") as f:
                                f.write(f"{img_path}\n")

                            gambar_terunduh += 1  # Menambah jumlah gambar yang sudah diunduh

                        except Exception as e:
                            print(f"Terjadi kesalahan saat mendownload gambar: {e}")

        # Menampilkan jumlah gambar yang sudah diunduh
        print(f"\nJumlah gambar yang berhasil diunduh: {gambar_terunduh}")    
        
        # Menutup browser
        browser.close()

def main():
    while True:
        # Memulai proses download gambar
        download_images()

        # Memberikan opsi untuk mengulangi atau keluar
        pilihan = input("\nApakah Anda ingin mengulang proses? (y/n): ").strip().lower()
        if pilihan != 'y':
            print("Terima kasih telah menggunakan script ini.")
            break

# Menjalankan program utama
if __name__ == "__main__":
    main()
