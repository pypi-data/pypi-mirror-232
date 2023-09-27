The GenSer package (i.e. Generalised Serialisation) contains the set of functions to perform the dimension transformation of the numerical dataset. To use the package you should have a dataset of non-negative integer values. Having n features in your dataset, you may transform it to m features and, after your work with data, return back to n features. The following functions available:

dim_step_down(data, powers): 
    data is a list of lists; 
    powers is list of powers of the features, i.e. how many different values can the feature take.

dim_step_up(data, powers): 
    the same description as for dim_step_down.

transform_to(data, d): 
    Transforms the dimension of the given dataset to the d value
    
    Arguments:
    data (list of lists): the input dataset without labels
    d (int): the target dimension
    
    Outputs:
    A dataset of dimension d, 
    A list of transformation hints: a tuple (powers, tdict) for every step.

transform_out_down(data, rlist): 
    Transforms back the dimension of the given dataset 
    when the dimension had been increased by transform_to 
    
    Arguments:
    data (list of lists): the input dataset without labels
    rlist (list): the list resulted from transform_to
    
    Outputs:
    A restored dataset, 
    A powers of the restored dataset (may differ from the 
        initial powers of transform_to argument data).

transform_out_up(data, rlist): 
    Transforms back the dimension of the given dataset 
    when the dimension had been decreased by transform_to 
    
    Arguments:
    data (list of lists): the input dataset without labels
    rlist (list): the list resulted from transform_to
    
    Outputs:
    A restored dataset, 
    A powers of the restored dataset (may differ from the 
        initial powers of transform_to argument data). 


Additional information available directly from the author by request on email shoukhov@mail.ru
