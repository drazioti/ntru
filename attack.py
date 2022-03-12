''' 
Requirements : The code is written in Sagemath ver. 8.1
  
 AUTHORS: K. A. Draziotis (drazioti@gmail.com)
          Marios Adamoudis (marios.p7@hotmail.com)
          2021: initial version 
 REFERENCES:  http://www.sagemath.org/ 
 * Please report bugs *


'''

# some auxiliary functions we use in the case we do not reduce our basis in sagemath but in FPyyll
# In this case we use flag=2 in the function the_attack()
# For small values of N, N<400 we do not need them
# You have to hardcode the variable file

file=r'/path/to/reduced_matrixN557q8192y2.5.txt'
def mat2fp(A):
    from fpylll import IntegerMatrix
    L = IntegerMatrix(A.dimensions()[0],A.dimensions()[1])
    for i in range(A.dimensions()[0]):
        for j in range(A.dimensions()[1]):
            L[i,j] = int(A[i,j])
    return L

def stringtorow(L):
    M = []
    i = 0
    j = 0
    item = ' '
    left = 0
    right = 0
    item = L[0]
    while i < len(L) - 1:
        left = i
        right = i
        while item in ['-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            i = i + 1
            item = L[i]
            right = i
        M.append([i, L[left:right]])
        i = i + 1
        item = L[i]
    Q = []
    for i in range(len(M)):
        if M[i][1] != '':
            Q.append(int(M[i][1]))
    return Q
    
def convert_file(file):
    f = open(file, 'r')
    temp = f.read()
    f.close()
    
    f = open(file, 'w')
    f.write("[")
    f.write(temp)
    f.write("]")
    f.close()
    M=[]
    with open(file) as f:
        for line in f:
            M.append(stringtorow(line))
    M=matrix([M[i] for i in range(len(M[0]))])
    M=mat2fp(M)
    return M

# key generation for NTRUencrypt (we refer to NTRU-HPS)

Zx.<x> = ZZ[]
def T(d1,d2,N):
  # generate a list with d+1 ones and d minus ones 
    import random
    Zx.<x> = ZZ[]    
    a = d1*[1]
    b = d2*[-1]
    c = (N-d1-d2)*[0]
    L = flatten([a,b,c])
    random.shuffle(L) 
    return L,Zx(L)

# Generation of private keys : (f,g)
def private_keys(N,d):
    f = T(d+1,d,N)
    g = T(d,d,N)
    return f[1],g[1]
    
# Compute the inverses of f in R_p and R_q

def CenterLift(f,q,N):    
    f_balanced = list(   ((f[i]+q//2)%q) -q//2  for i in range(N))
    return Zx(f_balanced)

def Invertmodprime(f,p,N):        #p must be prime
    T = Zx.change_ring(Integers(p)).quotient(x^N-1)
    return Zx(lift(1/T(f)))
    
def Invertmodpowerofprime(f,q,e,N): # we compute the inverse of f in R_m where m = q ^ e, and q is a prime number
    F = Invertmodprime(f,q,N)
    if e == 1:      
        return F
    n = 2
    while e>0:
        temp = Convolution_in_R(F,f,N);
        F = Convolution_in_R_p(F,2-temp,N,q^n);
        e = floor(e/2)
        n = 2*n
    return F
    
def Convolution_in_R(f,g,N):
    return (f*g)%(x^N-1)

def Convolution_in_R_p(f,g,N,p):
    h = (f*g)%(x^N-1)
    h1 = list(   (h[i]%p)   for i in range(N)   )
    return  Zx(h1)  
        
def gen_keys(N,d,p,q,e): 
  # N,p are primes, usually p=3 
    f,g=private_keys(N,d);
    try:
        Invertmodprime(f,q,N)
    except ZeroDivisionError:
        print("Oops! there is not inverse of f in R_q")
        return
    try:
        Invertmodprime(f,p,N)
    except ZeroDivisionError:
        print("Oops! there is not inverse of f in R_p")
        return
    Fq = Invertmodpowerofprime(f,q,e,N)      
    h = Convolution_in_R_p(Fq,g,N,q^e); # public key
    print("checking if f is inverted modq...",Convolution_in_R_p(f,Fq,N,q^e)==1)
    return f,g,h
  
# step 1-4 of the pseudocode of the attack

def initial_param(N,q,exponent,y):
    import random
    # step 1
    k = (N-1)/2
    
    # step 2
    vector_a = [i for i in range(-k,0)] + [i for i in range(1,k+1)] + [floor(N*m^(1/y)) + 1] 
    random.shuffle(vector_a[:N-1])
    A = Zx(vector_a)
    
    # step 3
    M_NTRU = matrix_for_the_lattice(N,q,exponent,A)
    
    
    # step 4
    B =Convolution_in_R_p(A,e,N,m);
    Blist = B.coefficients(sparse=False);len(Blist)
    
    return A,k,vector_a,M_NTRU,b,Blist
    
def corrections(N,m,p,h,A,r):
    C1 = Convolution_in_R_p(-p*A,r[1],N,m)
    C = Convolution_in_R_p(C1,h,N,m);
    # E must be an approximation of C_vector in order the attack succeedd
    M_vector = M.coefficients(sparse=False)
    C_vector = C.coefficients(sparse=False)
    # we correct the vectors by appending zeros in the case their dimension is <N
    
    print len(M_vector),len(C_vector)
    if len(M_vector)<N:
        diff = N - len(M_vector)
        M_vector.append(diff*[0])
        M_vector=flatten(M_vector)
    if len(C_vector)<N:
        diff = N - len(C_vector)
        C_vector.append(diff*[0])
        C_vector=flatten(C_vector)
        
    print len(M_vector),len(C_vector)
    return C_vector,M_vector
    
# step 5
# Our oracle, which in each call returns an approximation of the vector C

def oracle(N,m,p,h,A,r,Range):
    import random
    Real = M_vector + C_vector # note that M_vector, C_vector are lists, so the sum is the concatenation of the two lists
    u = M_vector + (vector(C_vector) + vector(Blist)).list()
    temp  = vector(C_vector) + vector([randint(-Range,Range) for i in range(N)]);
    E = [0]*N + list(temp);
    #print E
    return E

def target_vector(N,Blist,E):
    if len(Blist)==N:
        t = vector(N*[0] + Blist) + vector(E)
    return t # the target vector t = (0_N,b) + E    

def LLL_reduction_of_M_NTRU(init_M_NTRU):        
    def fptosage(A):
        n = A.nrows
        C = matrix(n)
        for i in range(n):
            C[i] = list(A[i])
        return C
    import time
    from fpylll import IntegerMatrix,LLL
    start = time.time()
    M_NTRU_fplll = IntegerMatrix.from_matrix(init_M_NTRU)
    LLL.reduction(M_NTRU_fplll, delta =0.99 )
    M_NTRU = fptosage(M_NTRU_fplll)
    print("LLL is done")
    print("time for LLL:"),time.time()-start
    return M_NTRU,M_NTRU_fplll 
  
def the_attack(N,m,p,h,A,r,Range,Blist,init_M_NTRU,M_NTRU1,counts,flag):
    
    # flag is 1 or 2
    # N,m,p,h are public parameters
    # init_M_NTRU is the custom NTRU matrix which depends on the vector a = (-k,k+1,...,0,1,2,...)
    # counts, execute the algorithm for 'counts' times. Each time we choose a new vector E
    # Range, is a parameter that constraints the choice of the vector E, |E_i-c_i|<Range.
    
    from fpylll import GSO
    import time
    
    def fptosage(A):
        n = A.nrows
        C = matrix(n)
        for i in range(n):
            C[i] = list(A[i])
        return C
    
    
    def hits(L,M):
        Len = len(L)
        K = []
        for i in range(Len):
            if L[i]!=M[i]:
                K.append(i)
        Len1 = Integer(len(K))
        percentage = ((Len-Len1)/Len) * 100
        print "percentage:",float(percentage)
        print "the lists differs in ",Len1," elements"
        return 

    print("N=",N)
    print("d=",d)
    print("p=",p)
    print("q,e,q^e=",q,exponent,q^exponent)
    print("range : |e_i-c_i|<= ",Range)
    print("y=",y)
    start =  time.time()
    
    # reduction #
    # we use flag=1 in the case we reduce the basis (before we send it to babai) in sagemath
    if flag==1:
        M_NTRU,M_NTRU_fplll = LLL_reduction_of_M_NTRU(init_M_NTRU)
    # we use flag=2 in the case we have aleready reduce our Ntru matrix in Fpylll.
    # This is becouse in sagemath we get error for large values of N
    if flag==2:
        M_NTRU_fplll = M_NTRU1
        M_NTRU = fptosage(M_NTRU_fplll)
    M_GSO = GSO.Mat(M_NTRU_fplll)
    M_GSO.update_gso()
    
    for i in range(counts):
        start1 = time.time()
        print "\n",i
        print "======="
       
        # the oracle #
        E = oracle(N,m,p,h,A,r,Range) 
        
        # the target vector #   
        t = target_vector(N,Blist,E)
        
        # we apply Babai. We use fpylll implementation of Babai.
        L = M_GSO.babai(t)
      
        w = sum(L[i]*M_NTRU[i] for i in range(M_NTRU_fplll.nrows)).list()
        
        print("babai done")
        print("time for babai:",time.time()-start)
        print("success/fail:",list(w[0:N])== M_vector)  
    
        hits(list(w[0:N]),M_vector)
      
        if list(w[0:N])== M_vector: #or list(w_old[0:N])== M_vector:
            print("total time for the loop:",time.time()-start1)
            break
    print("total time for the attack:",time.time()-start)
