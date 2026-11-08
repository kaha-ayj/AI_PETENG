# Tahap 2 — Kurasi dan Persiapan Dataset

## Tujuan

Menjadikan foto yang telah divalidasi tim sebagai dataset yang dapat dilatih dan dievaluasi secara reproducible.

## Dataset awal

Audit terakhir menunjukkan 44 gambar yang dapat dibaca:

| Kelas | Jumlah |
|---|---:|
| `bukan_jalan` | 11 |
| `terang` | 11 |
| `redup` | 10 |
| `gelap` | 12 |

Dataset ini dapat digunakan untuk menguji pipeline dan membuat baseline awal. Dataset belum cukup untuk menyimpulkan kesiapan produksi.

## Definisi kelas baseline

- `terang`: jalan terlihat dengan pencahayaan yang memadai.
- `redup`: pencahayaan kurang atau tidak merata, tetapi konteks jalan masih terlihat.
- `gelap`: pencahayaan sangat minim dan sebagian permukaan jalan sulit terlihat.
- `bukan_jalan`: foto tidak menampilkan jalan yang relevan untuk analisis.

Validasi tim perlu dicatat sebagai metadata, termasuk kriteria dan reviewer. Jika semua foto telah disetujui, statusnya dapat dicatat sebagai `diterima`, tetapi provenance dan lisensi tetap perlu disimpan.

## Struktur yang disarankan

```text
dataset_raw/
  own/
  public/

dataset_curated/
  bukan_jalan/
  terang/
  redup/
  gelap/

dataset/
  train/
  val/
  test/
```

## Metadata minimum

Setiap gambar sebaiknya memiliki:

- `image_id`
- `path_relative`
- `source_type`
- `source_reference`
- `license`
- `confirmed_class`
- `review_status`
- `reviewer`
- `reviewed_at`
- `review_notes`
- `sha256`
- `group_id` untuk lokasi, sesi, atau seri foto

## Pembagian data

Untuk eksperimen awal gunakan pembagian stratified 70/15/15 bila jumlah per kelas memungkinkan. Dengan hanya 44 gambar, hasil validation/test akan tidak stabil. Alternatif yang lebih tepat untuk baseline kecil adalah stratified k-fold cross-validation, tetap dengan test set yang tidak disentuh selama pemilihan model.

Aturan anti-leakage:

- Split dilakukan sebelum augmentasi.
- Foto dari seri, lokasi, atau sesi yang sangat mirip sebaiknya berada pada split yang sama.
- Duplikat byte dan duplikat visual perlu diperiksa.
- Test set tidak digunakan untuk memilih hyperparameter atau threshold.

## Augmentasi

Augmentasi hanya diterapkan pada training set. Gunakan transformasi realistis seperti resize, crop ringan, rotasi kecil, dan perubahan brightness/contrast yang terbatas. Jangan mengubah tingkat pencahayaan secara ekstrem karena pencahayaan adalah target label.

## Target lanjutan

Target awal PRD adalah 300 foto pencahayaan, yaitu 100 foto per kelas `terang`, `redup`, dan `gelap`. Foto nyata dari kamera HP tetap diprioritaskan. Foto publik dapat digunakan sebagai data pendukung setelah sumber dan lisensinya tercatat.

## Checklist tahap

- [ ] Semua 44 foto tercatat sebagai data yang divalidasi.
- [ ] Metadata sumber dan lisensi dilengkapi.
- [ ] Kelas final ditetapkan.
- [ ] Group/session untuk mencegah leakage ditentukan.
- [ ] Dataset curated dibuat.
- [ ] Train/validation/test split dibuat.
- [ ] Distribusi kelas dicatat.
- [ ] Manifest dataset disimpan dan dapat direproduksi.
