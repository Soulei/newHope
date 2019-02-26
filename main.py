import newHope
import params
import sys
import hashlib

if __name__ == "__main__":
    alice_message = newHope.send_b_seed(True)
    bob_message = newHope.send_u(alice_message)
    newHope.compute_vprime(bob_message)

    #Key v' = us -> v'=as's+e's
    print("Alice's key is ")
    print(str(newHope.a_key))
    #Key v = bs' + e'' -> v=as's+es'+e''
    print("Bob's key is ")
    print(str(newHope.b_key))

    #Comparing if the two keys are equal
    count_eq = 0
    for i, c in enumerate(newHope.a_key):
        if newHope.b_key[i] == c:
            count_eq+=1
    print("Key_a and Key_b are equal up to {}% ".format((count_eq*100)/params.N))
