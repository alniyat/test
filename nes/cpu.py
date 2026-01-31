from __future__ import annotations

from dataclasses import dataclass

from .memory import Memory


FLAG_CARRY = 0x01
FLAG_ZERO = 0x02
FLAG_INTERRUPT = 0x04
FLAG_DECIMAL = 0x08
FLAG_BREAK = 0x10
FLAG_UNUSED = 0x20
FLAG_OVERFLOW = 0x40
FLAG_NEGATIVE = 0x80


@dataclass
class CPU:
    memory: Memory
    a: int = 0
    x: int = 0
    y: int = 0
    sp: int = 0xFD
    pc: int = 0
    status: int = FLAG_UNUSED | FLAG_INTERRUPT

    def reset(self) -> None:
        self.sp = 0xFD
        self.status = FLAG_UNUSED | FLAG_INTERRUPT
        self.pc = self._read_word(0xFFFC)

    def step(self) -> int:
        opcode = self._fetch_byte()
        if opcode == 0x00:  # BRK
            self.status |= FLAG_BREAK
            return 7
        if opcode == 0xEA:  # NOP
            return 2
        if opcode == 0xA9:  # LDA #imm
            value = self._fetch_byte()
            self.a = value
            self._update_zn(self.a)
            return 2
        if opcode == 0xA5:  # LDA zp
            addr = self._fetch_byte()
            self.a = self.memory.read(addr)
            self._update_zn(self.a)
            return 3
        if opcode == 0xAD:  # LDA abs
            addr = self._fetch_word()
            self.a = self.memory.read(addr)
            self._update_zn(self.a)
            return 4
        if opcode == 0x85:  # STA zp
            addr = self._fetch_byte()
            self.memory.write(addr, self.a)
            return 3
        if opcode == 0x8D:  # STA abs
            addr = self._fetch_word()
            self.memory.write(addr, self.a)
            return 4
        if opcode == 0xA2:  # LDX #imm
            self.x = self._fetch_byte()
            self._update_zn(self.x)
            return 2
        if opcode == 0xE8:  # INX
            self.x = (self.x + 1) & 0xFF
            self._update_zn(self.x)
            return 2
        if opcode == 0xCA:  # DEX
            self.x = (self.x - 1) & 0xFF
            self._update_zn(self.x)
            return 2
        if opcode == 0x4C:  # JMP abs
            self.pc = self._fetch_word()
            return 3
        if opcode == 0x20:  # JSR
            addr = self._fetch_word()
            self._push_word((self.pc - 1) & 0xFFFF)
            self.pc = addr
            return 6
        if opcode == 0x60:  # RTS
            self.pc = (self._pop_word() + 1) & 0xFFFF
            return 6
        if opcode == 0x78:  # SEI
            self.status |= FLAG_INTERRUPT
            return 2
        if opcode == 0xD8:  # CLD
            self.status &= ~FLAG_DECIMAL
            return 2
        if opcode == 0x9A:  # TXS
            self.sp = self.x
            return 2
        if opcode == 0xBA:  # TSX
            self.x = self.sp
            self._update_zn(self.x)
            return 2
        if opcode == 0x48:  # PHA
            self._push_byte(self.a)
            return 3
        if opcode == 0x68:  # PLA
            self.a = self._pop_byte()
            self._update_zn(self.a)
            return 4
        if opcode == 0x69:  # ADC #imm
            value = self._fetch_byte()
            self._adc(value)
            return 2
        raise NotImplementedError(f"Unsupported opcode: {opcode:02X}")

    def run(self, max_steps: int | None = None) -> int:
        steps = 0
        while max_steps is None or steps < max_steps:
            opcode = self.memory.read(self.pc)
            if opcode == 0x00:
                self.step()
                return steps + 1
            self.step()
            steps += 1
        return steps

    def _fetch_byte(self) -> int:
        value = self.memory.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def _fetch_word(self) -> int:
        low = self._fetch_byte()
        high = self._fetch_byte()
        return low | (high << 8)

    def _read_word(self, addr: int) -> int:
        low = self.memory.read(addr)
        high = self.memory.read(addr + 1)
        return low | (high << 8)

    def _push_byte(self, value: int) -> None:
        self.memory.write(0x0100 + self.sp, value)
        self.sp = (self.sp - 1) & 0xFF

    def _push_word(self, value: int) -> None:
        self._push_byte((value >> 8) & 0xFF)
        self._push_byte(value & 0xFF)

    def _pop_byte(self) -> int:
        self.sp = (self.sp + 1) & 0xFF
        return self.memory.read(0x0100 + self.sp)

    def _pop_word(self) -> int:
        low = self._pop_byte()
        high = self._pop_byte()
        return low | (high << 8)

    def _update_zn(self, value: int) -> None:
        if value == 0:
            self.status |= FLAG_ZERO
        else:
            self.status &= ~FLAG_ZERO
        if value & 0x80:
            self.status |= FLAG_NEGATIVE
        else:
            self.status &= ~FLAG_NEGATIVE

    def _adc(self, value: int) -> None:
        carry = 1 if (self.status & FLAG_CARRY) else 0
        result = self.a + value + carry
        self.status = (self.status & ~FLAG_CARRY) | (FLAG_CARRY if result > 0xFF else 0)
        result &= 0xFF
        self._update_zn(result)
        self.a = result
