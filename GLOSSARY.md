# Glossary AI PETENG

## Frontend

Aplikasi yang digunakan warga untuk mengirim laporan dan melihat status laporan. Frontend tidak menjadi sumber kebenaran hasil AI.

## Backend PETENG

Layanan utama yang menerima laporan, menyimpan data, memanggil AI PETENG, menyimpan hasil analisis, dan menyediakan data untuk Frontend serta Web Admin.

## AI PETENG

Layanan internal berbasis FastAPI yang memvalidasi gambar dan menjalankan model CNN untuk memperkirakan tingkat pencahayaan visual pada foto.

## Web Admin

Aplikasi untuk petugas atau pengelola yang membaca laporan dari Backend dan melakukan pemeriksaan manual atau tindak lanjut.

## Laporan

Data bisnis yang dibuat oleh warga melalui Frontend. Laporan dapat memiliki foto, status bisnis, hasil AI, dan histori proses.

## Analisis AI

Proses validasi berkas dan inferensi CNN terhadap foto. Analisis AI bukan keputusan final atas kebenaran laporan.

## Status AI

Status teknis proses analisis, seperti `belum_diproses`, `diproses`, `selesai`, `perlu_tinjauan_manual`, dan `gagal`.

## Status foto

Penilaian kelayakan foto untuk klasifikasi, yaitu `layak_dinilai`, `tidak_layak`, atau `perlu_tinjauan`.

## Status bisnis laporan

Status yang dikelola Backend untuk menggambarkan progres laporan. Status ini berbeda dari status AI dan tidak ditentukan langsung oleh model.

## Confidence

Skor keyakinan keluaran model terhadap kelas yang diprediksi. Confidence rendah dapat menyebabkan foto diarahkan ke tinjauan manual.

## Model version

Identitas versi model CNN yang digunakan untuk menghasilkan analisis. Nilai ini disimpan agar hasil dapat ditelusuri.

## Request ID

Identitas teknis untuk menelusuri satu permintaan antara Frontend, Backend, dan AI PETENG.

## Sumber kebenaran

Komponen yang bertanggung jawab menyimpan dan menentukan keadaan resmi suatu data. Untuk laporan dan hasil AI yang sudah dicatat, sumber kebenarannya adalah Backend PETENG.

## Tinjauan manual

Pemeriksaan manusia terhadap foto atau hasil AI ketika foto tidak relevan, confidence rendah, atau proses membutuhkan keputusan petugas.
