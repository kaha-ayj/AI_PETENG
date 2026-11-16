# Tahap 5 — Integrasi CNN ke FastAPI

## Tujuan

Menghubungkan checkpoint CNN yang telah dievaluasi ke endpoint FastAPI tanpa mencampur routing, validasi gambar, dan logika model.

## Struktur komponen

```text
app/
  api/routes.py
  core/config.py
  models/cnn_classifier.py
  schemas/prediction.py
  services/image_validation.py
  services/prediction_service.py
```

## Alur request

```text
Upload image
  ↓
Validasi ukuran dan isi file
  ↓
Decode dan preprocess gambar
  ↓
Model loader mengambil checkpoint
  ↓
CNN menghasilkan logits
  ↓
Softmax menghasilkan confidence
  ↓
Mapping kelas dan aturan threshold
  ↓
Response API
```

## Aturan hasil

### Prediksi kelas pencahayaan

Jika hasil adalah `terang`, `redup`, atau `gelap` dan confidence mencukupi:

```text
ai_status = selesai
photo_status = layak_dinilai
lighting_class = hasil model
```

### Foto bukan jalan

```text
ai_status = selesai
photo_status = tidak_layak
lighting_class = null
```

### Confidence tidak mencukupi

Confidence di bawah threshold adalah kegagalan inferensi, bukan keputusan tentang kelayakan foto. Service mengembalikan HTTP 500 dengan `error_code = INFERENCE_FAILED`; Backend tidak boleh menyimpannya sebagai `tidak_valid`.

### Model tidak tersedia

```text
HTTP 503
error_code = MODEL_UNAVAILABLE
```

Kegagalan model tidak boleh dianggap sebagai foto tidak layak.

## Model loading

Model sebaiknya dimuat saat startup atau melalui dependency yang terkontrol, bukan dimuat ulang pada setiap request. Startup harus gagal secara jelas atau readiness endpoint harus melaporkan model belum siap.

Simpan informasi berikut bersama checkpoint:

- `model_version`.
- Class mapping.
- Input size.
- Normalization.
- Path checkpoint.

## Readiness

Selain `/health`, pertimbangkan:

```http
GET /ready
```

Contoh response:

```json
{
  "status": "ready",
  "model_loaded": true,
  "model_version": "resnet18-peteng-v1"
}
```

## Checklist tahap

- [ ] Checkpoint dapat dimuat.
- [ ] Preprocessing inference sama dengan preprocessing validation.
- [ ] Model tidak dimuat ulang setiap request.
- [ ] `bukan_jalan` dipetakan dengan benar.
- [ ] Confidence threshold diterapkan.
- [ ] Model version dikembalikan.
- [ ] Model unavailable menghasilkan error yang jelas.
- [ ] Endpoint diuji dengan gambar baru.
