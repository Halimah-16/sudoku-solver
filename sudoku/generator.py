"""
Pembuat teka-teki Sudoku.

Langkahnya:
1. Buat papan penuh yang valid secara acak.
2. Hapus angka satu per satu dengan urutan acak.
3. Setiap kali menghapus, pastikan teka-teki masih punya TEPAT SATU solusi.
   Jika tidak, kembalikan angka tersebut.
4. Berhenti ketika jumlah angka tersisa sesuai tingkat kesulitan.
"""

import random
from typing import Optional

from .board import Grid, KOSONG
from .solver import count_solutions, random_full_grid

TINGKAT = {
    "mudah": 40,
    "sedang": 32,
    "sulit": 26,
}


def generate(tingkat: str = "sedang", seed: Optional[int] = None) -> Grid:
    """Membuat teka-teki Sudoku dengan solusi tunggal."""
    if tingkat not in TINGKAT:
        raise ValueError(f"Tingkat harus salah satu dari: {', '.join(TINGKAT)}")
    if seed is not None:
        random.seed(seed)

    target = TINGKAT[tingkat]
    papan = random_full_grid()
    urutan = list(range(81))
    random.shuffle(urutan)
    terisi = 81

    for i in urutan:
        if terisi <= target:
            break
        cadangan = papan[i]
        papan[i] = KOSONG
        if count_solutions(papan, batas=2) != 1:
            papan[i] = cadangan  # solusi jadi lebih dari satu, batalkan
        else:
            terisi -= 1
    return papan
