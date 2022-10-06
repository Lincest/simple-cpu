## assembler

> compile assembly code to bytecode.

`python assembler.py input.s > output.o`

## registers

- `size`: 32bit
- `endian`: little endian

| register   | description                                        |
| ---------- | -------------------------------------------------- |
| `r0`       | const: `0x00`                                      |
| `r1`-`r12` | common register                                    |
| `r13`      | `pc`                                               |
| `r14`      | `lr`                                               |
| `r15`      | `st`: cpu state  -> `0x00`: equal `0x1`: not equal |

## instructions

| instruction | description                                                  |
| ----------- | ------------------------------------------------------------ |
| `nop`       | no operation                                                 |
| `load`      | `load r1 r2` load data with address of r2 to r1              |
| `movi`      | `movi r1 1234`                                               |
| `store`     | `store r1 r2` store r2' s data to address of r1              |
| `inc`       | `inc r1` r1's data += 1                                      |
| `cmpi`      | `cmpi r1 1234` compare r1's data with 1234                   |
| `jnz`       | `jnz 0x12` jump to offset 0x12 (addr: current_addr + offset 0x12) if not zero |
| `halt`      | pause the cpu                                                |

### encoding of instruction

each instruction consists of 4 bytes

- `byte[0]`: opcode
- `byte[1]`: target register
- `byte[2], byte[3]`: source register
- `byte[2] and byte[3]`: immediate number

## pseudos

| pseudo  | description                                 |
| ------- | ------------------------------------------- |
| `label` | `label <name>` label definition             |
| `jnzl`  | `jnzl <name>` jump to label                 |
| `movil` | `movil r1 <label>`  save label's addr to r1 |
| `data`  | `data <number>` immediate numbers space     |