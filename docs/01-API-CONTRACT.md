# Tahap 1 — Kontrak API dan Validasi Berkas

## Tujuan

Menyediakan kontrak API yang stabil sebelum model CNN dihubungkan ke endpoint.

## Endpoint

### Health check

```http
GET /health
```

Endpoint ini hanya menunjukkan bahwa service dapat diakses. Kesiapan model sebaiknya dibedakan melalui endpoint readiness pada tahap integrasi.

### Analisis foto

```http
POST /api/v1/ai/validate
Content-Type: multipart/form-data
```

Field upload yang digunakan: `image`.

Format yang diterima: JPEG, PNG, dan WebP. Batas awal: 10 MB.

## Response sukses setelah model tersedia

```json
{
  "success": true,
  "ai_status": "selesai",
  "photo_status": "layak_dinilai",
  "lighting_class": "redup",
  "confidence": 0.87,
  "model_version": "resnet18-peteng-v1",
  "message": "Foto berhasil dianalisis."
}
```

## Nilai status

`ai_status`:

- `belum_diproses`
- `diproses`
- `selesai`
- `perlu_tinjauan_manual`
- `gagal`

`photo_status`:

- `layak_dinilai`
- `tidak_layak`
- `perlu_tinjauan`

`lighting_class`:

- `terang`
- `redup`
- `gelap`
- `null`

Jika prediksi CNN adalah `bukan_jalan`, response harus memakai `photo_status: tidak_layak` dan `lighting_class: null`.

## Response error

```json
{
  "success": false,
  "ai_status": "gagal",
  "error_code": "INVALID_IMAGE",
  "message": "Isi file bukan gambar yang valid."
}
```

Kode awal yang perlu didukung:

- `UNSUPPORTED_MEDIA_TYPE`
- `EMPTY_FILE`
- `FILE_TOO_LARGE`
- `INVALID_IMAGE`
- `IMAGE_TOO_SMALL`
- `MODEL_UNAVAILABLE`
- `INFERENCE_FAILED`

## Aturan penting

- `success: true` berarti request berhasil diproses oleh service, bukan berarti laporan warga benar.
- Kegagalan teknis tidak boleh dikembalikan sebagai `photo_status: tidak_layak`.
- Foto yang tidak relevan tidak boleh dipaksa menjadi `gelap`.
- Nama file pengguna tidak boleh dijadikan path penyimpanan tepercaya.
- Validasi MIME type harus dilengkapi pemeriksaan format aktual dengan Pillow.

## Checklist tahap

- [ ] Field upload `image` disepakati dengan backend Go.
- [ ] Schema Pydantic dibuat.
- [ ] Konfigurasi ukuran file dan model dipusatkan.
- [ ] Validasi isi gambar ditambahkan.
- [ ] Error response konsisten.
- [ ] OpenAPI dan contoh request diperbarui.
- [ ] Test endpoint dasar tersedia.
