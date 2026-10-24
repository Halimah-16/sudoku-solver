"""
Algoritma penyelesaian Sudoku.

Terdapat dua versi:

1. `solve_basic` - backtracking murni. Mengisi kotak kosong secara berurutan
   dari kiri atas, mencoba angka 1-9, dan mundur (backtrack) jika buntu.
   Mudah dipahami, tetapi bisa lambat untuk soal sulit.

2. `solve` - backtracking dengan dua optimasi:
   - Bitmask: angka yang sudah dipakai di setiap baris, kolom, dan blok
     disimpan sebagai bit, sehingga pengecekan cukup satu operasi.
   - Heuristik MRV (Minimum Remaining Values): selalu memilih kotak dengan
     kandidat paling sedikit. Kotak yang hanya punya satu kemungkinan langsung
     terisi, dan kebuntuan terdeteksi jauh lebih awal.
"""

import random
import time
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from .board import Grid, KOSONG, is_valid_puzzle, kotak_ke

SEMUA = 0b1111111110  # bit 1..9 menyala

# Callback opsional untuk visualisasi: dipanggil (indeks, angka) setiap
# kali solver mengisi (angka > 0) atau menghapus (angka = 0) sebuah kotak.
Callback = Optional[Callable[[int, int], None]]


@dataclass
class SolverStats:
    """Statistik proses penyelesaian, berguna untuk membandingkan algoritma."""
    langkah: int = 0      # berapa kali angka dicoba ditempatkan
    backtrack: int = 0    # berapa kali solver harus mundur
    waktu: float = 0.0    # detik
    dihentikan: bool = False  # True jika melewati batas langkah


class _BatasTercapai(Exception):
    pass


# ======================================================================
# Versi 1: backtracking dasar
# ======================================================================
def _aman(grid: Grid, indeks: int, angka: int) -> bool:
    r, c = divmod(indeks, 9)
    if any(grid[r * 9 + k] == angka for k in range(9)):
        return False
    if any(grid[k * 9 + c] == angka for k in range(9)):
        return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            if grid[rr * 9 + cc] == angka:
                return False
    return True


def solve_basic(grid: Grid, on_step: Callback = None,
                batas_langkah: Optional[int] = None
                ) -> Tuple[Optional[Grid], SolverStats]:
    """
    Menyelesaikan Sudoku dengan backtracking murni.

    `batas_langkah` (opsional) menghentikan pencarian jika terlalu lama;
    dalam hal itu hasilnya None dan `stats.dihentikan` bernilai True.
    """
    stats = SolverStats()
    if not is_valid_puzzle(grid):
        return None, stats
    papan = list(grid)
    kosong = [i for i, n in enumerate(papan) if n == KOSONG]
    mulai = time.perf_counter()

    def bt(pos: int) -> bool:
        if pos == len(kosong):
            return True
        i = kosong[pos]
        for angka in range(1, 10):
            if _aman(papan, i, angka):
                papan[i] = angka
                stats.langkah += 1
                if batas_langkah and stats.langkah > batas_langkah:
                    raise _BatasTercapai
                if on_step:
                    on_step(i, angka)
                if bt(pos + 1):
                    return True
                papan[i] = KOSONG
                stats.backtrack += 1
                if on_step:
                    on_step(i, KOSONG)
        return False

    try:
        berhasil = bt(0)
    except _BatasTercapai:
        berhasil = False
        stats.dihentikan = True
    stats.waktu = time.perf_counter() - mulai
    return (papan if berhasil else None), stats


# ======================================================================
# Versi 2: backtracking + bitmask + heuristik MRV
# ======================================================================
class _Pencari:
    def __init__(self, grid: Grid, acak: bool = False, on_step: Callback = None):
        self.papan = list(grid)
        self.baris = [0] * 9
        self.kolom = [0] * 9
        self.blok = [0] * 9
        self.acak = acak
        self.on_step = on_step
        self.stats = SolverStats()
        for i, n in enumerate(self.papan):
            if n:
                self._pasang(i, n)

    def _pasang(self, i: int, n: int) -> None:
        bit = 1 << n
        self.papan[i] = n
        self.baris[i // 9] |= bit
        self.kolom[i % 9] |= bit
        self.blok[kotak_ke(i)] |= bit

    def _lepas(self, i: int, n: int) -> None:
        bit = ~(1 << n)
        self.papan[i] = KOSONG
        self.baris[i // 9] &= bit
        self.kolom[i % 9] &= bit
        self.blok[kotak_ke(i)] &= bit

    def _kandidat(self, i: int) -> int:
        terpakai = self.baris[i // 9] | self.kolom[i % 9] | self.blok[kotak_ke(i)]
        return SEMUA & ~terpakai

    def _pilih_kotak(self) -> Tuple[int, int]:
        """Mengembalikan (indeks, kandidat) dari kotak kosong tersempit.
        Indeks -1 berarti papan sudah penuh."""
        terbaik, mask_terbaik, jumlah_terbaik = -1, 0, 10
        for i in range(81):
            if self.papan[i] == KOSONG:
                mask = self._kandidat(i)
                jumlah = bin(mask).count("1")
                if jumlah < jumlah_terbaik:
                    terbaik, mask_terbaik, jumlah_terbaik = i, mask, jumlah
                    if jumlah <= 1:
                        break  # tidak mungkin lebih baik lagi
        return terbaik, mask_terbaik

    def cari(self, batas: int = 1) -> List[Grid]:
        """Mencari hingga `batas` solusi."""
        hasil: List[Grid] = []

        def bt() -> bool:
            i, mask = self._pilih_kotak()
            if i == -1:
                hasil.append(list(self.papan))
                return len(hasil) >= batas
            angka_list = [n for n in range(1, 10) if mask & (1 << n)]
            if self.acak:
                random.shuffle(angka_list)
            for n in angka_list:
                self._pasang(i, n)
                self.stats.langkah += 1
                if self.on_step:
                    self.on_step(i, n)
                if bt():
                    return True
                self._lepas(i, n)
                self.stats.backtrack += 1
                if self.on_step:
                    self.on_step(i, KOSONG)
            return False

        mulai = time.perf_counter()
        bt()
        self.stats.waktu = time.perf_counter() - mulai
        return hasil


def solve(grid: Grid, on_step: Callback = None
          ) -> Tuple[Optional[Grid], SolverStats]:
    """Menyelesaikan Sudoku dengan backtracking teroptimasi (bitmask + MRV)."""
    if not is_valid_puzzle(grid):
        return None, SolverStats()
    pencari = _Pencari(grid, on_step=on_step)
    hasil = pencari.cari(batas=1)
    return (hasil[0] if hasil else None), pencari.stats


def count_solutions(grid: Grid, batas: int = 2) -> int:
    """
    Menghitung jumlah solusi, berhenti saat mencapai `batas`.
    Sudoku yang baik hanya memiliki tepat satu solusi.
    """
    if not is_valid_puzzle(grid):
        return 0
    return len(_Pencari(grid).cari(batas=batas))


def random_full_grid() -> Grid:
    """Membuat papan penuh yang valid secara acak (dipakai oleh generator)."""
    return _Pencari([KOSONG] * 81, acak=True).cari(batas=1)[0]
