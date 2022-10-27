# Tamarin models

Two folders:
- `sol1` is the model for the protocol that uses trusted time (Sect. 4.1)
- `sol2` is the model for the protocol that uses epochs (Sect. 4.2)

The models are defined in the files called `theory.spthy`. 

We successfully verified all the lemmas in the models using Tamarin version
`1.7.1`. Outputs from previous execution are found in `output.txt` and
`output.spthy`.

The oracles `oracle.py` help Tamarin to create efficient proofs and allow it to
terminate. Without it, Tamarin would get stuck in some proofs.

More details can be found in the paper (Sect. 4.3 and Appendix B).