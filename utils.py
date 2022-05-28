import copy
from constant import *
import math
import numpy as np
from PIL import Image

sequence = []

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
                #AlphaNumber = getAlpha(result[i+j]) ^ getAlpha(item1 + item2)
                if(result[i+j] > 255):
                    result[i+j] = result[i+j] % 255
                AlphaNumber = AlphaTable[result[i+j]] ^ AlphaTable[item1 + item2]
                #result[i+j] = getAlphaIndex(AlphaNumber)
                result[i+j] = AlphaTable.index(AlphaNumber)
    return result


# def getAlpha(a):
#     if(a == 0):
#         return 1
#     result = getAlpha(a-1) * 2
#     while(result > 255):
#         result = result ^ 285
#     return result

# def getAlphaIndex(a): 
#     if(math.log(a,2) % 1 == 0):
#         return int(math.log(a,2))
#     elif(a % 2 == 0):
#         return getAlphaIndex(a // 2) + 1
#     else:
#         a = a ^ 285
#         return getAlphaIndex(a)


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
    if(M[0] == 0):
        M = np.delete(M,0)
        return getPolynomialDivision(M,G,deepth-1)
    #first = getAlphaIndex(M[0])
    first = AlphaTable.index(M[0])
    a = G + first

    a[a > 255 ] = a[a > 255] % 255

    for i in range(0,len(a)):
        a[i] = AlphaTable[a[i]]
        #a[i] = getAlpha(a[i])

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
        for i in range(0,len(ec)):
            data += bin(eccodewords[i])[2:].zfill(8)
        return addRemainderBits(data,version)
    else:
        m = getMessagePolynomial(data)
        for _ in range(0,blocktable[2]):
            n.append(m[index:index + blocktable[3]])
            index += blocktable[3]
        for _ in range(0,blocktable[4]):
            n.append(m[index:index + blocktable[5]])
            index += blocktable[5]
        for i in range(0,max(blocktable[3],blocktable[5])):
            for j in range(0,blocktable[2] + blocktable[4]):
                if(i > len(n[j])-1):
                    continue
                result += bin(n[j][i])[2:].zfill(8)
        # add error correct codewords
        for i in range(0,blocktable[1]):
            for j in range(0,blocktable[2] + blocktable[4]):
                result += bin(ec[j][i])[2:].zfill(8)
    return addRemainderBits(result,version)
    
def addRemainderBits(result,version):
    # add remainder bits if necessary
    if(2 <= version <= 6):
        return result + '0000000'
    elif(14 <= version <=20):
        return result + '000'
    elif(21 <= version <= 27):
        return result + '0000'
    elif(28 <= version <= 34):
        return result + '000'
    else:
        return result

def getInitializedMap(version):
    size = ((version - 1) * 4) + 21
    map = np.full((size,size),2,dtype=int)
    
    # set finder pattern
    finderpattern = np.array([[1,1,1,1,1,1,1],[1,0,0,0,0,0,1],[1,0,1,1,1,0,1],[1,0,1,1,1,0,1],
                             [1,0,1,1,1,0,1],[1,0,0,0,0,0,1],[1,1,1,1,1,1,1]])
    for i in ((0,0),(size-7,0),(0,size-7)):
        map[i[0]:i[0]+7, i[1]:i[1]+7] = finderpattern
    
    # set seperator pattern
    map[7,0:8] = map[0:8,7] = 0
    map[7,size-8:size] = map[size-8:size,7] = 0
    map[0:8,size-8] = map[size-8,0:8] = 0

    # set alignment pattern
    alignpattern = np.array([[1,1,1,1,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,0,1],[1,1,1,1,1]])
    if(version > 1):
        for i in AlignmentTable[version - 2]:
            for j in AlignmentTable[version -2]:
                if((i-2) < 8 and (j-2) < 8):
                    continue
                elif((i-2) < 8 and (j+2) > (size - 8)):
                    continue
                elif((i+2) > (size-8) and (j-2) < 8 ):
                    continue
                else:
                    map[i-2:i+3,j-2:j+3] = alignpattern
    
    # set timing patterns
    flag = True
    for i in range(8,size - 8):
        if(flag == True):
            map[6,i] = map[i,6] = 1
        else:
            map[6,i] = map[i,6] = 0
        flag = not flag

    # set dark module
    map[(version * 4)+9,8] = 1

    # set reserved area
    map[8,0:6] = map[0:6,8] = map[8,7:9] = map[7:9,8] = 0
    map[8,size-8:size] = map[size-7:size,8] = 0
    if(version >= 7):
        map[0:6,size-11:size-7] = map[size-11:size-7,0:6] = 0    

    getSequence(map) # get data position sequence

    return map

