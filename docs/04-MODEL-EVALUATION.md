# Tahap 4 — Evaluasi Model CNN

## Tujuan

Menilai kemampuan model pada data yang tidak digunakan saat training dan memahami jenis kesalahan model.

## Metrik wajib

- Accuracy.
- Precision per kelas.
- Recall per kelas.
- F1-score per kelas.
- Macro F1-score.
- Confusion matrix.
- Waktu inferensi per gambar.

Accuracy tidak boleh menjadi satu-satunya indikator. Recall `gelap`, misalnya, perlu dianalisis terpisah karena kegagalan mengenali foto gelap dapat berdampak pada tujuan produk.

## Evaluasi empat kelas

Evaluasi awal dilakukan untuk:

```text
bukan_jalan, terang, redup, gelap
```

Untuk laporan API, prediksi `bukan_jalan` dipetakan menjadi foto tidak layak dan tidak dikembalikan sebagai kelas pencahayaan.

## Evaluasi kualitas dan kondisi nyata

Test harus mencakup variasi:

- Foto jernih.
- Foto sedikit buram.
- Noise malam.
- Resolusi rendah.
- Pencahayaan tidak merata.
- Lampu kendaraan atau lampu toko.
- Foto bukan jalan.
- Foto dari perangkat atau sumber yang tidak dominan di training.

## Analisis kesalahan

Simpan contoh false positive dan false negative. Untuk setiap kesalahan, catat:

- Label sebenarnya.
- Prediksi model.
- Confidence.
- Sumber atau group gambar.
- Dugaan penyebab kesalahan.
- Apakah perlu menambah data atau mengubah pedoman label.

## Threshold confidence

Confidence threshold tidak boleh dipilih hanya berdasarkan asumsi. Evaluasi threshold pada validation set dan pilih berdasarkan trade-off antara:

- Prediksi yang cukup meyakinkan.
- Jumlah foto yang diarahkan ke tinjauan manual.
- Kesalahan pada kelas pencahayaan.

Test set hanya digunakan untuk evaluasi akhir.

## Laporan evaluasi

Setiap eksperimen final harus menghasilkan:

```text
reports/
  classification_report.json
  confusion_matrix.png
  error_examples.csv
  evaluation_summary.md
```

Laporan harus mencantumkan keterbatasan jumlah gambar, sumber data, perangkat, dan kemungkinan leakage.

## Kriteria baseline

Baseline dianggap berhasil secara teknis jika:

- Model dapat dimuat ulang.
- Label mapping konsisten.
- Inference berjalan pada gambar baru.
- Metrik dapat dihasilkan otomatis.
- Kesalahan model dapat ditinjau.

Angka target produksi ditetapkan setelah dataset dan baseline cukup representatif.

## Checklist tahap

- [ ] Test set dikunci.
- [ ] Classification report dibuat.
- [ ] Confusion matrix dibuat.
- [ ] Metrik per kelas dianalisis.
- [ ] Waktu inferensi diukur.
- [ ] Threshold confidence dievaluasi.
- [ ] Kesalahan model dicatat.
- [ ] Keterbatasan evaluasi ditulis.
