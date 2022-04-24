from email import message
from inspect import getgeneratorlocals
from constant import *
import math
import numpy as np

# CapacityTable is not strictly orderly tuple, 
# but we can noticed that tuple is orderly when we have fixed level and encodeMode,
# so we can redifine bisect algorithm
def bisect(encodeMode,level,target):
    low = 0
    high = 39

    while low < high:
        mid = (low + high) // 2
        data = CapacityTable[mid * 4 + level][encodeMode]
        if(data < target):
            low = mid + 1
        else:
            high = mid
    return low + 1

def getMaxCapacity(version,level) -> int:
    return BlockTable[(version - 1) * 4 + level][0] * 8

def getGeneratorPolynomial(version,level):
    ECcodewords = BlockTable[(version - 1) * 4 + level][1]
    return caculateGeneratorPolynomial(ECcodewords)

def caculateGeneratorPolynomial(ECcodewords):
    if(ECcodewords == 1):
        return [0,0]
    return mul(caculateGeneratorPolynomial(ECcodewords - 1), [0,ECcodewords - 1])

def mul(a,b):
    result = [None] * (b[1] + 2)
    for i,item1 in enumerate(a):
        for j, item2 in enumerate(b):
            if(result[i+j] == None):
                result[i+j] = item1 + item2
            else:
                AlphaNumber = getAlpha(result[i+j]) ^ getAlpha(item1 + item2)
                result[i+j] = getAlphaIndex(AlphaNumber)
    return result


def getAlpha(a):
    if(a == 0):
        return 1
    result = getAlpha(a-1) * 2
    while(result > 255):
        result = result ^ 285
    return result

def getAlphaIndex(a):
    if(math.log(a,2) % 1 == 0):
        return int(math.log(a,2))
    elif(a % 2 == 0):
        return getAlphaIndex(a // 2) + 1
    else:
        a = a ^ 285
        return getAlphaIndex(a)


def getMessagePolynomial(data):
    messagePolynomial = []
    for i in range(0,len(data),8):
        a = int(data[i:i+8],2)
        messagePolynomial.append(a)
    return messagePolynomial


def getPolynomialDivision(MP,GP,deepth):
    if(deepth == 0):
        return MP
    M = np.array(MP)
    G = np.array(GP)

    first = getAlphaIndex(M[0])
    a = G + first

    a[a > 255 ] = a[a > 255] % 255

    for i in range(0,len(a)):
        a[i] = getAlpha(a[i])

    if(len(a) < len(M)):
        a = np.pad(a,(0,len(M)-len(a)), 'constant', constant_values = (0,0))
    else:
        M = np.pad(M,(0,len(a)-len(M)), 'constant', constant_values = (0,0))    
    
    a = a ^ M

    if(a[0] == 0):
        a = np.delete(a,0)
    
    return getPolynomialDivision(a,G,deepth - 1)


def getErrorCorrectCodes(data,version,level):
    messagePolynomial = getMessagePolynomial(data)
    generatorPolynomial = getGeneratorPolynomial(version,level)
    block = BlockTable[(version - 1) * 4 + level]
    length = len(block)
    index = 0
    result = []

    if(length == 4 and block[2] == 1):
        return getPolynomialDivision(messagePolynomial,generatorPolynomial,len(messagePolynomial))
    for _ in range(0,block[2]):
        message = messagePolynomial[index:index+block[3]]
        index += block[3]
        result.append(getPolynomialDivision(message,generatorPolynomial,len(message)))
    if(length == 6):
        for _ in range(0,block[4]):
            message = messagePolynomial[index:index+block[5]]
            index += block[5]
            result.append(getPolynomialDivision(message,generatorPolynomial,len(message)))

    return result



def interleave(data,version,level,eccodewords):  # need a better method :-(
    ec = np.array(eccodewords)
    blocktable = BlockTable[(version - 1) * 4 + level]
    m = []
    n = []
    index = 0
    result = ""
    if(ec.ndim == 1):
        for i in range(0,len(ec),8):
            data += bin(eccodewords[i])[2:].zfill(8)
        return data
    else:
        m = getMessagePolynomial(data)
        for _ in range(0,blocktable[2]):
            n.append(m[index:index + blocktable[3]])
            index += blocktable[3]
        for _ in range(0,blocktable[4]):
            n.append(m[index:index + blocktable[5]])
            index += blocktable[5]
        for i in range(0,max(blocktable[3],blocktable[5]) - 1):
            for j in range(0,blocktable[2] + blocktable[4]):
                if(i > len(n[j])):
                    continue
                result += bin(n[j][i])[2:].zfill(8)
        # add ec codewords
        

    return result

