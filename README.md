# PETENG — Dataset Starter (3 kelas pencahayaan)

Paket ini membantu mengumpulkan kandidat foto dari Wikimedia Commons dan mencatat sumber serta informasi lisensinya.

## Penting
- Paket ini **belum berisi foto yang sudah diverifikasi**. Lingkungan pembuatan file ini tidak dapat mengunduh file gambar eksternal secara langsung.
- Jalankan `download_wikimedia_candidates.py` di komputer Anda untuk mengambil kandidat gambar.
- Folder tujuan ditentukan dari kata pencarian, bukan label kebenaran. **Periksa setiap foto secara manual** sebelum menggunakannya sebagai data latih.
- Gunakan hanya gambar yang lisensinya mengizinkan penggunaan yang Anda perlukan. Simpan atribusi dan URL sumber.
- Jangan menyimpulkan bahwa jalan aman secara nyata hanya dari foto. Kelas di sini hanya menunjukkan tampilan tingkat penerangan pada foto.

## Cara menjalankan (Windows CMD)

1. Ekstrak ZIP ini, misalnya ke `D:\\peteng-project\\ai_peteng\\`.
2. Aktifkan virtual environment proyek Anda:
   `D:\\peteng-project\\ai_peteng\\.venv\\Scripts\\activate.bat`
3. Pasang dependensi:
   `python -m pip install requests pillow`
4. Jalankan:
   `python download_wikimedia_candidates.py --out "D:\\peteng-project\\ai_peteng\\dataset_raw\\public" --per-query 8`
5. Buka `dataset_raw\\public\\sumber_dataset.csv` dan tinjau setiap gambar. Pindahkan gambar ke kelas yang benar setelah diperiksa.

## Struktur output

dataset_raw/public/
  kandidat_terang/
  kandidat_redup/
  kandidat_gelap/
  sumber_dataset.csv

Nama folder `kandidat_*` sengaja digunakan agar kandidat tidak langsung dianggap sebagai label final.
