# ntru
An attack to NTRUencrypt was implemented using [sagemath](https://www.sagemath.org/)

See [generate.md](./generate.md) for the sagemath code that generates a pair (pk,sk) for NTRU and an encrypted message.

See [attack.md](./attack.md) for the attack.

For large values of N, say N>400, sagemath produces _babai's infinite loop_ for LLL (we used sagemath 8.5).

In [fpylll](https://github.com/fplll/fpylll) LLL succeeded. For instance, for N=509, it took 5 minutes for the LLL reduction.

For N=509 and 677 you can use the already reduced matrices from the direcory reduced_matrices/

In the code (attack.py) there is an option in the function ```the_attack``` to set ```flag=2```, where then the code will use the reduced matrix from the file and will not compute it.
