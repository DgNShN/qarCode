import os
import qrcode
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import http.server
import socketserver
import threading
import socket
import urllib.parse
import time
import sys


def generate_qr_code(data, save_path):
    """QR kodunu oluşturur ve dosyaya kaydeder."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save(save_path)
    messagebox.showinfo("QR Kod", f"QR kodu '{save_path}' olarak kaydedildi.")


def show_qr_code_image(qr_code_path):
    """QR kodunu ekranda gösterir."""
    qr_window = tk.Toplevel()
    qr_window.title("QR Kodunu Görüntüle")

    img = Image.open(qr_code_path)
    tk_img = ImageTk.PhotoImage(img)

    img_label = tk.Label(qr_window, image=tk_img)
    img_label.image = tk_img  # Referansı tut
    img_label.pack()

    qr_window.mainloop()


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Dosyaların indirilmesi için HTTP yanıtlarını özelleştirir."""

    def end_headers(self):
        if self.path != '/':
            self.send_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(self.path))
        super().end_headers()


def start_http_server(directory, port=8000):
    """Belirtilen dizinde bir HTTP sunucusu başlatır."""
    os.chdir(directory)
    handler = CustomHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Port {port}'ta dosya paylaşımı başlatıldı.")
        httpd.serve_forever()


def select_file():
    """Kullanıcının dosya seçmesini sağlar ve QR kodu oluşturur."""
    file_path = filedialog.askopenfilename()
    if file_path:
        directory = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # HTTP sunucusunu başlatma
        server_thread = threading.Thread(target=start_http_server, args=(directory,))
        server_thread.daemon = True
        server_thread.start()

        # HTTPS URL (Yerli geliştirmede HTTPS kullanmak için SSL sertifikası gereklidir. Bu örnekte HTTP kullanıyoruz.)
        local_ip = socket.gethostbyname(socket.gethostname())
        encoded_file_name = urllib.parse.quote(file_name)
        file_url = f"http://{local_ip}:8000/{encoded_file_name}"  # HTTPS URL yerine HTTP kullanılıyor
        qr_code_path = f"{file_name}_qr.png"
        print(f"Dosya URL'si: {file_url}")  # URL'yi konsola yazdırır
        generate_qr_code(file_url, qr_code_path)

        # QR kodunu ekranda gösterme
        show_qr_code_image(qr_code_path)

        # Uygulamanın belirli bir süre sonra kapanmasını sağlar
        time.sleep(30)  # QR kodunun taranması için 30 saniye bekler
        sys.exit("QR kodu tarandı, uygulama kapatılıyor.")


def main():
    """Ana Tkinter penceresini başlatır."""
    root = tk.Tk()
    root.title("Dosya Aktarım Programı")
    root.geometry("300x150")

    label = tk.Label(root, text="Lütfen bir dosya seçin:")
    label.pack(pady=10)

    select_button = tk.Button(root, text="Dosya Seç", command=select_file)
    select_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
