# Minimal NES Emulator (Python)

This repository contains a tiny, educational NES emulator core focused on CPU execution only. It can load an iNES ROM, map PRG ROM into memory, and execute a small subset of 6502 instructions until a `BRK` instruction is reached.

## What's implemented

- iNES header parsing (PRG/CHR)
- 2KB RAM + simple PRG ROM mapping (NROM)
- Minimal 6502 CPU core with a small instruction set

## Quick start

```bash
python -m nes path/to/rom.nes --steps 10000
```

If the ROM executes a `BRK` instruction, execution stops and the CPU registers are printed.

## Notes

This is intentionally minimal and does **not** implement PPU, APU, or most memory-mapped I/O. It's meant as a starting point for experimentation and learning.
