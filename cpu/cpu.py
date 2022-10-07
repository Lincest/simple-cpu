import sys


def log(msg, should_exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if should_exit:
        sys.exit(-1)


class Cpu:
    def __init__(self):
        self.pc = 0
        self.register = 12 * [0]  # r1 ~ r12 (int saved)
        self.state = 0
        self.memory = bytearray(16 * 1024)  # 16KB memory
        self.memory_range = (0, 16 * 1024)  # the space range (16KB)
        self.instructions = [  # instructions
            self._nop,
            self._load,
            self._movi,
            self._store,
            self._inc,
            self._comi,
            self._jnz,
            self._halt,
            self._add,
        ]

    # load program (file after assembler compilation)
    def load_file(self, path):
        with open(path, 'rb') as f:
            code = bytearray(f.read())
            self.memory[0:len(code)] = code
            log("memory size = %dB" % len(self.memory))
            if len(self.memory) > self.memory_range[1]:
                raise RuntimeError('memory limit exceed')

    def fetch_instruction(self):
        # out of range
        if self.pc < self.memory_range[0] or self.pc > self.memory_range[1]:
            log("pc out of range: pc=0x%x" % self.pc, should_exit=True)

        inst_no = self.memory[self.pc]
        if inst_no >= len(self.instructions):
            log("invalid instruction number: %d" % inst_no, should_exit=True)

        # 4B of instruction
        instruction = self.memory[self.pc:self.pc + 4]
        return instruction

    def exec(self):
        while True:
            ins = self.fetch_instruction()
            instruction = self.instructions[ins[0]]
            instruction(ins)

    def pc_next(self):
        self.pc += 4

    # ------ instructions ----------

    def _nop(self, ins: list):
        log("[exec] no operation")
        self.pc_next()

    def _load(self, ins: list):
        tr, sr = ins[1], ins[2]
        address = self.register[sr]
        if address < self.memory_range[0] or address > self.memory_range[1]:
            log("segment fault, address = 0x%x" % address, should_exit=True)

        data = self.memory[address:address+4]
        self.register[tr] = int.from_bytes(data, 'little', signed=True)
        log("load from memory[r%d = 0x%x] = 0x%x (%d) -> r%d" % (sr, address, self.register[tr], self.register[tr], tr))
        self.pc_next()

    def _movi(self, ins: list):
        tr = ins[1]
        immediate_number = int.from_bytes(ins[2:4], 'little', signed=True)
        self.register[tr] = immediate_number
        log("mov imme = %d to r%d" % (immediate_number, tr))
        self.pc_next()

    def _store(self, ins: list):
        tr, sr = ins[1], ins[2]
        address = self.register[tr]
        data = self.register[sr].to_bytes(4, 'little', signed=True)
        self.memory[address:address+4] = data
        log("store from r%d = 0x%x (%d) to memory[r%d = 0x%x]" % (sr, self.register[sr], self.register[sr], tr, address))
        self.pc_next()

    def _inc(self, ins: list):
        tr = ins[1]
        self.register[tr] += 1
        log("r%d += 1 = %d" % (tr, self.register[tr]))
        self.pc_next()

    def _comi(self, ins: list):
        tr = ins[1]
        immediate_number = int.from_bytes(ins[2:4], 'little', signed=True)
        # if equal set 0, not equal set 1
        self.state = 0x0 if self.register[tr] == immediate_number else 0x1
        log("compare r%d = %d with %d, now r15 = 0x%x" % (tr, self.register[tr], immediate_number, self.state))
        self.pc_next()

    def _jnz(self, ins: list):
        immediate_number = int.from_bytes(ins[2:4], 'little', signed=True)
        # if equal next, else jump
        offset = 4 if not (self.state & 0x1) else immediate_number
        self.pc += offset

    def _halt(self, ins: list):
        log('cpu halt')
        sys.exit(0)

    def _add(self, ins: list):
        tr = ins[1]
        immediate_number = int.from_bytes(ins[2:4], 'little', signed=True)
        self.register[tr] += immediate_number
        log("r%d += %d = %d" % (tr, immediate_number, self.register[tr]))
        self.pc_next()


if __name__ == '__main__':
    cpu = Cpu()
    if len(sys.argv) != 2:
        log("usage: %s <input.s>" % (sys.argv[0]), should_exit=True)
    file_path = sys.argv[1]
    cpu.load_file(file_path)
    cpu.exec()