def getSequence(map):
    global sequence
    for i in range(0,map.shape[0]):
        for j in range(0,map.shape[1]):
            if(map[i,j] != 2):
                continue
            else:
                sequence.append((i,j))
    return 

def paddingData(map,data):
    m = 0
    j = map.shape[0] - 1 
    flag = True
    while(j > 0):
        if(j == 6):
            j -= 1
            continue
        if(flag):
            for i in range(map.shape[0]-1,-1,-1):
                if(map[i,j] != 2 and map[i,j-1] != 2):
                    continue
                elif(map[i,j] != 2):
                    map[i,j-1] = data[m]
                    m += 1
                elif(map[i,j-1] != 2):
                    map[i,j] = data[m]
                    m += 1
                else:
                    map[i,j] = data[m]
                    map[i,j-1] = data[m+1]
                    m += 2
        else:
            for i in range(0,map.shape[0]):
                if(map[i,j] != 2 and map[i,j-1] != 2):
                    continue
                elif(map[i,j] != 2):
                    map[i,j-1] = data[m]
                    m += 1
                elif(map[i,j-1] != 2):
                    map[i,j] = data[m]
                    m += 1
                else:
                    map[i,j] = data[m]
                    map[i,j-1] = data[m+1]
                    m += 2
    
        j -= 2
        flag = not flag
    return map

def getMaskedMap(map,version,level):
    min_score = 0
    result = np.array([])
    for i in range(0,8):
        formula = getMaskFormula(i)
        copy_map = copy.deepcopy(map)
        masked_map = mask(copy_map,formula)
        final_map = paddingVersionFormat(masked_map,version,level,i)
        score = evaluation(final_map)
        if((score < min_score) or i == 0):
            min_score = score
            result = masked_map
    return result


def getMaskFormula(i):
    if(i == 0):
        return lambda x,y : (x + y) % 2 == 0
    elif(i == 1):
        return lambda x,y : x % 2 == 0
    elif(i == 2):
        return lambda x,y : y % 3 == 0
    elif(i == 3):
        return lambda x,y : (x + y) % 3 == 0
    elif(i == 4):
        return lambda x,y : (math.floor(x / 2) + math.floor(y / 3)) % 2 == 0
    elif(i == 5):
        return lambda x,y : ((x * y) % 2) + ((x * y) % 3) == 0
    elif(i == 6):
        return lambda x,y : (((x * y) % 2) + ((x * y) % 3)) % 2 == 0
    else:
        return lambda x,y : (((x + y) % 2) + ((x * y) % 3)) % 2 == 0 

def mask(map,formula):
    global sequence
    for i,j in sequence:
        if(formula(i,j)):
            map[i,j] = map[i,j] ^ 1
    return map

def evaluation(final_map):
    score = getPenaltybyRule1(final_map)
    score += getPenaltybyRule2(final_map)
    score += getPenaltybyRule3(final_map)
    score += getPenaltybyRule4(final_map)
    return score 

def paddingVersionFormat(map,version,level,pattern):
    #Format Information
    formatinfo = getFormatInfoEC(level,pattern)
    #Version Information
    if(version >= 7):
        versioninfo = getVersionInfoEC(version)
    #padding format infomation
    index = 0
    for i,j in FormatInfoTable:
        map[i,j] = formatinfo[index]
        index += 1
    map[8,map.shape[0]-8:map.shape[0]] = formatinfo[7:15] 
    formatinfo = formatinfo[::-1]
    map[map.shape[0]-7:map.shape[0],8] = formatinfo[8:15]
    #padding version information
    if(version >= 7):
        # bottom-left version block
        index = 0
        versioninfo = versioninfo[::-1]
        for i in range(0,6):
            for j in range(map.shape[0]-11,map.shape[0]-8):
                map[i,j] = versioninfo[index]
                map[j,i] = versioninfo[index]
                index += 1

    return map


