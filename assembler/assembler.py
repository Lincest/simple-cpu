import sys
import os
from collections import namedtuple
from typing import List

relocate_vec = namedtuple('relocate_vec', ['pc', 'op', 'tr', 'label', 'relative_addr'])
op_coder = namedtuple('coder', ['no', 'func'])
place_holder = 0xffffffff


def log_err(msg, should_exit=False):
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    if should_exit:
        sys.exit(-1)


class Compiler:
    def __init__(self):
        self.pc = 0  # pc pointer
        self.output_buffer = []  # compilation output
        self.labels = {}  # {name: pc}
        self.relocate_table: List[relocate_vec] = []  # relocate table
        self.instruction_set = {  # instructions
            'nop': op_coder(0, self.nop_resolver),
            'load': op_coder(1, self.tr_sr_resolver),
            'movi': op_coder(2, self.tr_im_resolver),
            'store': op_coder(3, self.tr_sr_resolver),
            'inc': op_coder(4, self.tr_nop_resolver),
            'cmpi': op_coder(5, self.tr_im_resolver),
            'jnz': op_coder(6, self.nop_im_resolver),
            # pseudo
            'data': op_coder(-1, self.data_resolver),
            'label': op_coder(-1, self.label_resolver),
            'jnzl': op_coder(-1, self.jnzl_resolver),
            'movil': op_coder(-1, self.movil_resolver)
        }

    def __call__(self, file_path, std_out=True):
        with open(file_path, 'r') as file:
            # parse each line
            for line in file.readlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                log_err("\nline: [%s]" % line)
                code = [i.replace(',', '').strip() for i in line.split()]  # space and ',' are supported
                instruction = code[0]
                ops = code[1:]
                if instruction in self.instruction_set.keys():
                    coder = self.instruction_set[instruction]
                    func = coder.func
                    no = coder.no
                    log_err("resolver(%d, %s)" % (no, ops))
                    func(no, ops)
                else:
                    log_err("invalid instruction: %s" % instruction, should_exit=True)

            # relocate
            for r in self.relocate_table:
                if r.label not in self.labels.keys():
                    log_err("invalid label: %s" % r.label, should_exit=True)
                addr = 4 * (self.labels[r.label] - r.pc if r.relative_addr else self.labels[r.label])
                ins = self.make_instruction(self.instruction_set[r.op].no, r.tr)
                ins[2:4] = addr.to_bytes(2, 'little', signed=True)
                code = int.from_bytes(ins, 'little')
                self.output_buffer[r.pc] = code  # relocate and overwrite
                log_err("relocate pc=%d (label=%s on %d) -> code: [%x]" % (r.pc, r.label, self.labels[r.label], code))

            # written in stdout
            if std_out:
                of = os.fdopen(sys.stdout.fileno(), "wb")
                assert of
                for i in range(0, self.pc):
                    of.write(self.output_buffer[i].to_bytes(4, 'little', signed=False))

                log_err("success!")

    @staticmethod
    def make_instruction(op, tr) -> bytearray:
        instruction = bytearray(4)
        instruction[0], instruction[1] = op, tr
        return instruction

    @staticmethod
    # no is r0, r1, ... r12
    def get_register_no(no: str, is_target=False) -> int:
        min_no = 0
        if is_target:
            min_no = 1  # r[0] can not use as target
        tr = int(no[1:])
        log_err("target register is r[%d]" % tr)
        if tr < min_no or tr > 12:
            log_err("bad register id = %s" % tr, should_exit=True)
        return tr

    @staticmethod
    def get_immediate_number(im: str) -> int:
        immediate_number = int(im, base=0)
        # range of signed 16bit number
        if immediate_number < -32768 or immediate_number > 32767:
            log_err("bad immediate number %s" % im, should_exit=True)
        return immediate_number

    def pc_next(self):
        self.pc += 1
        return self

    # add to compilation result
    def append_output(self, bytecode: int):
        log_err(f'pc = 0x{self.pc:02x} code -> {bytecode}')
        self.output_buffer.append(bytecode)
        self.pc_next()

    # [operation, target_register, source_register_1, source_register_2]
    def make_instruction_4(self, op: int, tr: int, sr1: int, sr2: int):
        ins = self.make_instruction(op, tr)
        ins[2], ins[3] = sr1, sr2
        code = int.from_bytes(ins, 'little')  # little endian
        log_err("(pc=%x) [%d, %d, %d, %d] -> code: [%x]" % (self.pc, op, tr, sr1, sr2, code))
        self.append_output(code)
        return self

    # [operation, target_register, immediate_number(2B)]
    def make_instruction_3(self, op: int, tr: int, im: int):
        ins = self.make_instruction(op, tr)
        immediate_number = im.to_bytes(2, 'little', signed=True)
        ins[2:4] = immediate_number
        code = int.from_bytes(ins, 'little')  # little endian
        log_err("(pc=%x) [%d, %d, %d] -> code: [%x] " % (self.pc, op, tr, im, code))
        self.append_output(code)
        return self

    # relocate with label
    def make_relocate(self, vec: relocate_vec):
        self.relocate_table.append(vec)
        self.append_output(place_holder)
        return self

    # ----------------- resolvers  -----------------
    # ----- ops: [](max = 4, min = 1)  -------------

    # no operation
    def nop_resolver(self, no: int, ops: list):
        self.make_instruction_4(no, 0, 0, 0)

    # e.g. load r1 r2
    def tr_sr_resolver(self, no: int, ops: list):
        tr, sr1 = self.get_register_no(ops[0], is_target=True), self.get_register_no(ops[1])
        self.make_instruction_4(no, tr, sr1, 0)

    # e.g. movi r1 1234
    def tr_im_resolver(self, no: int, ops: list):
        tr = self.get_register_no(ops[0], is_target=True)
        immediate_number = self.get_immediate_number(ops[1])
        self.make_instruction_3(no, tr, immediate_number)

    # e.g. inc r1
    def tr_nop_resolver(self, no: int, ops: list):
        tr = self.get_register_no(ops[0], is_target=True)
        self.make_instruction_4(no, tr, 0, 0)

    # e.g. jnz 1234
    def nop_im_resolver(self, no: int, ops: list):
        immediate_number = self.get_immediate_number(ops[0])
        self.make_instruction_3(no, 0, immediate_number)

    # e.g. data 0x23 0x35 0x1234 1223 -7766 ...
    def data_resolver(self, no: int, ops: list):
        for i in ops:
            self.append_output(int(i, 0))  # fixme: how to/should we keep little endian

    # e.g. label loop
    def label_resolver(self, no: int, ops: list):
        name = ops[0]
        self.labels[name] = self.pc  # current location

    # e.g. jnzl loop
    def jnzl_resolver(self, no: int, ops: list):
        label = ops[0]
        vec = relocate_vec(pc=self.pc, op='jnz', tr=0, label=label, relative_addr=True)
        self.make_relocate(vec)

    # e.g. movil r1 name
    def movil_resolver(self, no: int, ops: list):
        tr = self.get_register_no(ops[0], is_target=True)
        label = ops[1]
        vec = relocate_vec(pc=self.pc, op='movi', tr=tr, label=label, relative_addr=False)
        self.make_relocate(vec)


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     log_err("usage: %s <input.s>" % (sys.argv[0]), should_exit=True)
    # file_path = sys.argv[1]
    file_path = "../tests/resource/asm_code.s"
    compiler = Compiler()
    compiler(file_path)
