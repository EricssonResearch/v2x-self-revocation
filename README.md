# Efficient and Timely Revocation of V2X Credentials

This repository contains software artifacts for the paper _Efficient and Timely
Revocation of V2X Credentials_ that will appear at NDSS Symposium 2024.

## Abstract

In Intelligent Transport Systems, secure communication between vehicles,
infrastructure, and other road users is critical to maintain road safety. This
includes the revocation of cryptographic credentials of misbehaving or malicious
vehicles in a timely manner. However, current standards are vague about how
revocation should be handled, and recent surveys suggest severe limitations in
the scalability and effectiveness of existing revocation schemes. In this paper,
we present a formally verified mechanism for self-revocation of
Vehicle-to-Everything (V2X) pseudonymous credentials, which relies on a trusted
processing element in vehicles but does not require a trusted time source. Our
scheme is compatible with ongoing standardization efforts and, leveraging the
Tamarin prover, is the first to guarantee the actual revocation of credentials
with a predictable upper bound on revocation time and in the presence of
realistic attackers. We test our revocation mechanism in a virtual 5G-Edge
deployment scenario where a large number of vehicles communicate with each
other, simulating real-world conditions such as network malfunctions and delays.
Results show that our scheme upholds formal guarantees in practice, while
exhibiting low network overhead and good scalability.

## Structure

The repository is structured into three parts:

- `prl`
   contains scripts to generate and plot the markov matrices 
   (Sec. VII-B / Appendix D)
- `proofs`
   contains the Tamarin models used to formally verify our revocation scheme 
   (Sec. VI / Appendix B)
- `simulation`
   Containing the code used for our evaluation 
   (Sec. VII-A / Appendix C)

A README is also included on each individual folder containing instructions to
run our artifacts.