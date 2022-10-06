movi r1, 0
movil r2, data_addr
movil r3, io_addr
load r3, r3

label loop
load r4, r2
store r4, r3
inc r2
inc r1
cmpi r1, 10
jnzl loop

nop

label data_addr
data 0x12 0x34 0x56
data 0x12345678

label io_addr
data 4096