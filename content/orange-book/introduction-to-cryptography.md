---
title: "Introduction to Cryptography"
date: 2026-03-25
draft: false
description: "A practical guide to securing information in the digital age — from ancient ciphers to AES, RSA, Diffie-Hellman, hashing, and PKI."
tags: ["cryptography", "security", "fundamentals", "AES", "RSA", "PKI", "TLS"]
---

A practical guide to securing information in the digital age — from ancient ciphers and brute-force attacks to AES, RSA, Diffie-Hellman, cryptographic hashing, and Public Key Infrastructure.

*[🔬 Interactive Infographic →](../cryptography-infographic/)*

---

## What Is Cryptography?

Suppose you want to send a message that no one can understand except the intended recipient. How would you do that? This is the core problem cryptography has been solving for thousands of years — and in the digital age, it underpins virtually every secure communication we rely on, from online banking to private messaging.

Cryptography is the science of securing information by transforming it into an unreadable form for anyone who does not possess the correct key. The field spans a rich history — from ancient ciphers scratched in stone to the advanced mathematical algorithms protecting today's internet traffic. This post introduces the foundational concepts you need to understand how modern cryptography works.

Before diving into specific algorithms, it helps to define some core terms:

- **Plaintext** — The original, readable message before encryption.
- **Ciphertext** — The scrambled, encrypted form of the message.
- **Cryptographic Algorithm (Cipher)** — The set of rules that defines how encryption and decryption are performed.
- **Key** — A secret value used by the algorithm to convert plaintext to ciphertext and back.

---

## From Ancient Ciphers to Modern Algorithms

### The Caesar Cipher

One of the simplest and oldest encryption methods is the Caesar cipher, used by Julius Caesar more than 2,000 years ago. It works by shifting each letter of the alphabet a fixed number of positions. With a shift of 3, the letter A becomes D, B becomes E, and so on. To encrypt "TRY HACK ME" with a shift of 3, you get "WUB KDFN PH."

The Caesar cipher uses a keyspace of 25 — meaning there are only 25 possible shift values. Because there are so few possibilities, an attacker can simply try all of them — an approach called **brute force** — to recover the original message without knowing the key. A message encrypted with Caesar cipher can typically be broken in seconds by a modern computer.

### Substitution and Transposition Ciphers

The Caesar cipher is a type of substitution cipher, where each letter is replaced by another. A more complex variant is the mono-alphabetic substitution cipher, where each letter maps to a unique other letter across the full alphabet — creating a keyspace of over 400 septillion possible keys. This sounds extraordinarily secure, but it has a critical weakness: **letter frequency analysis**.

In English text, certain letters appear far more often than others. The letter 'e' appears approximately 13% of the time, 't' around 9.1%, and 'a' around 8.2%. An analyst can exploit this statistical pattern to break the cipher without ever knowing the key — making it fundamentally insecure for protecting sensitive information.

A transposition cipher takes a different approach: instead of replacing letters, it rearranges their order. While more complex to analyze than a simple substitution cipher, transposition ciphers alone are still considered cryptographically weak by modern standards.

### What Makes an Encryption Algorithm Secure?

For a modern encryption algorithm to be considered truly secure, recovering the original plaintext from the ciphertext must be **computationally infeasible**. In mathematical terms, this means the underlying problem should require so much computation time that it is practically unsolvable — even for the world's most powerful computers. If an encrypted message could be broken in one week, the encryption is considered insecure. If it would take a million years, it is considered practically secure.

---

## Symmetric Encryption

A symmetric encryption algorithm uses the same key for both encryption and decryption. The sender encrypts a plaintext message using a shared secret key, and the recipient uses that same key to decrypt the resulting ciphertext. The core requirement is that both parties must securely agree on a key before any encrypted communication can begin.

Symmetric encryption is efficient and fast, making it well-suited for encrypting large amounts of data.

### DES: A Cautionary Tale

The Data Encryption Standard (DES), published by NIST in 1977, was the dominant symmetric encryption algorithm for decades. DES uses a key size of only 56 bits. By 1997, a challenge message encrypted with DES was publicly cracked. By 1998, a DES key was broken in just 56 hours. These events demonstrated that a 56-bit key was no longer sufficient to resist modern brute-force attacks.

### AES: The Modern Standard

NIST published the Advanced Encryption Standard (AES) in 2001 as DES's successor. AES was selected as the winner of a competitive, public evaluation process after five years of review, with the Rijndael cipher family — designed by Belgian cryptographers Joan Daemen and Vincent Rijmen — emerging as the standard. AES supports key sizes of 128, 192, or 256 bits and is still considered secure and widely used today.

AES operates by repeatedly applying four core transformations to blocks of 128 bits:

