import unittest
from assembler import Compiler


class TestAssembler(unittest.TestCase):
    def setUp(self) -> None:
        self.compiler = Compiler()

    def check_output(self):
        buffer = [i.to_bytes(4, 'little', signed=False) for i in self.compiler.output_buffer]
        print('buffer = ', buffer)
        return buffer

    def test_load(self):
        self.compiler('./resource/test_load.s', './resource/test_load.o')
        ans = self.check_output()
        self.assertEqual(ans[0], b'\x01\x01\x02\x00')

    def test_endian(self):
        im = 1245
        bt = im.to_bytes(4, 'little', signed=True)
        b = int.from_bytes(bt, 'little')
        print('number = %d, b = %d', (im, b))
        self.assertEqual(im, b)
