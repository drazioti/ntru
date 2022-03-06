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