- **SubBytes** — Each byte is replaced using a fixed substitution table (S-box).
- **ShiftRows** — Rows within the data block are cyclically shifted.
- **MixColumns** — Columns are multiplied by a fixed mathematical matrix.
- **AddRoundKey** — A round key is combined with the current data block using XOR.

The number of transformation rounds depends on the key size. AES is a block cipher — it processes data in fixed 128-bit chunks. Stream ciphers, another category of symmetric algorithms, process data one byte at a time.

> **Note:** AES-256 is widely considered quantum-resistant, while AES-128 and AES-192 may offer reduced security against future quantum computing attacks.

### What Symmetric Encryption Achieves

When implemented correctly with a secure key, symmetric encryption provides three critical security properties:

- **Confidentiality** — An intercepted ciphertext reveals nothing to an eavesdropper without the key.
- **Integrity** — Any modification to the ciphertext will prevent successful decryption or produce unreadable output.
- **Authenticity** — Successful decryption implies the message was created by someone who possessed the shared key.

### The Scalability Problem

Symmetric encryption has a fundamental scalability challenge: the key must be securely exchanged in advance. For two people, only one key is needed. For three people, three keys are required. For 100 users, approximately 4,950 unique keys are needed. Beyond the sheer number of keys, each one must be exchanged over a secure channel — which is often impractical over public networks. This limitation helped motivate the development of asymmetric cryptography.

---

## Asymmetric Encryption

Asymmetric encryption eliminates the need for a pre-shared secret key. Instead, each party generates a **key pair** — a public key, shared openly with anyone, and a private key, kept strictly secret. Critically, it is mathematically infeasible to derive the private key from the public key.

The fundamental property that makes this work: a message encrypted with one key can only be decrypted with the other key in the pair.

- If Alice encrypts a message with Bob's public key, only Bob's private key can decrypt it.
- If Bob encrypts a message with his own private key, anyone with Bob's public key can decrypt it — proving it came from Bob.

### Security Goals Enabled by Asymmetric Encryption

Asymmetric encryption can achieve all four major security goals:

- **Confidentiality** — Encrypt with the recipient's public key; only their private key decrypts it.
- **Integrity** — Any modification to the ciphertext will prevent correct decryption.
- **Authenticity** — A message encrypted (or signed) with a private key proves it came from the private key holder.
- **Non-repudiation** — Since only the sender has access to their private key, they cannot later deny having sent a message.

In practice, asymmetric encryption is slower than symmetric encryption and is not well-suited for encrypting large amounts of data directly. In real-world systems, the two approaches are commonly combined: asymmetric encryption securely exchanges a symmetric session key, and all subsequent communication uses faster symmetric encryption.

### RSA

RSA — named for its inventors Ron Rivest, Adi Shamir, and Leonard Adleman, who publicly described the algorithm in 1977 at MIT — is one of the most widely used asymmetric encryption systems in the world. It is the foundation of secure web traffic, digital signatures, and encrypted email.

RSA's security relies on a mathematical hard problem: it is easy to multiply two large prime numbers together, but extremely difficult to factor the result back into those two primes. This asymmetry between easy multiplication and hard factoring is what makes RSA secure.

The key generation process involves choosing two large prime numbers (p and q), computing their product N, and deriving two related values (e and d) that serve as the public and private exponents respectively. The public key is the pair (N, e) and the private key is (N, d). Encryption raises the plaintext to the power of e modulo N; decryption raises the ciphertext to the power of d modulo N.

In practice, RSA keys are typically 2,048 to 4,096 bits long. NIST considers 2,048-bit RSA keys sufficient through at least 2030. The security of RSA keys depends critically on the use of secure random number generation — if the prime numbers can be guessed or predicted, the entire system is compromised.

> **Historical note:** An equivalent system was independently developed in 1973 at GCHQ by mathematician Clifford Cocks — but that work was classified for over two decades. Rivest, Shamir, and Adleman are credited with the first public description of the algorithm.

---

## Diffie-Hellman Key Exchange

Whitfield Diffie and Martin Hellman published their landmark paper "New Directions in Cryptography" in 1976, introducing the concept of public-key cryptography and what became known as the Diffie-Hellman key exchange. They received the ACM Turing Award — often called the "Nobel Prize of Computing" — in 2015 for work recognized as having "laid the foundation for modern cryptography."

The Diffie-Hellman key exchange solves a seemingly impossible problem: how can two parties agree on a shared secret over a public, insecure channel — in full view of eavesdroppers — without ever transmitting that secret?

