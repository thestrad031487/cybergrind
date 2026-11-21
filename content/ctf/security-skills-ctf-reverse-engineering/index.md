---
title: "Security Skills CTF: reverse engineering"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["ctf", "security-skills", "writeup", "ai-assisted", "reverse-engineering", "elf", "objdump", "xor"]
description: "Reading Python and JavaScript, running strings on an ELF, then statically reversing two stripped x86-64 binaries that hide their data with XOR."
platform: "Security Skills"
difficulty: "Beginner"
category: "Reverse Engineering"
---

Five challenges, 375 points. The first three are about reading. The last two are stripped Linux binaries that hide their data with simple XOR schemes. I solved both statically with `objdump` and a few lines of Python, without running either binary.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## RE01: read the Python (25)

```python
secret_flag = "Professor{read_the_source}"
print("Welcome to Cyber Command")
print("This script stores a secret in a variable")
```

The script never prints the variable, so running it wouldn't help. You have to read the code.

Flag: `Professor{read_the_source}`

## RE02: put the pieces together (50)

```javascript
const parts = ["Professor{", "pieces_fit_", "together}"];
console.log(parts.join(""));
```

Flag: `Professor{pieces_fit_together}`

## RE03: readable strings in a program (75)

A 64-bit Linux ELF, not stripped. String literals survive compilation, so `strings` finds the flag.

```bash
strings -a RE03-hello-linux-amd64 | grep 'Professor{'
```

On Windows without WSL, PowerShell can do the same:

```powershell
Select-String -Path .\RE03-hello-linux-amd64 -Pattern 'Professor\{[^}]*\}' -AllMatches |
  % { $_.Matches.Value }
```

Flag: `Professor{binary_strings_intro}`

## RE04: license checker (100)

A stripped x86-64 ELF that takes a six-character activation code. The field notes say the code isn't stored as a readable string and ask you to work backward from the validation loop rather than patch the binary.

`strings` only shows the usage text and the accept and reject messages. `objdump -d -M intel` on `.text` shows `main` passing `argv[1]` to a check function at `0x1149`. The important part of the loop:

```nasm
mov    eax, edx          ; edx = i
add    eax, eax
add    eax, edx          ; eax = 3*i
add    eax, 0x31         ; eax = 3*i + 0x31
xor    eax, ecx          ; ecx = input[i]
...
lea    rcx, [rip+0xe5d]  ; table at 0x2008
movzx  eax, BYTE PTR [rax+rcx*1]
cmp    edx, eax
```

So each byte has to satisfy `input[i] ^ (3*i + 0x31) == table[i]`. There's a `strlen` check for exactly 6 before the loop.

The table at `.rodata:0x2008` is `7c 00 65 0d 76 72`. XOR undoes itself, so each character is `table[i] ^ (3*i + 0x31)`:

| i | table | key | char |
|---|---|---|---|
| 0 | 0x7c | 0x31 | M |
| 1 | 0x00 | 0x34 | 4 |
| 2 | 0x65 | 0x37 | R |
| 3 | 0x0d | 0x3a | 7 |
| 4 | 0x76 | 0x3d | K |
| 5 | 0x72 | 0x40 | 2 |

```python
t = bytes.fromhex("7c00650d7672")
print("".join(chr(b ^ (3*i + 0x31)) for i, b in enumerate(t)))   # M4R7K2
```

The binary accepts `M4R7K2` (it's case sensitive). The board wants it in lowercase.

Flag: `Professor{m4r7k2}`

## RE05: hidden endpoint (125)

An "update client" simulator that never touches the network. It keeps an endpoint hostname and a unit ID masked in the binary, and `--check <endpoint> <unit-id>` tells you whether you've recovered them. The technician's note says the masking isn't AES and points you at a small unmasking routine.

That routine is at `0x1149`. It takes a destination buffer, a source pointer, a length and a one-byte key:

```nasm
mov    eax, esi          ; esi = i
shl    eax, 0x3
sub    eax, esi          ; eax = 7*i
movzx  eax, BYTE PTR [rbp-0x28]
add    eax, ecx          ; key + 7*i
xor    ecx, eax          ; src[i] ^ (key + 7*i)
```

`main` calls it twice before it even looks at the arguments:

```nasm
mov    ecx, 0x53         ; key
mov    edx, 0x13         ; length 19
lea    rsi, [rip+0xe2e]  ; src 0x2010  -> endpoint
call   1149

mov    ecx, 0x39         ; key
mov    edx, 0x3          ; length 3
lea    rsi, [rip+0xe24]  ; src 0x2023  -> unit ID
call   1149
```

Then `--check` runs `strcmp` on your two arguments against the two decoded buffers. Decoding the same way:

```python
d = open("update_client", "rb").read()
un = lambda a, n, k: "".join(chr(d[a+i] ^ ((k + 7*i) & 0xff)) for i in range(n))
print(un(0x2010, 19, 0x53))   # edge-relay.ops.test
print(un(0x2023, 3, 0x39))    # U42
```

`.rodata` sits at the same offset in the file as in memory in this binary, which is why the virtual addresses work as file offsets. Check `objdump -h` before assuming that.

The first hostname label is `edge-relay`. The hyphen is part of the name, so it stays.

Flag: `Professor{edge-relay_u42}`

## Operator notes

AI help made the biggest difference in this category. Reading Intel syntax out of a stripped binary is slow if you don't do it every day. The AI went through the `objdump` output, found the check routine in RE04 and the unmasking routine in RE05, explained the math in plain terms and wrote the decoders. It never executed either binary, and that's how I'd want any unknown executable handled.

The results are also easy to verify. In a throwaway VM, RE04 should accept `M4R7K2`, and RE05's `--check` should confirm the endpoint and unit ID. The only loose end was board format. The hyphen in `edge-relay` is part of the hostname, but I kept `Professor{edgerelay_u42}` as a backup in case the board wanted it stripped.

## What this section teaches

String hiding only stops `strings`. Once you find the routine that rebuilds the data, a few lines of Python finish the job. In both binaries the "secret" sat in `.rodata` next to a short loop that explained exactly how to read it. Real malware uses fancier versions of this same trick, and the method for beating it is the same: find the decoder, then run it yourself outside the program.
