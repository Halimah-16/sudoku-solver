"""Unit test Sudoku Solver. Jalankan: python -m pytest -v"""

import pytest

from sudoku import (count_solutions, generate, is_solved, is_valid_puzzle,
                    parse, solve, solve_basic)
from sudoku.board import format_board, to_string

MUDAH = "53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79"
SOLUSI_MUDAH = ("534678912672195348198342567859761423426853791"
                "713924856961537284287419635345286179")
SULIT = "8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4.."


def test_parse_format_satu_baris_dan_kotak():
    kotak = """
    5 3 . | . 7 . | . . .
    6 . . | 1 9 5 | . . .
    . 9 8 | . . . | . 6 .
    ------+-------+------
    8 . . | . 6 . | . . 3
    4 . . | 8 . 3 | . . 1
    7 . . | . 2 . | . . 6
    ------+-------+------
    . 6 . | . . . | 2 8 .
    . . . | 4 1 9 | . . 5
    . . . | . 8 . | . 7 9
    """
    assert parse(kotak) == parse(MUDAH)
    assert to_string(parse(MUDAH)) == MUDAH


def test_parse_jumlah_salah():
    with pytest.raises(ValueError):
        parse("123")


def test_deteksi_bentrokan():
    grid = parse(MUDAH)
    assert is_valid_puzzle(grid)
    grid[2] = 5  # angka 5 sudah ada di baris pertama
    assert not is_valid_puzzle(grid)


@pytest.mark.parametrize("fungsi", [solve, solve_basic])
def test_kedua_algoritma_menyelesaikan_soal(fungsi):
    hasil, stats = fungsi(parse(MUDAH))
    assert hasil == parse(SOLUSI_MUDAH)
    assert is_solved(hasil)
    assert stats.langkah > 0


def test_soal_sulit():
    hasil, _ = solve(parse(SULIT))
    assert is_solved(hasil)
    # angka soal tidak boleh berubah
    soal = parse(SULIT)
    assert all(s == 0 or s == h for s, h in zip(soal, hasil))


def test_optimasi_lebih_sedikit_langkah():
    _, cepat = solve(parse(SULIT))
    _, dasar = solve_basic(parse(SULIT))
    assert cepat.langkah < dasar.langkah


def test_soal_tanpa_solusi():
    # baris pertama butuh angka 9 di kotak terakhir, tetapi kolomnya sudah punya 9
    grid = parse("12345678." + "........9" + "." * 63)
    assert is_valid_puzzle(grid)
    assert solve(grid)[0] is None
    assert solve_basic(grid)[0] is None


def test_soal_tidak_valid_dikembalikan_none():
    grid = parse("11" + "." * 79)
    assert solve(grid)[0] is None


def test_hitung_solusi():
    assert count_solutions(parse(MUDAH)) == 1
    assert count_solutions(parse("." * 81), batas=5) == 5


def test_batas_langkah_basic():
    hasil, stats = solve_basic(parse(SULIT), batas_langkah=100)
    assert hasil is None and stats.dihentikan


@pytest.mark.parametrize("tingkat,target", [("mudah", 40), ("sedang", 32)])
def test_generator_solusi_tunggal(tingkat, target):
    grid = generate(tingkat, seed=42)
    assert is_valid_puzzle(grid)
    assert sum(1 for n in grid if n) >= target
    assert count_solutions(grid) == 1


def test_generator_tingkat_salah():
    with pytest.raises(ValueError):
        generate("mustahil")


def test_format_board():
    teks = format_board(parse(MUDAH))
    assert teks.count("\n") == 12
    assert "5 3 ." in teks
