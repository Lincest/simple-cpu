# simple-cpu

> a simple cpu simulator wirtten in python

the `assembler` is to compile asm code into bytecode

the `cpu` is a simple simulator of cpu to run bytecode

to see the instructions, goto `./assembler/readme.md`

## how to run/test

> see `./Makefile`

- on linux: run `make test` (with python3 installed) 
- on windows:
  - run ` python ./assembler/assembler.py ./tests/resource/asm_code.s ./tests/resource/asm_code.o`
  - then run `python ./cpu/cpu.py ./tests/resource/asm_code.o`

### example code and result

code: 

```shell
movi r1, 0
movi r3, 4096
movil r2, data_addr

label loop
# load memory[r2] to r4
load r4, r2
# store r4's value to memory[r3]
store r3, r4
# load memory[r3] to r5
load r5, r3
# r2 += 4
add r2, 4
# compare r4's value with number 20
cmpi r5, 20 
# jump if not equal
jnzl loop
# program ends
halt

label data_addr
data 20 30 40
data 0x1234 0xfeff
data 0x123456ff
```

result: 

```shell
memory size = 16384
mov imme = 0 to r1
mov imme = 4096 to r3
mov imme = 40 to r2
load from memory[r2 = 0x28] = 0x14 (20) -> r4
store from r4 = 0x14 (20) to memory[r3 = 0x1000]
load from memory[r3 = 0x1000] = 0x14 (20) -> r5
r2 += 4 = 44
compare r5 = 20 with 20, now r15 = 0x0
load from memory[r2 = 0x2c] = 0x1e (30) -> r4
store from r4 = 0x1e (30) to memory[r3 = 0x1000]
load from memory[r3 = 0x1000] = 0x1e (30) -> r5
r2 += 4 = 48
compare r5 = 30 with 20, now r15 = 0x1
cpu halt
```

## ref

[pipeline_simulator](https://github.com/nekin2017/pipeline_simulator)
