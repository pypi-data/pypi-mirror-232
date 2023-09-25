import pandas as pd
def get_initial_values():
    a = 2
    b = 3
    c = a+b
    print (a+b)
    return b,a,c
def get_d():
    d = 10
    return d
def add_all(d, b, a, c):
    a = a + d
    b = b + d
    c = c + d
    return b,a,c
def print_all(a, b, d, c):
    print (a, b, c, d)
    return a,b,c,d
def analyze():
    x = [1, 2, 3]
    y = [100, 200, 300]
    z = [u+v for u,v in zip(x,y)]
    product = [u*v for u, v in zip(x,y)]
def index_pipeline ():
    b, a, c = get_initial_values ()
    d = get_d ()
    b, a, c = add_all (d, b, a, c)
    a, b, c, d = print_all (a, b, d, c)
    analyze ()
