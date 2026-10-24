# Sudoku Solver

Penyelesai dan pembuat teka-teki Sudoku yang ditulis dengan Python murni tanpa library eksternal. Proyek ini mengimplementasikan algoritma **backtracking** dalam dua versi, yaitu versi dasar dan versi teroptimasi, lalu membandingkan performa keduanya.

Pada soal tersulit di benchmark, versi teroptimasi menyelesaikan soal dengan **718 langkah dalam ~6 milidetik**, sementara backtracking dasar membutuhkan **hampir 10 juta langkah dan ~96 detik**.

## Fitur

- Menyelesaikan soal Sudoku apa pun yang valid, termasuk mendeteksi soal tanpa solusi dan soal dengan banyak solusi
- Dua algoritma: backtracking dasar dan backtracking dengan bitmask + heuristik MRV
- **Animasi** proses backtracking langkah demi langkah di terminal
- **Pembuat soal** baru dengan tiga tingkat kesulitan, dijamin memiliki solusi tunggal
- **Benchmark** untuk membandingkan kedua algoritma
- Menerima input dalam format satu baris maupun format kotak
- Menu interaktif dan antarmuka command line dengan `argparse`
- Unit test dengan pytest

## Contoh

```
$ python main.py solve "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4.."

Solusi (angka hijau diisi oleh solver):
+-------+-------+-------+
| 8 1 2 | 7 5 3 | 6 4 9 |
| 9 4 3 | 6 8 2 | 1 7 5 |
| 6 7 5 | 4 9 1 | 2 8 3 |
+-------+-------+-------+
| 1 5 4 | 2 3 7 | 8 9 6 |
| 3 6 9 | 8 4 5 | 7 2 1 |
| 2 8 7 | 1 6 9 | 5 3 4 |
+-------+-------+-------+
| 5 2 1 | 9 7 4 | 3 6 8 |
| 4 3 8 | 5 2 6 | 9 1 7 |
| 7 9 6 | 3 1 8 | 4 5 2 |
+-------+-------+-------+

Waktu    : 109,41 ms
Langkah  : 13.810
Backtrack: 13.750
```

## Cara Kerja Algoritma

### Backtracking dasar

Backtracking adalah teknik mencoba semua kemungkinan secara sistematis dan mundur begitu menemui jalan buntu:

1. Cari kotak kosong berikutnya (dari kiri atas ke kanan bawah).
2. Coba isi dengan angka 1 sampai 9.
3. Jika angka tersebut tidak bentrok dengan baris, kolom, dan blok 3×3, lanjutkan ke kotak kosong berikutnya.
4. Jika tidak ada angka yang cocok, kembali ke kotak sebelumnya dan coba angka lain (inilah *backtrack*).
5. Ulangi sampai semua kotak terisi.

Cara ini pasti menemukan jawaban jika ada, tetapi bisa sangat lambat karena sering baru menyadari kesalahan setelah mengisi banyak kotak.

### Versi teroptimasi

Versi ini menambahkan dua teknik:

**Bitmask.** Angka yang sudah dipakai di setiap baris, kolom, dan blok disimpan sebagai bit dalam satu bilangan bulat. Misalnya, jika baris berisi angka 1, 3, dan 9, nilainya `0b1000001010`. Untuk mengetahui kandidat sebuah kotak cukup satu operasi:

```python
kandidat = SEMUA & ~(baris[r] | kolom[c] | blok[b])
```

Tidak perlu lagi memeriksa 27 kotak satu per satu.

**Heuristik MRV (Minimum Remaining Values).** Daripada mengisi kotak secara berurutan, solver selalu memilih kotak kosong yang **kandidatnya paling sedikit**. Kotak dengan satu kandidat langsung terisi tanpa tebakan, dan kotak dengan nol kandidat langsung memicu backtrack. Akibatnya, kesalahan terdeteksi jauh lebih awal dan pohon pencarian menjadi jauh lebih kecil.

### Pembuat soal

1. Buat papan penuh yang valid dengan menjalankan solver pada papan kosong, mencoba angka dalam urutan acak.
2. Hapus angka satu per satu dalam urutan acak.
3. Setelah setiap penghapusan, hitung jumlah solusi. Jika lebih dari satu, kembalikan angka tersebut.
4. Berhenti ketika jumlah angka tersisa sesuai tingkat kesulitan (mudah 40, sedang 32, sulit 26).

## Benchmark

Hasil `python main.py benchmark` (angka bisa berbeda tergantung komputer):

| Soal | Dasar: waktu | Dasar: langkah | Teroptimasi: waktu | Teroptimasi: langkah |
|---|---:|---:|---:|---:|
| Mudah | 38 ms | 4.208 | 0,3 ms | 51 |
| Sedang | 1,8 ms | 200 | 0,3 ms | 49 |
| Sulit | 464 ms | 49.558 | 123 ms | 13.810 |
| Sangat sulit | ~96 detik | 9.727.396 | 6 ms | 718 |

Soal "Sangat sulit" dirancang khusus untuk menyulitkan solver yang mengisi kotak secara berurutan, sehingga perbedaannya sangat besar. Di sinilah heuristik MRV menunjukkan manfaatnya.

## Cara Menjalankan

**Prasyarat:** Python 3.8 atau lebih baru. Tidak ada library tambahan yang dibutuhkan untuk menjalankan aplikasi.

```bash
git clone https://github.com/Halimah-16/sudoku-solver.git
cd sudoku-solver

# Menu interaktif
python main.py

# Menyelesaikan soal (titik atau 0 untuk kotak kosong)
python main.py solve "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"

# Membaca soal dari file dan menampilkan animasi
python main.py solve --file soal.txt --animasi

# Memakai algoritma dasar
python main.py solve "53..7...." --algoritma dasar

# Membuat soal baru beserta solusinya
python main.py generate --tingkat sulit --solusi

# Membandingkan algoritma
python main.py benchmark
```

## Menjalankan Test

```bash
pip install -r requirements.txt
python -m pytest -v
```

## Struktur Proyek

```
sudoku-solver/
├── main.py              # Menu interaktif dan command line
├── sudoku/
│   ├── board.py         # Representasi papan, parsing, validasi
│   ├── solver.py        # Algoritma backtracking dasar & teroptimasi
│   └── generator.py     # Pembuat soal dengan solusi tunggal
├── puzzles/
│   └── contoh.txt       # Soal contoh untuk benchmark
├── tests/
│   └── test_sudoku.py
├── requirements.txt
└── LICENSE
```

## Rencana Pengembangan

- [ ] Algoritma Dancing Links (Algorithm X) dari Donald Knuth
- [ ] Teknik logika manusia (naked single, hidden single) sebelum backtracking
- [ ] Antarmuka grafis dengan Pygame atau versi web
- [ ] Menyelesaikan soal dari foto dengan OpenCV

## Lisensi

Proyek ini menggunakan lisensi [MIT](LICENSE).
