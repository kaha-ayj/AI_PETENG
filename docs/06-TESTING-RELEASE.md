# Tahap 6 — Testing, Integrasi, dan Release

## Tujuan

Memastikan service AI dapat digunakan backend Go secara konsisten dan aman sebelum deployment.

## Test unit

Cakupan minimum:

- Validasi MIME type.
- Validasi format aktual gambar.
- File kosong.
- File lebih dari 10 MB.
- Gambar rusak.
- Resolusi terlalu kecil.
- Mapping kelas `bukan_jalan`.
- Confidence rendah.
- Checkpoint tidak tersedia.

## Test API

Endpoint yang diuji:

- `GET /health`.
- `GET /ready` jika sudah tersedia.
- `POST /api/v1/ai/validate`.

Skenario upload:

- JPEG valid.
- PNG valid.
- WebP valid.
- Format tidak didukung.
- File bukan gambar dengan MIME palsu.
- Foto yang menghasilkan masing-masing kelas.
- Foto `bukan_jalan`.
- Prediksi confidence rendah.
- Model tidak tersedia.

## Kontrak dengan backend Go

Backend harus mengetahui:

- URL dan method endpoint.
- Nama field multipart: `image`.
- Batas ukuran file.
- Bentuk response sukses.
- Arti `ai_status` dan `photo_status`.
- Kode error.
- Perilaku ketika service AI tidak tersedia.

Backend tidak boleh menganggap semua HTTP 200 sebagai laporan valid. Status AI dan status bisnis laporan harus diproses secara terpisah.

## Pengujian Postman

Simpan collection lokal yang berisi:

- Environment lokal.
- Request health.
- Request readiness.
- Request validasi JPEG/PNG/WebP.
- Request file invalid.
- Assertion status code.
- Assertion field response.
- Contoh response model unavailable.

Collection dapat dijalankan di CI setelah endpoint stabil.

## Observability minimum

Catat tanpa menyimpan data sensitif berlebihan:

- Request ID.
- Waktu proses total.
- Waktu inferensi.
- Model version.
- Status hasil.
- Error code.
- Ukuran gambar.

Hindari mencatat isi foto atau data pribadi ke log biasa.

## Release checklist

- [ ] Semua test lokal lulus.
- [ ] Contract response terdokumentasi.
- [ ] Checkpoint dan konfigurasi tersedia.
- [ ] Model version dapat dilacak.
- [ ] Test set tidak berubah tanpa pencatatan.
- [ ] Error teknis dapat dibedakan dari hasil analisis.
- [ ] Backend Go sudah menguji response aktual.
- [ ] Batas CPU/memory dan waktu inferensi dicatat.
- [ ] Kebijakan penyimpanan foto jelas.
- [ ] Deployment dan rollback terdokumentasi.

## Catatan release awal

Release pertama sebaiknya dianggap sebagai baseline eksperimen jika masih menggunakan 44 gambar. Jangan mempublikasikan angka performa sebagai jaminan produksi sebelum dataset dan evaluasi diperluas.
