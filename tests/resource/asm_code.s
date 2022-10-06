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
