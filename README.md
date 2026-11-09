# AR Hand Tracking (Sci-Fi Pro)

Aplikasi computer vision interaktif real-time berbasis Python, MediaPipe Tasks, dan OpenCV untuk deteksi gestur tangan, visualisasi cyber skeleton, dan manipulasi Augmented Reality (AR) bertema Sci-Fi.

---

## 📌 Gambaran Proyek

Proyek ini memanfaatkan model **MediaPipe Hand Landmarker** dan pemrosesan video asinkron (**Threaded Camera**) untuk menghasilkan interaksi visual yang halus (~60 FPS). 

Pengguna dapat memanipulasi jendela portal dimensi AR di antara kedua tangan, mengganti shader/filter visual secara real-time, mengisi daya tembakan ketapel energi (*slingshot mode*), mengambil foto snapshot dengan gestur tangan, serta mereset sistem dengan gestur sederhana.

---

## ✨ Fitur Utama

- **Real-Time Hand Tracking & Cyber Skeleton**:
  - Pelacakan hingga 2 tangan secara simultan.
  - Visualisasi sendi tangan dengan tema cyber skeleton neon dan node bercahaya.
  - Akselerasi deteksi berbasis proxy resolution (320x180) untuk inferensi ringan (~11 ms) pada canvas 720p.

- **Interactive AR Portal (Dimension Window)**:
  - Membuka kotak portal dimensi dinamis yang terbentuk dari 4 titik ujung jari (telunjuk & jempol kedua tangan).
  - Dilengkapi efek aura cahaya bertingkat (*multi-layer glow*), cincin energi berdenyut, dan partikel percikan energi (*Doctor Strange energy sparks*).
  - Smoothing temporal (*Exponential Moving Average*) untuk mengurangi getaran koordinat (*jitter*).
  - Pemrosesan ROI terpotong (*bounding box cropping*) untuk menghemat beban pemrosesan CPU.

- **Koleksi Sci-Fi Shaders / Visual Filters**:
  1. `CYBER NEON`: Deteksi kontur tepi Canny berpadu aksen neon cyan.
  2. `THERMAL SENSOR`: Visualisasi panas inframerah menggunakan colormap Inferno.
  3. `MATRIX HOLOGRAM`: Efek scanline hologram hijau monokrom.
  4. `SYNTHWAVE 80s`: Palet gradasi retro magenta-ungu dengan colormap Magma.
  5. `CHROMATIC GLITCH`: Efek aberasi kromatik dan pergeseran warna channel RGB.
  6. `VINTAGE SEPIA`: Transformasi matriks warna bernuansa klasik/sepia.

- **Mekanik Gestur & Kontrol Interaktif**:
  - **Ganti Filter / Cycle Shader**: Cubit tangan kiri (*left pinch*) untuk berpindah ke filter visual berikutnya secara berurutan disertai efek audio.
  - **Ketapel Energi / Slingshot Charge**: Bentangkan tangan kiri dan tarik cubitan jempol tangan kanan ke belakang. Menampilkan laser bidikan, reticle dinamis, dan meteran tegangan (*tension meter*).
  - **Full-Screen Overload**: Lepaskan cubitan tangan kanan saat tarikan ketapel mencapai 100% untuk memicu ledakan shockwave, kilatan layar (*white screen flash*), dan mengaktifkan filter ke seluruh layar.
  - **Reality Window**: Saat mode Full-Screen Overload aktif, kotak portal AR berfungsi sebagai jendela tembus pandang yang menampilkan feed kamera asli tanpa filter.
  - **Snapshot Foto (Peace Sign ✌️)**: Gestur peace sign untuk mengambil tangkapan layar beresolusi penuh. File otomatis tersimpan ke penyimpanan lokal (`snapshot_ar_<timestamp>.png`) dengan efek flash shutter kamera.
  - **System Reset (Telapak Terbuka 🖐️)**: Buka 5 jari telapak tangan untuk mereset mode overload dan menormalkan kembali sistem ke status awal.

- **Audio Feedback Non-Blocking**:
  - Respon suara sintetis (SFX) di background thread saat mengganti filter, mengisi daya ketapel, menembak, mengambil foto, dan melakukan reset sistem tanpa menurunkan FPS.

- **Futuristic HUD**:
  - Tampilan informasi status sistem, filter aktif, mode operasional, dan indikator FPS real-time di bagian atas layar.

---

## 🛠️ Persyaratan Sistem & Instalasi

### 1. Prasyarat
- Python 3.9+
- Webcam / Kamera terhubung
- Sistem Operasi: Windows (untuk audio bawaan `winsound`) / Linux / macOS

### 2. Instalasi Dependensi
Clone repositori ini dan pasang dependensi:

```bash
git clone https://github.com/aldwrnnnnn/hand_tracking.git
cd hand_tracking
pip install -r requirements.txt
```

### 3. File Model MediaPipe
File model `hand_landmarker.task` sudah disertakan langsung di dalam repositori ini. Pastikan file berada di direktori yang sama dengan `main.py`.

---

## 🚀 Cara Menjalankan

Jalankan skrip utama:

```bash
python main.py
```

### Kontrol Tombol:
- Tekan tombol **`q`** pada keyboard untuk menghentikan program dan menutup jendela tampilan kamera.

---

## 🎮 Ringkasan Panduan Gestur

| Gestur | Aksi | Deskripsi |
|---|---|---|
| **Dua Tangan Terbuka** | AR Portal | Membentuk jendela dimensi AR di antara ujung jari kedua tangan |
| **Cubit Tangan Kiri** | Ganti Shader | Berpindah ke filter visual berikutnya |
| **Tarik Cubit Tangan Kanan** | Slingshot Charge | Membidik dan menarik ketapel energi |
| **Lepas Tangan Kanan (100%)** | Overload Blast | Memicu ledakan energi dan mengaktifkan filter layar penuh |
| **Peace Sign (✌️)** | Snapshot Foto | Mengambil foto dan menyimpan file ke disk |
| **Telapak Terbuka (🖐️)** | System Reset | Menormalkan sistem kembali ke status awal |

---

## 📄 Hak Cipta & Lisensi

Proyek ini dibuat dan dimiliki sepenuhnya oleh **aldwrnnnnn (Gede Aldi Irawan)**.

Hak Cipta © 2026 **aldwrnnnnn (Gede Aldi Irawan)**. Seluruh hak cipta dilindungi undang-undang.

Proyek ini dilisensikan di bawah [MIT License](LICENSE). Anda diperkenankan menggunakan, memodifikasi, dan mendistribusikan kode ini dengan tetap menyertakan informasi hak cipta asli pembuat proyek.
