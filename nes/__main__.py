from __future__ import annotations

import argparse

from .cpu import CPU
from .ines import INESRom
from .memory import Memory


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal NES emulator")
    parser.add_argument("rom", help="Path to iNES ROM")
    parser.add_argument("--steps", type=int, default=None, help="Max CPU steps")
    args = parser.parse_args()

    rom = INESRom.load(args.rom)
    memory = Memory.with_rom(rom.prg_rom)
    cpu = CPU(memory)
    cpu.reset()
    executed = cpu.run(max_steps=args.steps)

    print("Stopped after", executed, "steps")
    print(
        f"A={cpu.a:02X} X={cpu.x:02X} Y={cpu.y:02X} "
        f"SP={cpu.sp:02X} PC={cpu.pc:04X} STATUS={cpu.status:02X}"
    )


if __name__ == "__main__":
    main()
