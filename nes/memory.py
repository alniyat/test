from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Memory:
    """Minimal NES memory map with 2KB RAM and PRG ROM mapping.

    This intentionally ignores PPU/APU/I/O registers and only provides
    simple reads/writes for early experiments.
    """

    ram: bytearray
    prg_rom: bytes

    @classmethod
    def with_rom(cls, prg_rom: bytes) -> "Memory":
        return cls(ram=bytearray(0x800), prg_rom=prg_rom)

    def read(self, addr: int) -> int:
        addr &= 0xFFFF
        if addr < 0x2000:
            return self.ram[addr % 0x800]
        if 0x8000 <= addr <= 0xFFFF:
            return self._read_prg(addr)
        return 0x00

    def write(self, addr: int, value: int) -> None:
        addr &= 0xFFFF
        value &= 0xFF
        if addr < 0x2000:
            self.ram[addr % 0x800] = value
            return
        # Writes to ROM and I/O are ignored in this minimal implementation.

    def _read_prg(self, addr: int) -> int:
        if len(self.prg_rom) == 0x4000:
            return self.prg_rom[(addr - 0x8000) % 0x4000]
        return self.prg_rom[addr - 0x8000]
