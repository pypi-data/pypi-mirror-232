import pandas as pd
def get_initial_values(test=False):
    a = 2
    b = 3
    c = a+b
    print (a+b)
    return a,b,c
def get_d():
    d = 10
    return d
def print_all(a, c, b, d):
    print (a, b, c, d)
    return a,b
def analyze():
    x = [1, 2, 3]
    y = [100, 200, 300]
    z = [u+v for u,v in zip(x,y)]
    product = [u*v for u, v in zip(x,y)]
def myfunc (x, y, a=1, b=3):
    print ('hello', a, b)
    c = a+b
    return c

def index_pipeline (test=False, load=True, save=True, result_file_name="index_pipeline"):

    # load result
    result_file_name += '.pk'
    path_variables = Path ("index") / result_file_name
    if load and path_variables.exists():
        result = joblib.load (path_variables)
        return result

    a, b, c = get_initial_values (test=test)
    d = get_d ()
    a, b = print_all (a, c, b, d)
    analyze ()
    c = myfunc (x, y, a, b)

    # save result
    result = Bunch (a=a,c=c,b=b,d=d)
    if save:    
        path_variables.parent.mkdir (parents=True, exist_ok=True)
        joblib.dump (result, path_variables)
    return result
