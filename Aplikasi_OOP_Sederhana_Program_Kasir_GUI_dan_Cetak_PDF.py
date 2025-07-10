import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
from fpdf import FPDF
import platform
import subprocess

class Produk:
    def __init__(self, nama, harga):
        self.nama = nama
        self.harga = harga

class Keranjang:
    def __init__(self):
        self.items = []

    def tambah_produk(self, produk, jumlah):
        self.items.append((produk, jumlah))

    def hitung_total(self):
        return sum(p.harga * j for p, j in self.items)

    def kosongkan(self):
        self.items = []

    def get_item_list(self):
        return self.items

class KasirApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Kasir Presisi")
        self.root.geometry("600x500")

        self.keranjang = Keranjang()
        self.daftar_produk = [
            Produk("Kopi", 5000),
            Produk("Teh", 3000),
            Produk("Air Mineral", 2000),
            Produk("Roti", 7000)
        ]

        main_frame = tk.Frame(root, width=500)
        main_frame.pack(padx=20, pady=10, fill='x')

        # Input Nama Customer
        tk.Label(main_frame, text="Nama Customer").pack(anchor='w')
        self.entry_customer = tk.Entry(main_frame)
        self.entry_customer.pack(fill='x', pady=(0, 10))

        # Pilih Produk
        tk.Label(main_frame, text="Pilih Produk").pack(anchor='w')
        self.var_produk = tk.StringVar()
        self.combo_produk = ttk.Combobox(main_frame, textvariable=self.var_produk, width=50)
        self.combo_produk['values'] = [p.nama for p in self.daftar_produk]
        self.combo_produk.current(0)
        self.combo_produk.pack(fill='x')

        # Jumlah & Tambah ke Keranjang
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill='x', pady=8)
        tk.Label(input_frame, text="Jumlah").pack(side=tk.LEFT)
        self.entry_jumlah = tk.Entry(input_frame, width=10)
        self.entry_jumlah.pack(side=tk.LEFT, padx=(10, 20))
        self.btn_tambah = tk.Button(input_frame, text="Tambah ke Keranjang", width=20, command=self.tambah_keranjang)
        self.btn_tambah.pack(side=tk.RIGHT)

        # Keranjang
        tk.Label(main_frame, text="Keranjang Belanja:").pack(anchor='w', pady=(10, 0))
        self.listbox = tk.Listbox(main_frame, width=70, height=10)
        self.listbox.pack(fill='x', pady=5)

        # Uang Dibayar & Tombol Bayar
        uang_frame = tk.Frame(main_frame)
        uang_frame.pack(fill='x', pady=10)
        tk.Label(uang_frame, text="Uang Dibayar (Rp):").pack(side=tk.LEFT)
        self.entry_uang = tk.Entry(uang_frame, width=20)
        self.entry_uang.pack(side=tk.LEFT, padx=(10, 20))
        self.btn_bayar = tk.Button(uang_frame, text="Bayar", width=20, command=self.hitung_kembalian)
        self.btn_bayar.pack(side=tk.RIGHT)

        # Total, Kembalian & Cetak PDF
        hasil_frame = tk.Frame(main_frame)
        hasil_frame.pack(fill='x', pady=5)
        self.label_total = tk.Label(hasil_frame, text="Total: Rp0")
        self.label_total.pack(side=tk.LEFT, padx=(0, 40))
        self.label_kembalian = tk.Label(hasil_frame, text="Kembalian: Rp0")
        self.label_kembalian.pack(side=tk.LEFT, padx=(0, 20))
        self.btn_cetak = tk.Button(hasil_frame, text="Cetak Struk PDF", width=20, command=self.cetak_pdf)
        self.btn_cetak.pack(side=tk.RIGHT)

    def tambah_keranjang(self):
        try:
            nama_produk = self.var_produk.get()
            jumlah = int(self.entry_jumlah.get())
            produk = next(p for p in self.daftar_produk if p.nama == nama_produk)
            self.keranjang.tambah_produk(produk, jumlah)
            self.listbox.insert(tk.END, f"{produk.nama} x {jumlah} = Rp{produk.harga * jumlah}")
            self.update_total()
            self.entry_jumlah.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan jumlah yang valid!")

    def update_total(self):
        total = self.keranjang.hitung_total()
        self.label_total.config(text=f"Total: Rp{total}")

    def hitung_kembalian(self):
        try:
            total = self.keranjang.hitung_total()
            uang_dibayar = int(self.entry_uang.get())
            if uang_dibayar < total:
                messagebox.showwarning("Uang Kurang", "Uang yang dibayar kurang dari total.")
                return
            kembalian = uang_dibayar - total
            self.label_kembalian.config(text=f"Kembalian: Rp{kembalian}")
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan nominal uang dibayar dengan benar!")

    def cetak_pdf(self):
        try:
            customer_name = self.entry_customer.get().strip()
            if customer_name == "":
                messagebox.showwarning("Customer Kosong", "Masukkan nama customer terlebih dahulu.")
                return

            total = self.keranjang.hitung_total()
            uang_dibayar = int(self.entry_uang.get())
            kembalian = uang_dibayar - total
            now = datetime.datetime.now()
            waktu_str = now.strftime("%Y-%m-%d %H:%M:%S")

            folder_path = r"D:\StrukKasir"
            os.makedirs(folder_path, exist_ok=True)
            filename = f"struk_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(folder_path, filename)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Struk Pembayaran", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Tanggal & Waktu: {waktu_str}", ln=True)
            pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=True)
            pdf.cell(200, 10, txt="-----------------------------", ln=True)
            for produk, jumlah in self.keranjang.get_item_list():
                pdf.cell(200, 10, txt=f"{produk.nama} x {jumlah} = Rp{produk.harga * jumlah}", ln=True)
            pdf.cell(200, 10, txt="-----------------------------", ln=True)
            pdf.cell(200, 10, txt=f"Total     : Rp{total}", ln=True)
            pdf.cell(200, 10, txt=f"Dibayar   : Rp{uang_dibayar}", ln=True)
            pdf.cell(200, 10, txt=f"Kembalian : Rp{kembalian}", ln=True)
            pdf.cell(200, 10, txt="-----------------------------", ln=True)
            pdf.cell(200, 10, txt="Terima kasih telah berbelanja!", ln=True)

            pdf.output(filepath)

            self.print_file(filepath)
            messagebox.showinfo("Sukses", f"Struk berhasil dicetak dan disimpan:\n{filepath}")
        except ValueError:
            messagebox.showerror("Input Error", "Masukkan nilai uang dibayar dengan valid!")

    def print_file(self, filepath):
        try:
            acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
            if not os.path.exists(acrobat_path):
                messagebox.showwarning("Print Manual", f"Struk disimpan di:\n{filepath}\n\nBuka dan cetak secara manual.")
                return
            subprocess.Popen([acrobat_path, '/N', '/T', filepath], shell=False)
        except Exception as e:
            messagebox.showerror("Cetak Gagal", f"Gagal mencetak file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KasirApp(root)
    root.mainloop()
