# Message recovery attack to NTRU using a lattice independent from the public key


[![GPLv2](https://img.shields.io/badge/license-GPLv2-lightgrey.svg)](https://opensource.org/licenses/GPL-2.0)
[![CC BY 2](https://img.shields.io/badge/License-CC_BY_2.0-lightgrey.svg)](https://creativecommons.org/licenses/by/2.0/)

An attack to NTRUencrypt was implemented using [sagemath](https://www.sagemath.org/) and [Fpylll](https://github.com/fplll/fpylll)

The code is in [attack.py](./attack.py)

References:

[1] Marios Adamoudis, K. A. Draziotis, Message recovery attack to NTRU using a lattice independent from the public key, http://arxiv.org/abs/2203.09620


## Authors

* K. A. draziotis (drazioti@gmail.com)
* Marios Adamoudis (marios.p7@hotmail.com )

credits: Some functions are from https://latticehacks.cr.yp.to/ntru.html

## License

This project is licensed under the GPLv2 License

The images are provided with [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)

## Getting Started


prerequisites : [sagemath](https://www.sagemath.org/) version >=8.1 and  [Fpylll](https://github.com/fplll/fpylll).

-----

In [generate.md](./generate.md) there is  sagemath code that generates a pair ```(pk,sk)``` for NTRU and a random plaintext and also its encryption (ciphertext).

See [attack.md](./attack.md) for comments on the attack.py

For large values of ```N```, say ```N>400```, ```sagemath``` produces _babai's infinite loop_ for LLL (we used sagemath 8.5).

In [fpylll](https://github.com/fplll/fpylll) LLL succeeded. For instance, for ```N=509```, it took ```5``` minutes for the LLL reduction.

For ```N=509,557``` and ```677``` you can use the already reduced matrices from the directory [reduced_matrices/](./reduced_matrices). To compute the LLL- reduction of matrices in fpylll we use the code in [ntru_large_matrices_reduction.ipynb](./ntru_large_matrices_reduction.ipynb)

In the code (attack.py) there is an option in the function ```the_attack(.)``` to set ```flag=2```, then the code will use the reduced matrix from the file in the directory ```reduced_matrices/``` it and will not compute LLL reduction on it.

In [appendix.ipynb](./appendix.ipynb) there is  Fpylll code that checks suitable values (N,q,y) that satisfy the hypotheses of 
Proposition.