The protocol works using modular arithmetic. Both parties agree publicly on two values: a prime number q and a generator g. Each party then privately selects a secret random number and calculates a corresponding public value to share. Using each other's public values and their own private numbers, both parties independently compute the same shared secret. An eavesdropper who observes the public values cannot feasibly compute the shared secret without solving the **discrete logarithm problem** — which, for sufficiently large numbers, is computationally intractable.

A simple numeric example illustrates the concept:

- Alice and Bob publicly agree on q = 29 and g = 3.
- Alice secretly picks a = 13 and sends A = 3¹³ mod 29 = 19 to Bob.
- Bob secretly picks b = 15 and sends B = 3¹⁵ mod 29 = 26 to Alice.
- Alice computes: 26¹³ mod 29 = 10. Bob computes: 19¹⁵ mod 29 = 10. Both arrive at the same shared secret: 10.

In real deployments, q is typically 256 bits or larger — an astronomically large number that makes it infeasible for any attacker to determine the private values.

### The Man-in-the-Middle Vulnerability

Diffie-Hellman in its basic form does not authenticate the parties involved. This makes it vulnerable to a **Man-in-the-Middle (MitM) attack**: an attacker could intercept the exchanged public values and substitute their own, conducting separate key agreements with both Alice and Bob while each believes they are talking directly to the other. This is why Diffie-Hellman is typically used in combination with authenticated mechanisms — such as digital signatures and PKI certificates — to verify the identity of both parties.

> Today, Diffie-Hellman (and its elliptic curve variants) is found in virtually every HTTPS connection, SSH session, and IPsec tunnel on the internet.

---

## Cryptographic Hashing

A cryptographic hash function takes an input of any size and produces a fixed-size output called a **message digest** or checksum. No matter whether the input is a four-byte text file or a five-gigabyte video, the output length remains constant. The SHA-256 algorithm, for example, always produces a 256-bit (64 hexadecimal character) digest.

Hash functions have two critical properties that make them valuable for security:

- **One-way** — Given a hash output, it is computationally infeasible to reconstruct the original input.
- **Avalanche effect** — Even a single-bit change to the input produces a completely different output hash.

### Password Storage

Storing passwords in plaintext is a critical security failure. If a database is compromised, every password is immediately exposed. A more secure approach stores the hash of each password — so even with database access, an attacker cannot directly recover any password.

However, a naive hash-only approach is still vulnerable to **rainbow table attacks**: precomputed lookup tables that map common passwords to their hashes. The defense is **salting** — adding a unique random value to each password before hashing. This ensures that even two users with identical passwords will produce different stored hashes, defeating rainbow table attacks.

For high-security password storage, modern systems use dedicated key derivation functions such as PBKDF2, which applies thousands of hash iterations to further slow down brute-force attempts.

File integrity verification is another major use. Any modification to a file — even changing a single bit — produces a dramatically different hash value, making it straightforward to detect tampering or accidental corruption during file transfer.

### HMAC

Hash-based Message Authentication Code (HMAC) combines a hash function with a secret key to produce a message authentication code. Unlike a plain hash, an HMAC cannot be forged without knowing the key, providing both integrity verification and authenticity confirmation. HMAC is defined in RFC 2104 and is widely used in API authentication and secure protocols.

### Algorithm Status

Currently considered secure hash algorithms include SHA-224, SHA-256, SHA-384, SHA-512, and RIPEMD-160. Older algorithms, including MD5 and SHA-1, are considered cryptographically broken — it is possible to construct two different inputs that produce the same hash (a collision), making them unsuitable for security-critical applications.

---

## Public Key Infrastructure (PKI)

Public Key Infrastructure (PKI) is a comprehensive framework of policies, roles, hardware, software, and procedures used to create, manage, distribute, use, store, and revoke digital certificates. Its purpose is to establish trust in public key cryptography at scale — solving the fundamental question: how do you know that the public key you received actually belongs to the person or organization you think it does?

PKI addresses the Man-in-the-Middle vulnerability of Diffie-Hellman by introducing a trusted third party: the **Certificate Authority (CA)**. A CA is an organization that verifies the identity of entities requesting certificates and digitally signs those certificates with its own private key. When your browser connects to a website over HTTPS, it uses PKI to confirm that the server's public key genuinely belongs to the domain you intended to visit.

### How PKI Works

The process of obtaining a PKI certificate involves two main steps:

- **Certificate Signing Request (CSR)** — The entity generates a key pair, creates a certificate request containing its public key and identifying information, and submits it to a CA.
- **CA Signing** — The CA verifies the identity of the requester, signs the certificate with its own private key, and issues the signed certificate. The signature allows anyone with the CA's public key to verify the certificate's authenticity.

For this system to work, the recipient (such as a web browser) must already trust the CA that signed the certificate. Operating systems and browsers ship with a pre-installed list of trusted root CAs. A certificate signed by a trusted CA inherits that trust.

