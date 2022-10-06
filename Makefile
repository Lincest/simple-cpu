# 1. put .s file into tests/resource
# 2. go to ./cpu/result check the debug info

test: 
	python3 ./assembler/assembler.py ./tests/resource/asm_code.s ./tests/resource/asm_code.o && python3 ./cpu/cpu.py ./tests/resource/asm_code.o 2>&1 | tee ./cpu/result

clean:
	rm ./tests/resource/asm_code.o
	rm ./cpu/result

