# plug-remote-python

This repository contains a remote runtime library for plug written in python and a few examples.

It communicates with plug through the [plug-remote-runtime](https://github.com/plug-obp/plug-runtime-remote).

Examples:
- [alice_bob_peterson](src/alice_bob_peterson.py),
- [two_counters](src/two_counters.py)

To load these examples in the Plug OBP2 verifier select the **remote** type and load :
- [alice_bob_peterson.remote](alice_bob_peterson.remote) along with the GPSL properties in [alice_bob_peterson.gpsl](alice_bob_peterson.gpsl)
- [two_counters.remote](two_counters.remote)

Old Examples -- using a preliminary implementation of the Pythonic remote runtime:

- [simple counter](src/old/r_counter.py),
- [guard action counter](src/old/ga_counter.py),
- [alicebob](src/old/alicebob.py)