### SSL/TLS and HTTPS

PKI is the backbone of HTTPS and the TLS protocol that secures the modern web. When you connect to a website, the process follows these steps:

1. Your browser requests the server's TLS certificate.
2. The server sends its certificate, which contains its public key and is signed by a CA.
3. Your browser verifies the certificate's signature using the CA's public key (already trusted via the pre-installed root store).
4. If valid, a TLS handshake occurs: the client and server agree on a shared symmetric session key and cipher suite.
5. All subsequent communication in the session is encrypted using that symmetric key.

This process combines asymmetric encryption (for authentication and key exchange) with symmetric encryption (for efficient bulk data encryption) — taking the best of both worlds.

---

## Putting It All Together

Modern cryptographic systems rarely rely on a single technique in isolation. A typical secure connection on the internet brings together multiple cryptographic primitives working in concert:

- **Asymmetric encryption** (RSA or elliptic curve) authenticates identities and securely establishes a shared session key.
- **Symmetric encryption** (AES) uses that session key to encrypt the bulk of communication efficiently.
- **Cryptographic hashing** verifies message integrity and underlies digital signatures.
- **HMAC** provides authenticated integrity checks on transmitted data.
- **PKI certificates** validate that public keys belong to verified identities, defeating man-in-the-middle attacks.

Together, these components deliver the four pillars of cryptographic security: **confidentiality, integrity, authenticity, and non-repudiation**. Understanding how they interrelate is foundational for anyone working in cybersecurity, software development, or IT infrastructure.

---

## References and Sources

**Primary Standards and Specifications**

1. National Institute of Standards and Technology (NIST). Federal Information Processing Standards Publication 197: Advanced Encryption Standard (AES). November 26, 2001 (updated May 9, 2023). https://csrc.nist.gov/pubs/fips/197/final
2. Kaliski, B. IETF RFC 2104: HMAC: Keyed-Hashing for Message Authentication. February 1997. https://www.rfc-editor.org/rfc/rfc2104
3. Rescorla, E. IETF RFC 2631: Diffie-Hellman Key Agreement Method. June 1999.

**Foundational Research Papers**

4. Diffie, W. and Hellman, M.E. "New Directions in Cryptography." IEEE Transactions on Information Theory, vol. IT-22, no. 6, November 1976, pp. 644–654.
5. Rivest, R.L., Shamir, A., and Adleman, L. "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems." Communications of the ACM, vol. 21, no. 2, February 1978, pp. 120–126. https://people.csail.mit.edu/rivest/Rsapaper.pdf

**Encyclopedic and Technical References**

6. Wikipedia contributors. "Advanced Encryption Standard." https://en.wikipedia.org/wiki/Advanced_Encryption_Standard
7. Wikipedia contributors. "RSA cryptosystem." https://en.wikipedia.org/wiki/RSA_cryptosystem
8. Wikipedia contributors. "Diffie–Hellman key exchange." https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
9. Wikipedia contributors. "Public key infrastructure." https://en.wikipedia.org/wiki/Public_key_infrastructure

**Institutional and Industry Sources**

10. National Inventors Hall of Fame. "Adi Shamir." https://www.invent.org/inductees/adi-shamir
11. National Inventors Hall of Fame. "Leonard Adleman." https://www.invent.org/inductees/leonard-adleman
12. DigiCert. "What is PKI?" https://www.digicert.com/what-is-pki
13. IBM. "What is Public Key Infrastructure (PKI)?" https://www.ibm.com/think/topics/public-key-infrastructure
14. Okta. "What Is Public Key Infrastructure (PKI) & How Does It Work?" https://www.okta.com/identity-101/public-key-infrastructure/
15. TechTarget. "RSA algorithm." https://www.techtarget.com/searchsecurity/definition/RSA
16. TechTarget. "What is Diffie-Hellman Key Exchange?" https://www.techtarget.com/searchsecurity/definition/Diffie-Hellman-key-exchange
17. Comparitech. "What is the Diffie–Hellman key exchange and how does it work?" https://www.comparitech.com/blog/information-security/diffie-hellman-key-exchange/
18. Splunk. "RSA Algorithm in Cryptography: Rivest Shamir Adleman Explained." https://www.splunk.com/en_us/blog/learn/rsa-algorithm-cryptography.html
19. OWASP. "Password Storage Cheat Sheet." https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
20. TryHackMe. "Introduction to Cryptography" room. https://tryhackme.com

---

*This post is intended for educational purposes. Cryptography is a rapidly evolving field — always consult current standards and expert guidance before implementing cryptographic systems in production environments.*
