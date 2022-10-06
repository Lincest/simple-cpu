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
        self.compiler('./resource/test_load.s', std_out=False)
        ans = self.check_output()
        self.assertEqual(ans[0], b'\x01\x01\x02\x00')
