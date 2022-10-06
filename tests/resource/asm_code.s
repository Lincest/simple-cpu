movi r1, 0
movil r2, data_addr
movil r3, io_addr

label loop
load r4, r2
store r3, r4
inc r2
cmpi r4, 20
jnzl loop

halt

label data_addr
data 20 30 40
data 0x1234 0xfeff
data 0x123456ff

label io_addr
data 4096