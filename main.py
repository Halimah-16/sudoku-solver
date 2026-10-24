"""
Sudoku Solver - aplikasi command line.

Contoh penggunaan:
    python main.py                          # menu interaktif
    python main.py solve "53..7....6..195..."  # selesaikan soal
    python main.py solve --file soal.txt --animasi
    python main.py generate --tingkat sulit
    python main.py benchmark
"""

import argparse
import os
import sys
import time

from sudoku import (count_solutions, format_board, generate, is_valid_puzzle,
                    parse, solve, solve_basic)
from sudoku.board import to_string

FILE_CONTOH = os.path.join(os.path.dirname(__file__), "puzzles", "contoh.txt")

if os.name == "nt":
    os.system("")  # mengaktifkan warna ANSI di terminal Windows


# ---------------------------------------------------------------------------
# Fungsi bantu
# ---------------------------------------------------------------------------
def angka(nilai, desimal=0):
    """Format angka gaya Indonesia: 12.345,67"""
    teks = f"{nilai:,.{desimal}f}"
    return teks.replace(",", "_").replace(".", ",").replace("_", ".")


def baca_soal_contoh():
    """Membaca file contoh, mengembalikan list (nama, grid)."""
    soal = []
    with open(FILE_CONTOH, encoding="utf-8") as f:
        for baris in f:
            baris = baris.strip()
            if not baris or baris.startswith("#"):
                continue
            nama, isi = baris.split("|", 1)
            soal.append((nama.strip(), parse(isi)))
    return soal


def tampilkan_animasi(grid, jeda):
    """Menyelesaikan sambil menampilkan setiap langkah di terminal."""
    papan = list(grid)
    print("\033[2J", end="")  # bersihkan layar

    def langkah(i, angka):
        papan[i] = angka
        print("\033[H", end="")  # kursor ke kiri atas
        print(format_board(papan, grid))
        time.sleep(jeda)

    return solve(grid, on_step=langkah)


def selesaikan_dan_tampilkan(grid, algoritma="cepat", animasi=False, jeda=0.02):
    if not is_valid_puzzle(grid):
        print("Soal tidak valid: ada angka yang bentrok di baris, kolom, atau blok.")
        return False

    print("Soal:")
    print(format_board(grid))

    if animasi:
        hasil, stats = tampilkan_animasi(grid, jeda)
    elif algoritma == "dasar":
        hasil, stats = solve_basic(grid)
    else:
        hasil, stats = solve(grid)

    if hasil is None:
        print("\nSoal ini tidak memiliki solusi.")
        return False

    print("\nSolusi (angka hijau diisi oleh solver):")
    print(format_board(hasil, grid))
    print(f"\nWaktu    : {angka(stats.waktu * 1000, 2)} ms")
    print(f"Langkah  : {angka(stats.langkah)}")
    print(f"Backtrack: {angka(stats.backtrack)}")
    if count_solutions(grid, batas=2) > 1:
        print("Catatan  : soal ini memiliki lebih dari satu solusi.")
    return True


# ---------------------------------------------------------------------------
# Perintah
# ---------------------------------------------------------------------------
def cmd_solve(args):
    try:
        if args.file:
            with open(args.file, encoding="utf-8") as f:
                grid = parse(f.read())
        elif args.soal:
            grid = parse(args.soal)
        else:
            print("Berikan soal sebagai teks atau dengan --file.")
            return 1
    except (OSError, ValueError) as e:
        print(f"Gagal membaca soal: {e}")
        return 1
    ok = selesaikan_dan_tampilkan(grid, args.algoritma, args.animasi, args.jeda)
    return 0 if ok else 1


def cmd_generate(args):
    print(f"Membuat soal tingkat {args.tingkat}...")
    grid = generate(args.tingkat, seed=args.seed)
    terisi = sum(1 for n in grid if n)
    print(format_board(grid))
    print(f"\n{terisi} angka terisi, solusi tunggal.")
    print(f"Format satu baris: {to_string(grid)}")
    if args.solusi:
        hasil, _ = solve(grid)
        print("\nSolusi:")
        print(format_board(hasil, grid))
    return 0


