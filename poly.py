import params
import os

QINV = 12287 # -inverse_mod(p,2^18)
RLOG = 18

# a and b are the coefficients of these polys as lists.
def pointwise(a, b):
    coefficients = []
    for i in range(0, params.N):
        t = montgomery_reduce(3186 * b[i])
        coefficients.append(montgomery_reduce(a[i] * t))
    return coefficients

# a and b are the coefficients of these polys as lists.
def add(a, b):
    coefficients = []
    for i in range(0, params.N):
        coefficients.append(barrett_reduce(a[i] + b[i]))
    return coefficients

def mul_coefficients(coefficients, factors):
    for i in range(0, params.N):
        coefficients[i] = montgomery_reduce(coefficients[i] * factors[i])
    return coefficients

def montgomery_reduce(a):
    u = a * QINV
    u &= (1 << RLOG) - 1
    u *= params.Q
    a += u
    return a >> 18

def barrett_reduce(a):
    u = (a * 5) >> 16
    u *= params.Q
    a -= u
    return a