def getFormatInfoEC(level,pattern):
    format = ""
    if(level == 0): format = "01"
    elif(level == 1): format = "00"
    elif(level == 2): format = "11"
    else: format = "10"

    format += bin(pattern)[2:].zfill(3)

    format = np.array(list(format),dtype=int)
    M = np.pad(format,(0,15-len(format)),'constant',constant_values =(0,0))

    eccodes = ReedSolomon(M,(10,[1,0,1,0,0,1,1,0,1,1,1]))

    format = np.concatenate((format,eccodes),axis=0)
    mask = np.array([1,0,1,0,1,0,0,0,0,0,1,0,0,1,0])
    format = format ^ mask

    return format

def getVersionInfoEC(version):
    version = bin(version)[2:].zfill(6)
    version = np.array(list(version),dtype=int)
    M = np.pad(version,(0,18-len(version)),'constant',constant_values =(0,0))
    eccodes = ReedSolomon(M,(12,[1,1,1,1,1,0,0,1,0,0,1,0,1]))
    version = np.concatenate((version,eccodes),axis=0)
    return version

def ReedSolomon(M,info):
    G = np.array(info[1])
    M = np.trim_zeros(M,'f')
    if(M.shape[0] <= info[0]):
        M = np.pad(M,(info[0]-len(M),0),'constant',constant_values=(0,0))
        return M

    if(G.shape[0] < M.shape[0]):
        G = np.pad(G,(0,M.shape[0]-G.shape[0]),'constant',constant_values = (0,0))

    M = M ^ G

    return ReedSolomon(M,info)

def getPenaltybyRule1(map):
    score_x = score_y = 0
    last_color_x = last_color_y = map[0,0]
    count_x = count_y = 1
    for i in range(0,map.shape[0]):
        for j in range(1,map.shape[1]):
            # evaluate row
            if(map[i,j] == last_color_x):
                count_x += 1
            else:
                last_color_x = map[i,j]
                count_x = 1
            if(count_x >= 5):
                score_x += (3 + (count_x - 5))
            # evaluate column
            if(map[j,i] == last_color_y):
                count_y += 1
            else:
                last_color_y = map[j,i]
                count_y = 1
            if(count_y >= 5):
                score_y += (3 + (count_y - 5))
    return score_x + score_y

def getPenaltybyRule2(map):
    score = 0
    for i in range(0,map.shape[0] - 1):
        for j in range(0,map.shape[1] - 1):
            module = map[i,j]
            if (map[i,j+1] == module) and (map[i+1,j] == module) and (map[i+1,j+1] == module):
                score += 3
    return score

def getPenaltybyRule3(map):
    score = 0
    pattern1 = np.array([1,0,1,1,1,0,1,0,0,0,0])
    pattern2 = np.array([0,0,0,0,1,0,1,1,1,0,1])
    for i in range(0,map.shape[0] - 11):
        for j in range(0,map.shape[1] - 11):
            if (map[i:i+11,j] == pattern1).all() or (map[i:i+11,j] == pattern2).all():
                score += 40
            if (map[i,j:j+11] == pattern1).all() or (map[i,j:j+11] == pattern2).all():
                score += 40
    return score

def getPenaltybyRule4(map):
    total_count = map.shape[0] * map.shape[1]
    dark_count = np.count_nonzero(map == 1)
    ratio = dark_count / total_count
    previous = math.floor(ratio / 5) * 5
    next = (math.floor(ratio / 5) + 1) * 5
    score = min(abs(previous - 50) / 5, abs(next - 50) / 5)
    return score * 10

def draw(map):
    block_len = 5
    x = y = block_len * 4
    image = Image.new('1',[(len(map)+8)*block_len]*2,'white')
    for i in range(0,map.shape[0]):
        for j in range(0,map.shape[1]):
            if(map[i,j] == 1):
                draw_bit(image,x,y,block_len)
            x += block_len
        x,y = block_len*4,y+block_len
    image.save("out.png") 
    return

def draw_bit(image,x,y,le):
    for i in range(le):
        for j in range(le):
            image.putpixel((x+i,y+j),0)
    return


    
