# Tahap 8 — Kontrak Integrasi Backend Go dan AI PETENG

## Batas layanan

Dokumen ini mendefinisikan komunikasi internal:

```text
Backend Go → AI PETENG
```

Frontend dan Web Admin tidak memanggil endpoint AI secara langsung pada alur final.

## Request

```http
POST /api/v1/ai/validate
Content-Type: multipart/form-data
Authorization: Bearer <service-token>
X-Request-ID: <request-id>
```

Field wajib:

```text
image: binary image file
```

Format yang didukung:

- JPEG
- PNG
- WebP

Ukuran maksimum awal: 10 MB.

## Response berhasil

```json
{
  "success": true,
  "ai_status": "selesai",
  "photo_status": "layak_dinilai",
  "lighting_class": "redup",
  "confidence": 0.82,
  "model_version": "resnet18-peteng-v1",
  "message": "Foto berhasil dianalisis."
}
```

## Response perlu review

```json
{
  "success": true,
  "ai_status": "perlu_tinjauan_manual",
  "photo_status": "perlu_tinjauan",
  "lighting_class": null,
  "confidence": 0.62,
  "model_version": "resnet18-peteng-v1",
  "message": "Confidence model belum cukup untuk memberikan hasil otomatis."
}
```

## Response foto tidak layak

```json
{
  "success": true,
  "ai_status": "selesai",
  "photo_status": "tidak_layak",
  "lighting_class": null,
  "confidence": 0.91,
  "model_version": "resnet18-peteng-v1",
  "message": "Foto tidak menunjukkan jalan yang relevan untuk dianalisis."
}
```

## Error

| HTTP | Error code | Arti |
|---:|---|---|
| 400 | `UNSUPPORTED_MEDIA_TYPE` | Format file tidak didukung |
| 400 | `EMPTY_FILE` | File kosong |
| 400 | `INVALID_IMAGE` | Isi file bukan gambar valid |
| 400 | `IMAGE_TOO_SMALL` | Resolusi terlalu kecil |
| 413 | `FILE_TOO_LARGE` | File melebihi 10 MB |
| 500 | `INFERENCE_FAILED` | Inferensi gagal |
| 503 | `MODEL_UNAVAILABLE` | Model atau service belum siap |

## Timeout dan retry

Backend Go sebaiknya memiliki:

- Connect timeout.
- Request timeout.
- Jumlah retry terbatas.
- Exponential backoff.
- Idempotency atau request ID.
- Status laporan yang tetap tersimpan ketika retry gagal.

Jangan mengubah kegagalan teknis menjadi `photo_status: tidak_layak`.

## Penyimpanan hasil di Backend

Backend sebaiknya menyimpan:

```text
report_id
request_id
ai_status
photo_status
lighting_class
confidence
model_version
processed_at
error_code
```

Backend juga perlu menyimpan hash foto bila ingin memastikan hasil AI terkait dengan foto yang benar.

## API untuk Frontend dan Web Admin

Endpoint untuk Frontend dan Web Admin tetap berada di Backend Go, misalnya:

```http
GET /api/reports/{report_id}
GET /api/admin/reports/{report_id}
```

Endpoint tersebut mengembalikan status bisnis laporan dan hasil AI yang sudah disimpan Backend.

## Acceptance criteria

- [ ] Backend dapat mengirim multipart field bernama `image`.
- [ ] Backend dapat membaca response sukses.
- [ ] Backend membedakan `perlu_tinjauan_manual` dari `gagal`.
- [ ] Backend menangani HTTP 503.
- [ ] Backend tidak menerima hasil prediksi mentah dari Frontend sebagai sumber kebenaran.
- [ ] Frontend membaca hasil dari Backend.
- [ ] Web Admin membaca hasil dari Backend.
- [ ] Request ID dapat ditelusuri dalam log Backend dan AI.
