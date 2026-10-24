"""
Representasi papan Sudoku.

Papan disimpan sebagai list berisi 81 bilangan bulat (baris demi baris),
dengan 0 menandakan kotak kosong. Indeks kotak = baris * 9 + kolom.
"""

from typing import List, Optional

Grid = List[int]

KOSONG = 0
UKURAN = 9


def parse(teks: str) -> Grid:
    """
    Mengubah teks menjadi papan Sudoku.

    Angka 1-9 dibaca sebagai isi kotak, sedangkan '0' atau '.' sebagai kotak
    kosong. Karakter lain (spasi, baris baru, '|', '-', '+') diabaikan,
    sehingga format satu baris maupun format kotak sama-sama bisa dibaca.
    """
    isi = []
    for ch in teks:
        if ch in "123456789":
            isi.append(int(ch))
        elif ch in "0.":
            isi.append(KOSONG)
    if len(isi) != 81:
        raise ValueError(f"Papan harus berisi 81 kotak, ditemukan {len(isi)}.")
    return isi


def to_string(grid: Grid) -> str:
    """Mengubah papan menjadi string satu baris (kotak kosong ditulis '.')."""
    return "".join(str(n) if n else "." for n in grid)


def format_board(grid: Grid, asli: Optional[Grid] = None) -> str:
    """
    Menampilkan papan dalam bentuk kotak yang mudah dibaca.

    Jika `asli` diberikan, angka yang diisi oleh solver akan diberi warna
    agar mudah dibedakan dari angka soal.
    """
    hijau, reset = "\033[32m", "\033[0m"
    garis = "+-------+-------+-------+"
    baris_teks = [garis]
    for r in range(UKURAN):
        sel = []
        for c in range(UKURAN):
            n = grid[r * 9 + c]
            simbol = str(n) if n else "."
            if asli is not None and n and not asli[r * 9 + c]:
                simbol = f"{hijau}{simbol}{reset}"
            sel.append(simbol)
        baris_teks.append(
            "| " + " ".join(sel[0:3]) + " | " + " ".join(sel[3:6])
            + " | " + " ".join(sel[6:9]) + " |")
        if r % 3 == 2:
            baris_teks.append(garis)
    return "\n".join(baris_teks)


def kotak_ke(indeks: int) -> int:
    """Nomor blok 3x3 (0-8) tempat sebuah kotak berada."""
    return (indeks // 27) * 3 + (indeks % 9) // 3


def is_valid_puzzle(grid: Grid) -> bool:
    """Memeriksa apakah angka-angka yang sudah ada tidak saling bentrok."""
    if len(grid) != 81 or any(not 0 <= n <= 9 for n in grid):
        return False
    baris = [set() for _ in range(9)]
    kolom = [set() for _ in range(9)]
    blok = [set() for _ in range(9)]
    for i, n in enumerate(grid):
        if n == KOSONG:
            continue
        r, c, b = i // 9, i % 9, kotak_ke(i)
        if n in baris[r] or n in kolom[c] or n in blok[b]:
            return False
        baris[r].add(n)
        kolom[c].add(n)
        blok[b].add(n)
    return True


def is_solved(grid: Grid) -> bool:
    """Papan selesai jika tidak ada kotak kosong dan tidak ada bentrokan."""
    return KOSONG not in grid and is_valid_puzzle(grid)