def cmd_benchmark(args):
    batas = args.batas
    print(f"Membandingkan kedua algoritma (backtracking dasar dibatasi "
          f"{angka(batas)} langkah).\n")
    kepala = f"{'Soal':<14}{'Dasar (ms)':>14}{'Langkah':>14}{'Cepat (ms)':>14}{'Langkah':>12}"
    print(kepala)
    print("-" * len(kepala))
    for nama, grid in baca_soal_contoh():
        _, sd = solve_basic(grid, batas_langkah=batas)
        _, sc = solve(grid)
        waktu_dasar = angka(sd.waktu * 1000, 2)
        langkah_dasar = angka(sd.langkah)
        if sd.dihentikan:
            waktu_dasar, langkah_dasar = "> " + waktu_dasar, "> " + angka(batas)
        print(f"{nama:<14}{waktu_dasar:>14}{langkah_dasar:>14}"
              f"{angka(sc.waktu * 1000, 2):>14}{angka(sc.langkah):>12}")
    print("\nTanda > berarti backtracking dasar dihentikan karena terlalu lama.")
    return 0


# ---------------------------------------------------------------------------
# Menu interaktif (dijalankan tanpa argumen)
# ---------------------------------------------------------------------------
def menu_interaktif():
    while True:
        print("\n" + "=" * 36)
        print("          SUDOKU SOLVER")
        print("=" * 36)
        print("1. Selesaikan soal contoh")
        print("2. Masukkan soal sendiri")
        print("3. Lihat animasi backtracking")
        print("4. Buat soal baru")
        print("5. Bandingkan algoritma (benchmark)")
        print("0. Keluar")
        pilihan = input("Pilih: ").strip()

        if pilihan == "1":
            soal = baca_soal_contoh()
            for i, (nama, _) in enumerate(soal, 1):
                print(f"  {i}. {nama}")
            try:
                nomor = int(input("Nomor soal: ")) - 1
                selesaikan_dan_tampilkan(soal[nomor][1])
            except (ValueError, IndexError):
                print("Nomor tidak valid.")
        elif pilihan == "2":
            print("Ketik 81 angka (0 atau titik untuk kotak kosong).")
            print("Boleh dalam satu baris atau 9 baris; tekan Enter kosong untuk selesai.")
            baris = []
            while True:
                b = input()
                if not b.strip():
                    break
                baris.append(b)
            try:
                selesaikan_dan_tampilkan(parse("\n".join(baris)))
            except ValueError as e:
                print(e)
        elif pilihan == "3":
            nama, grid = baca_soal_contoh()[0]
            selesaikan_dan_tampilkan(grid, animasi=True, jeda=0.05)
        elif pilihan == "4":
            tingkat = input("Tingkat (mudah/sedang/sulit) [sedang]: ").strip() or "sedang"
            try:
                cmd_generate(argparse.Namespace(tingkat=tingkat, seed=None, solusi=False))
            except ValueError as e:
                print(e)
        elif pilihan == "5":
            cmd_benchmark(argparse.Namespace(batas=2_000_000))
        elif pilihan == "0":
            print("Sampai jumpa!")
            return
        else:
            print("Pilihan tidak valid.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Penyelesai dan pembuat teka-teki Sudoku dengan algoritma backtracking.")
    sub = parser.add_subparsers(dest="perintah")

    p_solve = sub.add_parser("solve", help="menyelesaikan soal Sudoku")
    p_solve.add_argument("soal", nargs="?", help="81 karakter, titik atau 0 untuk kotak kosong")
    p_solve.add_argument("--file", help="baca soal dari file teks")
    p_solve.add_argument("--algoritma", choices=["cepat", "dasar"], default="cepat")
    p_solve.add_argument("--animasi", action="store_true", help="tampilkan proses langkah demi langkah")
    p_solve.add_argument("--jeda", type=float, default=0.02, help="jeda animasi dalam detik")
    p_solve.set_defaults(fungsi=cmd_solve)

    p_gen = sub.add_parser("generate", help="membuat soal baru")
    p_gen.add_argument("--tingkat", choices=["mudah", "sedang", "sulit"], default="sedang")
    p_gen.add_argument("--seed", type=int, help="angka acak tetap agar hasil bisa diulang")
    p_gen.add_argument("--solusi", action="store_true", help="tampilkan juga solusinya")
    p_gen.set_defaults(fungsi=cmd_generate)

    p_bench = sub.add_parser("benchmark", help="membandingkan kedua algoritma")
    p_bench.add_argument("--batas", type=int, default=2_000_000,
                         help="batas langkah untuk backtracking dasar")
    p_bench.set_defaults(fungsi=cmd_benchmark)

    args = parser.parse_args(argv)
    if args.perintah is None:
        menu_interaktif()
        return 0
    return args.fungsi(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nDihentikan.")
