import numpy as np
from functools import wraps
from stochastic.processes import continuous
from collections.abc import Iterable


def check_len(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        x = args[0]
        assert hasattr(x, '__getitem__'), "input should be indexable"
        assert len(x) >= 2, "input should be longer than 2"
        return fn(*args, **kwargs)
        
    return wrapper

def check_binary(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        x = args[0]
        if isinstance(x, Iterable):
            assert all((item == 0 or item == 1) for item in x), "all x values should be binaries"
        else:
            assert x == 0 or x == 1, "all x values should be binaries"
            
        return fn(*args, **kwargs)
    return wrapper

def rsigmoid(x):
    return 1.0 / (1.0 + np.exp(-5*(2*x-1)))

def rise(scale, T):
    ts = np.arange(T)
    xs = ts / (T-1)
    y = scale * rsigmoid(xs)
    return y

@check_len
@check_binary
def bin2cont(x, scale, effect_len):
    diff = x[-1] - x[0] # -1, 0, 1
    return diff * rise(scale, effect_len)

@check_binary
def bin2cat(x, target_value):
    return x * target_value

@check_len
def cat2cont(x, scale, effect_len):
    end_state = x[-1]
    scl = scale[end_state]
    
    return bin2cont(x, scl, effect_len)

def cat2bin(x, test_elems):
    return np.isin(x, test_elems)

@check_len
def mean_grad(x, scale):
    grad = np.mean(np.gradient(x))
    return scale * grad

def bound_it(x, up, low, scale=1):
    return scale * ((x>low) and (x<up))

def group_it(x, spectrum, scale=1):
    bins = np.digitize(x, spectrum)
    return scale * bins

def to_camel_case(s):
    s = s.replace("-", " ")  # replace "-" with space
    words = s.split()  # split string into words
    words = [word.capitalize() for word in words]  # capitalize each word
    return "".join(words)  # join words without space

def identity(x):
    return x





def step2sawtooth(x, height):
    dx = np.where(np.diff(x)==1.0)[0] + 1
    incremental_seq = np.hstack([
        np.arange(1, b-a+1) for a, b in 
        zip([0] + dx.tolist(), dx.tolist() + [len(x)])
    ])
    y = x.copy()
    y[x == 1] = incremental_seq[x == 1]
    return height*y

def scale(x, scl):
    return scl*x

def constant_signal(ts, height):
    return np.ones_like(ts)*height

def bessel_process(ts):
    return continuous.BesselProcess().sample_at(ts)

def mfbm(ts):
    return continuous.MultifractionalBrownianMotion(t=max(ts)).sample(len(ts)-1)


def uniform_discrete(ts, values, trans_freq=0.008, start_val=None, end_val=None, rng=None):
    if rng is None:
        rng = np.random.default_rng()
    
    n_trans = max(round(len(ts)*trans_freq), 1)
    
    trans_pt = np.sort(rng.choice(ts, size=n_trans, replace=False))
    
    trans_v = rng.choice(values, size=n_trans-1)
    
    if start_val is None:
        start_val = rng.choice(values, 1)
    
    if end_val is None:
        end_val = rng.choice(values, 1)
        
    trans_v = np.concatenate([start_val, trans_v, end_val])
    
    result = np.zeros_like(ts)
    for i in range(n_trans):
        start_idx = 0 if i == 0 else trans_pt[i-1]
        result[start_idx:trans_pt[i]] = trans_v[i]
        
    return result


def node_agg_compatible(node_type, agg_type):
    if node_type == 'continuous':
        to_check = [agg_type] if isinstance(agg_type,str) else agg_type.keys()
        return all(typ in {'average', 'sum', 'weighted'} for typ in to_check) 
    elif node_type in {'categorical', 'binary'}:
        return agg_type == 'vote'
    else:
        return True
    
    
def validate_mixture_eff(all_effs):
    if 'value' in all_effs:
        return len(all_effs.keys()) == 1
    return True