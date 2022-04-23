from constant import *
import math


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




    
    