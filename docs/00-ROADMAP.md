# AI PETENG — Roadmap Pengembangan

## Tujuan

Dokumen ini menjadi peta jalan pengerjaan AI PETENG dari kondisi prototype sampai layanan CNN yang dapat diintegrasikan dengan backend Go.

## Keputusan dasar

- Model utama menggunakan CNN/transfer learning, bukan YOLO.
- Dataset yang telah divalidasi tim dapat digunakan sebagai dataset awal untuk eksperimen.
- Dataset awal berisi empat kelas: `bukan_jalan`, `terang`, `redup`, dan `gelap`.
- `bukan_jalan` diperlakukan sebagai kelas relevansi pada baseline, bukan sebagai tingkat pencahayaan.
- Hasil AI tidak menentukan kebenaran laporan atau kerusakan PJU.

## Tahapan

| Tahap | Dokumen | Hasil utama | Status |
|---|---|---|---|
| 1 | `01-API-CONTRACT.md` | Kontrak request, response, dan error | Direncanakan |
| 2 | `02-DATASET-CURATION.md` | Dataset terkurasi, metadata, dan split | Dataset awal tersedia; split belum dibuat |
| 3 | `03-CNN-TRAINING.md` | Baseline CNN terlatih dan checkpoint | Belum dimulai |
| 4 | `04-MODEL-EVALUATION.md` | Metrik, confusion matrix, dan analisis kesalahan | Belum dimulai |
| 5 | `05-INFERENCE-INTEGRATION.md` | Model terhubung ke FastAPI | Belum dimulai |
| 6 | `06-TESTING-RELEASE.md` | Pengujian kontrak dan kesiapan integrasi | Belum dimulai |

## Urutan kerja

1. Finalisasi kontrak API sebelum perilaku endpoint berubah.
2. Catat dan susun dataset yang sudah divalidasi ke format yang dapat direproduksi.
3. Buat split data tanpa leakage.
4. Latih baseline transfer learning menggunakan data awal.
5. Evaluasi dengan metrik per kelas, bukan accuracy saja.
6. Hubungkan model terbaik ke service inferensi.
7. Uji endpoint dan integrasi backend Go.
8. Tambahkan data berdasarkan kesalahan model.

## Kriteria selesai keseluruhan

- API memiliki response schema yang konsisten.
- File valid, file rusak, dan error teknis dibedakan.
- Model memiliki label mapping dan versi yang jelas.
- Evaluasi memakai data yang tidak digunakan saat training.
- Foto `bukan_jalan` tidak menghasilkan kelas pencahayaan.
- Confidence rendah dapat diarahkan ke tinjauan manual.
- Backend Go dapat mengonsumsi kontrak tanpa bergantung pada detail internal Python.
