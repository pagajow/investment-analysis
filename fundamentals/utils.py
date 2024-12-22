import numpy as np

def get_cagr(values: np.array):
    """ compound annual growth rate (CAGR) """
    cagr = (values[-1] / values[0]) ** (1/(len(values) - 1)) - 1 
    return cagr
def predict_cagr(values: np.array, years:int=4):
    cagr = get_cagr(values)
    #print("cagr", cagr)
    return [values[-1] * ((1 + cagr) ** year) for year in range(1, years + 1)]

def get_geomean(values: np.array):
    ratios = values[1:] / values[:-1] -1
    return np.prod(ratios + 1) ** (1 / len(ratios)) - 1
def predict_geomean(values: np.array, years:int=4):
    geomean = get_geomean(values)
    #print("geomean", geomean)
    return [values[-1] * ((1 + geomean) ** year) for year in range(1, years + 1)]

def get_linearreg(values: np.array):
    n = len(values)
    y = np.array(values)
    x = np.array(range(n))
    sx, sy, sxy, sx2 = sum(x), sum(y), sum(x*y), sum(x**2)
    a = (n*sxy - sx*sy)/(n*sx2 - sx**2)
    b = (sy*sx2 - sx*sxy)/(n*sx2 - sx**2)
    return a,b
def predict_linearreg(values: np.array, years:int=4):
    a,b = get_linearreg(values)
    #print("a,b", a,b)
    return [a*year+b for year in range(len(values), len(values) + years)]