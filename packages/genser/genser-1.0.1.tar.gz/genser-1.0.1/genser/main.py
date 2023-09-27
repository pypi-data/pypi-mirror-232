#!/usr/bin/env python
# coding: utf-8

def dim_step_down(data: list, powers: list):
    """
    Decreases the dimension by 1
    
    Arguments:
    data (list of lists): the input dataset without labels
    powers (list): the powers of the features ordered as in data vector
    
    Outputs:
    A dataset of decreased dimension, 
    A new list of powers,
    A dictionary of the transformation in the form of 
        {k1: Pk1, k2: Pk2}, where k1<k2 are the indexes of the unified features 
        and Pk1, Pk2 are their corresponding powers. 
    """
    Pk = min(powers)
    k = powers.index(Pk)
    Pm = min(powers[:k]+powers[k+1:])
    if Pm in powers[:k]:
        Pk1, k1 = Pm, powers[:k].index(Pm)
        Pk2, k2 = Pk, k
    else:
        Pk1, k1 = Pk, k
        Pk2, k2 = Pm, k + 1 + powers[k+1:].index(Pm)
    return list(map(lambda x: x[:k1] + [Pk2*x[k1] + x[k2]] + 
                    x[k1+1:k2] + x[k2+1:], data)), powers[:k1]+[Pk1*Pk2]+powers[k1+1:k2]+powers[k2+1:], {k1: Pk1, k2: Pk2}

def dim_step_up(data: list, powers: list):
    """
    Increases the dimension by 1
    
    Arguments:
    data (list of lists): the input dataset without labels
    powers (list): the powers of the features ordered as in data vector
    
    Outputs:
    A dataset of increased dimension, 
    A new list of powers,
    A dictionary of the transformation in the form of 
        {k: Pk, n: Pn}, where k is the index of the maximal power value 
        and n = len(powers). 
    """
    P = max(powers)
    k = powers.index(P)
    Pk = int(P**(1/2))
    Pn = P/Pk
    if int(Pn) != Pn:
        Pn = int(Pn) + 1
    else:
        Pn = int(Pn)
    return list(map(lambda x: x[:k] + [x[k]//Pn] + x[k+1:] + [x[k]%Pn], data)), powers[:k]+[Pk]+powers[k+1:]+[Pn], {k: Pk, len(powers): Pn}


def dim_backstep_up(data: list, powers: list, tdict: dict):
    """
    Increases the dimension by 1 in the case when 
    the dimension had been decreased by dim_step_down
    
    Arguments:
    data (list of lists): the input dataset without labels
    tdict (dict): the output dict from the dim_step_down function
    
    Outputs:
    A dataset of restored dimension, 
    A restored list of powers. 
    """
    k1, k2 = tuple(tdict.keys())
    Pk1, Pk2 = tuple(tdict.values())
    return list(map(lambda x: x[:k1] + [x[k1]//Pk2] + x[k1+1:k2] 
                    + [x[k1]%Pk2] + x[k2:], data)), powers[:k1]+[Pk1]+powers[k1+1:k2]+[Pk2]+powers[k2:]


def dim_backstep_down(data: list, powers: list, tdict: dict):
    """
    Decreases the dimension by 1 in the case when 
    the dimension had been increased by dim_step_up
    
    Arguments:
    data (list of lists): the input dataset without labels
    tdict (dict): the output dict from the dim_step_up function
    
    Outputs:
    A dataset of restored dimension, 
    A restored list of powers. 
    """
    k, n = tuple(tdict.keys())
    Pk, Pn = tuple(tdict.values())
    return list(map(lambda x: x[:k] + [x[k]*Pn+x[n]] + x[k+1:-1], data)), powers[:k]+[Pk*Pn]+powers[k+1:-1]


def transform_to(data: list, d: int):
    """
    Transforms the dimension of the given dataset to the d value
    
    Arguments:
    data (list of lists): the input dataset without labels
    d (int): the target dimension
    
    Outputs:
    A dataset of dimension d, 
    A list of transformation hints: a tuple (powers, tdict) for every step. 
    """
    columns = [[d[i] for d in data] for i,_ in enumerate(data[0])]
    powers = list(map(lambda x: max(x)+1, columns))
    n = len(powers)
    if n > d:
        rlist = []
        for _ in range(d,n):
            data, powers, tdict = dim_step_down(data,powers)
            rlist.append((powers,tdict))
    elif n < d:
        rlist = []
        for _ in range(n,d):
            data, powers, tdict = dim_step_up(data,powers)
            rlist.append((powers,tdict))
    return data, rlist


def transform_out_up(data: list, rlist: list):
    """
    Transforms back the dimension of the given dataset 
    when the dimension had been decreased by transform_to 
    
    Arguments:
    data (list of lists): the input dataset without labels
    rlist (list): the list resulted from transform_to
    
    Outputs:
    A restored dataset, 
    A powers of the restored dataset (may differ from the 
        initial powers of transform_to argument data). 
    """
    rlist.reverse()
    for r in rlist:
        powers, tdict = r[0], r[1]
        data, p = dim_backstep_up(data, powers, tdict)
    return data, p


def transform_out_down(data: list, rlist: list):
    """
    Transforms back the dimension of the given dataset 
    when the dimension had been increased by transform_to 
    
    Arguments:
    data (list of lists): the input dataset without labels
    rlist (list): the list resulted from transform_to
    
    Outputs:
    A restored dataset, 
    A powers of the restored dataset (may differ from the 
        initial powers of transform_to argument data). 
    """
    rlist.reverse()
    for r in rlist:
        powers, tdict = r[0], r[1]
        data, p = dim_backstep_down(data, powers, tdict)
    return data, p