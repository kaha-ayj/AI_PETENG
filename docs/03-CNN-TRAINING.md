# Tahap 3 — Pelatihan CNN Baseline

## Tujuan

Melatih model klasifikasi gambar menggunakan CNN transfer learning untuk memprediksi empat kelas baseline:

```text
bukan_jalan
gelap
redup
terang
```

YOLO tidak digunakan pada tahap ini karena kebutuhan utama adalah klasifikasi keseluruhan gambar, bukan deteksi lokasi objek.

## Strategi model

Jangan melatih CNN dari nol dengan 44 gambar. Mulai dengan transfer learning menggunakan salah satu model ringan:

- ResNet18.
- MobileNetV3 Small.
- EfficientNet-B0.

Model awal yang disarankan: ResNet18 atau MobileNetV3 Small dengan pretrained weights, lalu mengganti classifier menjadi empat output.

## Pipeline training

1. Baca manifest train dan validation.
2. Terapkan preprocessing yang sama dengan model pretrained.
3. Terapkan augmentasi hanya pada train.
4. Buat DataLoader.
5. Ganti layer classifier.
6. Latih classifier head terlebih dahulu bila diperlukan.
7. Lakukan fine-tuning bertahap.
8. Simpan checkpoint terbaik berdasarkan validation macro F1 atau balanced accuracy.
9. Simpan label mapping dan konfigurasi eksperimen.

## Artefak yang harus disimpan

```text
model_weights/
  resnet18-peteng-v1.pt
  resnet18-peteng-v1.json

artifacts/
  training_history.json
  class_distribution.json
  config.json
```

Metadata model minimal:

- Nama arsitektur.
- Versi model.
- Daftar kelas dan urutannya.
- Ukuran input.
- Normalisasi.
- Epoch.
- Learning rate.
- Seed.
- Dataset manifest/hash.
- Waktu training.
- Device CPU/CUDA.

## Keterbatasan dataset kecil

Dengan 44 gambar, model sangat mudah overfitting. Akurasi training yang tinggi tidak cukup untuk menyatakan model baik. Baseline ini hanya digunakan untuk memverifikasi pipeline dan menemukan kesalahan kelas.

Jika validation terlalu kecil, gunakan stratified k-fold untuk estimasi yang lebih stabil. Jangan menganggap hasil tersebut sebagai jaminan performa produksi.

## Reproducibility

Training harus mencatat random seed, versi dependency, konfigurasi transform, split manifest, dan checkpoint. Dataset test tidak boleh digunakan selama eksperimen pemilihan model.

## Checklist tahap

- [ ] Dataset split tersedia.
- [ ] Model pretrained dipilih.
- [ ] Training script menerima path dan konfigurasi.
- [ ] Class mapping disimpan.
- [ ] Checkpoint terbaik disimpan.
- [ ] History training disimpan.
- [ ] Training dan validation loss dicatat.
- [ ] Metrik per epoch dicatat.
- [ ] Eksperimen dapat diulang.
