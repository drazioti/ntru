# NTRUencrypt
Here we provide the pseudocode for generate keys in NTRUencypt.

![alt text](https://github.com/drazioti/ntru/blob/main/images/2022-03-06_17-24.png)

In sagemath we have,
```
# key generation
# generate a list with d+1 ones and d minus ones 
Zx.<x> = ZZ[]
def T(d1,d2,N):
    import random
    Zx.<x> = ZZ[]    
    a = d1*[1]
    b = d2*[-1]
    c = (N-d1-d2)*[0]
    L = flatten([a,b,c])
    random.shuffle(L) 
    return L,Zx(L)

# step 1, generation of private keys (f,g)
def private_keys(N,d):
    f = T(d+1,d,N)
    g = T(d,d,N)
    return f[1],g[1]
    
# step 3,4: compute the inverses of f in R_p and R_q

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
        
def gen_keys(N,d,p,q,e): # N,p primes, 
    #if d  >= ((q^e-p)/(6*p)).n():
    #    print d  , ((q^e-p)/(6*p)).n()
    #    return "choose a smaller d or larger N or q^e",d,(q^e-p)/(6*p).n()
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
```
For instance see https://tinyurl.com/3czkd32u

For the encryption we use the following pseudo code

![alt text](https://github.com/drazioti/ntru/blob/main/images/2022-03-06_17-39.png)

We provide the code for encryption and decryption,
```
# choose a random message
left = ceil(-p/2)
right = floor(p/2)
M = Zx([randint(left,right) for i in range(N)])
#print("the message M:",M) # the message
r = T(d,d,N) #ephemeral key
#show("the ephemeral key r:",r)

### Encryption
e1 = Convolution_in_R_p(h,p*r[1],N,q^exponent)
e = e1 + M;
print('the encryption e:',e)

### Decryption
m = q^exponent;
a = Convolution_in_R_p(f,e,N,m)
a = CenterLift(a,m,N)
Fp = Invertmodprime(f,p,N)
b=Convolution_in_R_p(Fp,a,N,p)
dec = CenterLift(b,p,N)
#print("decryption",dec)  
print(dec==M)     #we check if we find the message m(x)
```
Now our attack is the following.

![alt text](https://github.com/drazioti/ntru/blob/main/images/2022-03-06_18-17.png)

We use fpylll (https://github.com/fplll/fpylll) in order to apply Babai's nearest plane algorithm. 
So we shall ```import fpylll``` in sagemath. Babai's algorithm is a method of ```GSO``` in fpylll library.

In order to try our attack we need an oracle. ...
