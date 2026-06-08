# Jacó, filho de Isaac, filho de Abraão, teve 12 filhos.
import numpy as np

# A needs to be symetric
def Jacobi_Decomposition(A: np.matrix) -> np.matrix:
    max: np.float64 = A[0][0]
    p: int = 0
    q: int = 0

    for row in np.nditer(A, flags=["external_loop"], order='C'):
        print(row)
        wow = abs(row[0].max())
        if max < wow:
            max = wow
        #end
    return A
#end


Jacobi_Decomposition(np.matrix([[1, 2, 3], [4, 5, 6]]))
