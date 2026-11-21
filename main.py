# Entrypoint edisi koran gambar 20 November 2026 (v7).
#
# File ini sengaja dibuat sesederhana mungkin: mengambil gambar koran
# yang sudah selesai dirender (entry.png, satu folder dengan file ini)
# lalu menaruh salinannya di folder output yang dipakai penilai.
# Tidak ada pengolahan gambar di sini - render sudah dilakukan di luar,
# jadi file ini hanya memindahkan hasil akhirnya ke tempat yang benar.
# Sengaja hanya memakai modul bawaan Python supaya jalan di image
# python:3.13-slim tanpa Pillow atau paket tambahan apa pun.

from os import environ
from pathlib import Path
from shutil import copyfile

SOURCE_NAME = "entry.png"
DEFAULT_DIR = "/output"


def locate_source():
    # Gambar sumber tinggal di direktori yang sama dengan file ini,
    # sehingga perintah boleh dijalankan dari folder kerja mana saja
    # tanpa mengubah di mana gambar itu dicari.
    here = Path(__file__).resolve().parent
    return here / SOURCE_NAME


def resolve_target_dir():
    # Folder tujuan dibaca dari variabel lingkungan penilai; bila
    # kosong atau tidak diset, pakai jalur baku /output.
    raw = environ.get("MAKEFUN_OUTPUT_DIR", DEFAULT_DIR)
    cleaned = raw.strip() or DEFAULT_DIR
    return Path(cleaned)


def deliver():
    source = locate_source()
    if not source.is_file():
        print(f"missing source image: {source}")
        return 1
    target_dir = resolve_target_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / SOURCE_NAME
    copyfile(source, destination)
    print(f"copied {source.name} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(deliver())
