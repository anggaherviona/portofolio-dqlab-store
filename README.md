# Belanja Akhir Tahun: Ke Mana Larinya Uang Pelanggan DQLab Store?

Portofolio data storytelling oleh **Angga Herviona Ikhwanudin**.
Analisis 5.000 transaksi DQLab Store (Juli–Desember 2019) dengan Python, pandas, Altair, dan Streamlit.

## Isi folder

```
app.py                       # aplikasi Streamlit (artikel + 8 grafik interaktif)
requirements.txt             # library yang dibutuhkan
data/retail_raw_reduced.csv  # dataset pelatihan DQLab
```

## Menjalankan di komputer sendiri

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser akan terbuka di http://localhost:8501.

## Publikasi gratis di Streamlit Community Cloud

1. Buat akun di https://github.com, lalu buat repository baru (misalnya `portofolio-dqlab-store`), visibility **Public**.
2. Unggah ketiga isi folder ini ke repository (tombol **Add file → Upload files**). Pastikan folder `data` ikut terunggah.
3. Buka https://share.streamlit.io, masuk dengan akun GitHub.
4. Klik **Create app → Deploy a public app from GitHub**, pilih repository tadi, branch `main`, main file `app.py`.
5. Klik **Deploy**. Dalam beberapa menit aplikasi online dengan alamat `https://<nama-app>.streamlit.app`.

Setiap kali file di GitHub diubah, aplikasi otomatis ikut diperbarui.

## Yang bisa disesuaikan

- **Profil penulis**: ubah teks di blok `st.success(...)` pada sidebar.
- **Foto penulis**: simpan foto sebagai `foto.jpg` di folder yang sama, lalu tambahkan `st.image("foto.jpg")` di atas blok profil.
- **Narasi**: semua paragraf ada di `st.write(...)`; angka di dalamnya dihitung otomatis dari data.

## Kaitan dengan skema Data Analyst

| Unit | Bukti di aplikasi |
| --- | --- |
| Mengumpulkan & memvalidasi data | Pemuatan CSV, penghapusan 7 duplikat (catatan metodologi) |
| Menelaah data | Gambar 1–7 beserta narasi temuan |
| Menentukan objek data | Filter bulan, provinsi, dan brand |
| Business Intelligence | Dashboard interaktif yang dipublikasikan |
| Menyusun laporan | Artikel lengkap dengan kesimpulan dan rekomendasi |
