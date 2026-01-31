from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class INESRom:
    prg_rom: bytes
    chr_rom: bytes

    @classmethod
    def load(cls, path: str | Path) -> "INESRom":
        data = Path(path).read_bytes()
        if len(data) < 16 or data[0:4] != b"NES\x1a":
            raise ValueError("Invalid iNES header")
        prg_banks = data[4]
        chr_banks = data[5]
        flags6 = data[6]
        has_trainer = bool(flags6 & 0x04)
        offset = 16 + (512 if has_trainer else 0)
        prg_size = prg_banks * 16 * 1024
        chr_size = chr_banks * 8 * 1024
        prg_rom = data[offset : offset + prg_size]
        chr_rom = data[offset + prg_size : offset + prg_size + chr_size]
        return cls(prg_rom=prg_rom, chr_rom=chr_rom)
