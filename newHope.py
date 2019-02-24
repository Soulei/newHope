import poly
import os
import params
import hashlib

#global variables:
a_key = []
b_key = []
s_hat = []

# parse is gen(a) parse returns a list of random coefficients.
def parse(seed):
    hashing_algorithm = hashlib.shake_128()
    hashing_algorithm.update(seed)
    # 2200 bytes from SHAKE-128 function is enough data to get 1024 coefficients
    # smaller than 5q, from Alkim, Ducas, Pöppelmann, Schwabe section 7:
    shake_output = hashing_algorithm.digest(2200)
    output = []
    j = 0
    for i in range(0,params.N):
        coefficient = 5 * params.Q
        # Reject coefficients that are greater than or equal to 5q:
        while coefficient >= 5 * params.Q:
            coefficient = int.from_bytes(
                shake_output[j * 2 : j * 2 + 2], byteorder = 'little')
            print('j=' + str(j))
            j += 1
            if j * 2 >= len(shake_output):
                print('Error: Not enough data from SHAKE-128')
                exit(1)
        output.append(coefficient)
        print('chose ' + str(coefficient))
    return output

#noise distribution
def get_noise():
    coeffs = []
    for i in range(0, params.N):
        t = int.from_bytes(os.urandom(4), byteorder='little')
        d = 0
        for j in range(0, 8):
            d += (t >> j) & 0x01010101
        a = ((d >> 8) & 0xff) + (d & 0xff)
        b = (d >> 24) + ((d >> 16) & 0xff)
        coeffs.append(a + params.Q - b)
    return coeffs


# keygen is a server-side function that generates the private key s_hat and
# returns a message in the form of a tuple. This message should be encoded using
# JSON or another portable format and transmitted (over an open channel) to the
# client.

#Step for sending (b, seed)
#Alice sends the public key b and the seed
def send_b_seed(verbose = False):
    global s_hat
    #generating the seed with 256 bits
    seed = os.urandom(params.NEWHOPE_SEEDBYTES)

    #parse the seed to obtain a
    a_coeffs = parse(seed)

    #getting s and e with phi 16
    s_coeffs = get_noise()
    s_hat = s_coeffs
    e_coeffs = get_noise()

    #computing b<- a.s + e
    r_coeffs = poly.pointwise(s_coeffs, a_coeffs)
    b_coeffs = poly.add(e_coeffs, r_coeffs)

    #b and seed are sent to Bob
    return (b_coeffs, seed)

# sharedb is a client-side function that takes the (decoded) message received
# from the server as an argument. It generates the shared key b_key and returns
# a message in the form of a tuple. This message should be encoded using JSON or
# another portable format and transmitted (over an open channel) to the server.

#Step at the side of Bob sending u
#Computing the second public key u
def send_u(received):
    global b_key
    #getting s', e' and e'' with phi 16
    sprime_coeffs = get_noise()
    eprime_coeffs = get_noise()
    escndprime_coeffs = get_noise()

    #parse the seed to obtain a
    (pkb, seed) = received
    a_coeffs = parse(seed)

    #computing u<-as'+e'
    b_coeffs = poly.pointwise(a_coeffs, sprime_coeffs)
    u_coeffs = poly.add(b_coeffs, eprime_coeffs)

    #computing v<-bs'+e''
    v_coeffs = poly.pointwise(pkb, sprime_coeffs)
    v_coeffs = poly.add(v_coeffs, escndprime_coeffs)
    b_key = v_coeffs
    return u_coeffs

# shareda is a server-side function that takes the (decoded) message received
# from the client as an argument. It generates the shared key a_key.
def compute_vprime(received):
    global a_key, s_hat
    u_coeffs = received
    vprime_coeffs = poly.pointwise(s_hat, u_coeffs)
    a_key = vprime_coeffs
    return
