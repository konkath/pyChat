

def get_secret(p, g, a):
    mod = 1

    i = 0
    while i < a:
        current = g * mod
        mod = current % p
        i += 1
    return mod
