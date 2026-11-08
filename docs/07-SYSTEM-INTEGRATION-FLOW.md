# Tahap 7 — Alur Integrasi Sistem PETENG

## Keputusan arsitektur

Alur utama yang digunakan:

```text
Frontend → Backend Go → AI PETENG → Backend Go → Frontend/Web Admin
```

Frontend tidak menjadi sumber kebenaran hasil AI. Backend Go menjadi sumber kebenaran untuk laporan, status, foto, dan hasil analisis yang sudah dicatat.

## Tanggung jawab komponen

### Frontend

- Mengambil dan mengirim foto ke Backend Go.
- Menampilkan status laporan.
- Menampilkan hasil analisis yang diterima dari Backend Go.
- Menampilkan progres pemeriksaan.
- Tidak memanggil AI PETENG secara langsung pada alur final.

### Backend Go

- Menerima laporan dari Frontend.
- Menyimpan laporan dan foto.
- Memanggil AI PETENG melalui HTTP internal yang terautentikasi.
- Menyimpan hasil AI dan histori proses.
- Menentukan status bisnis laporan.
- Menangani timeout, retry, dan AI yang tidak tersedia.
- Menyediakan data kepada Frontend dan Web Admin.

### AI PETENG

- Memvalidasi file gambar.
- Menjalankan CNN.
- Menghasilkan kelas pencahayaan dan confidence.
- Menandai foto tidak relevan atau perlu review manual.
- Mengembalikan model version dan status analisis.
- Tidak mengelola akun, laporan, database aplikasi, atau keputusan bisnis.

### Web Admin

- Membaca laporan dan hasil AI melalui Backend Go.
- Meninjau foto yang diarahkan ke pemeriksaan manual.
- Memberikan keputusan atau koreksi melalui Backend Go.
- Tidak memanggil AI PETENG secara langsung.

## Alur final sinkron

1. Frontend mengirim laporan dan foto ke Backend Go.
2. Backend menyimpan laporan dengan status `diproses_ai`.
3. Backend mengirim foto ke `POST /api/v1/ai/validate`.
4. AI PETENG memvalidasi dan menganalisis foto.
5. AI mengembalikan hasil ke Backend.
6. Backend menyimpan hasil AI berdasarkan `report_id`.
7. Backend menentukan status bisnis laporan.
8. Frontend dan Web Admin membaca status dari Backend.

## Status yang harus dipisahkan

### Status AI

- `belum_diproses`
- `diproses`
- `selesai`
- `perlu_tinjauan_manual`
- `gagal`

### Status foto

- `layak_dinilai`
- `tidak_layak`
- `perlu_tinjauan`

### Status bisnis laporan

Status final ditentukan Backend Go. Contoh status awal:

- `diajukan`
- `diproses_ai`
- `menunggu_tinjauan_manual`
- `siap_ditinjau`
- `ditinjau`
- `selesai`

Nama final status bisnis perlu disepakati di kontrak Backend Go.

## Kontrak internal Backend → AI

Request:

```http
POST /api/v1/ai/validate
Content-Type: multipart/form-data
X-Request-ID: <request-id>
Authorization: Bearer <service-token>
```

Field:

```text
image: <foto laporan>
```

Backend sebaiknya menyertakan request ID untuk tracing. AI tidak perlu menerima identitas warga.

Response AI disimpan oleh Backend bersama:

- `report_id`
- `request_id`
- `ai_status`
- `photo_status`
- `lighting_class`
- `confidence`
- `model_version`
- `processed_at`

## Kegagalan proses

### AI timeout atau tidak tersedia

Backend mempertahankan laporan dan mengubah status menjadi status retry atau review teknis. Kegagalan AI tidak boleh dianggap sebagai foto tidak layak.

### AI mengembalikan confidence rendah

Backend menyimpan hasil dengan status `menunggu_tinjauan_manual`.

### AI mengembalikan `bukan_jalan`

AI mengembalikan `photo_status: tidak_layak` dan `lighting_class: null`. Backend menentukan tindakan bisnis berikutnya.

### Frontend terputus

Backend tetap menyimpan laporan dan dapat meneruskan proses AI. Frontend mengambil status terbaru menggunakan `report_id`.

## Evolusi ke proses asinkron

Jika inferensi atau volume request meningkat, Backend dapat mengganti pemanggilan sinkron dengan queue:

```text
Frontend → Backend → Queue → AI PETENG → Backend → Frontend/Admin
```

Kontrak status tetap dipertahankan agar perubahan ini tidak memaksa perubahan besar di Frontend.

## Prinsip keamanan

- Endpoint AI tidak dibuka sebagai endpoint publik untuk Flutter.
- Komunikasi Backend → AI menggunakan HTTPS atau jaringan internal terpercaya.
- Gunakan autentikasi service-to-service.
- Jangan mengirim token rahasia ke aplikasi Flutter.
- Backend memvalidasi hasil AI dan menyimpan histori.
- Log tidak menyimpan isi foto atau data pribadi secara sembarangan.
