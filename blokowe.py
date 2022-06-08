from file import createFile
from multiprocessing import Pool

def permutate(data, perm):
    res = ''
    for i in perm:
        res += data[i - 1]
    return res


def shiftLeft(data):
    res = data[1:]
    res += data[0]
    return res


def xor(a, b):
    return ''.join([str(int(i) ^ int(j)) for i, j in zip(a, b)])


def getSboxValue(data, sbox):
    row = int(data[0] + data[3], 2)
    col = int(data[1] + data[2], 2)
    res = bin(int(sbox[row][col]))[2:]
    if len(res) == 1:
        res = '0' + res
    return res


def encode(left, right, key):
    EP = [4, 1, 2, 3, 2, 3, 4, 1]
    SBOX1 = '1032 3210 0213 3132'.split()
    SBOX2 = '0123 2013 3010 2103'.split()
    P4 = [2, 4, 3, 1]

    expanded = permutate(right, EP)
    xored = xor(expanded, key)
    l, r = xored[:4], xored[4:]
    sbox = getSboxValue(l, SBOX1) + getSboxValue(r, SBOX2)
    res = xor(permutate(sbox, P4), left)
    return res, right


def solve(inData):
    msg, key = inData[0], inData[1]
    P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    P8 = [6, 3, 7, 4, 8, 5, 10, 9]
    IP = [2, 6, 3, 1, 4, 8, 5, 7]
    REVERSED_IP = [4, 1, 3, 5, 7, 2, 8, 6]

    p = permutate(key, P10)
    left, right = shiftLeft(p[:5]), shiftLeft(p[5:])
    key1 = permutate(left + right, P8)
    key2 = permutate(shiftLeft(shiftLeft(left)) + shiftLeft(shiftLeft(right)), P8)
    initial = permutate(msg, IP)
    l, r = encode(initial[:4], initial[4:], key1)
    l, r = encode(r, l, key2)
    return permutate(l + r, REVERSED_IP)

def ecb(key, msg):
    N = len(msg) // 8
    msgParts = []
    for i in range(N):
        msgParts.append((msg[i * 8:(i + 1) * 8], key))

    with Pool() as p:
        res = p.map(solve, msgParts)
    return ''.join(res)

def cbc(key, msg):
    IV = '10010011'
    N = len(msg) // 8
    totalRes = ''
    prev = IV
    for i in range(1, N):
        data = msg[i * 8:(i + 1) * 8]
        xored = xor(data, prev)
        currRes = solve((xored, key))
        totalRes += currRes
        prev = currRes
    return totalRes

def cfb(key, msg):
    IV = '10010011'
    N = len(msg) // 8
    totalRes = ''
    prev = IV
    for i in range(1, N):
        data = msg[i * 8:(i + 1) * 8]
        currRes = solve((prev, key))
        xored = xor(data, currRes)
        totalRes += xored
        prev = xored
    return totalRes

def ctr(key, msg):
    NONCE = '10010011'
    counter = 0
    N = len(msg) // 8
    totalRes = ''
    for i in range(1, N):
        curr = bin((int(NONCE, 2) + counter) % 256)[2:].zfill(8)
        data = msg[i * 8:(i + 1) * 8]
        currRes = solve((curr, key))
        xored = xor(data, currRes)
        totalRes += xored
        counter += 1
    return totalRes

if __name__ == '__main__':
    key = '1010000010'
    print('Podaj nazwę pliku wejsciowego')
    path = input()
    print('Podaj nazwe pliku wyjsciowego')
    outpath = input()
    print('Podaj tryb kodowania')
    print('1) ecb')
    print('2) cbc')
    print('3) cfb')
    print('4) ctr')
    opt = int(input())
    file = createFile(path)
    mode = None
    if opt == 1:
        mode = ecb
    elif opt == 2:
        mode = cbc
    elif opt == 3:
        mode = cfb
    elif opt == 4:
        mode = ctr
    res = mode(key, file.getBinaryData())
    file.saveEncoded(res, outpath)
