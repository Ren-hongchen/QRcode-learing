import copy
from constant import *
import math
import numpy as np
from PIL import Image

sequence = []

# CapacityTable is not strictly orderly tuple, 
# but we can noticed that tuple is orderly when we have fixed ec_level and encodeMode,
# so we can redifine bisect algorithm
def get_suitable_version(encode_mode, ec_level, target):
    low = 0
    high = 39

    while low < high:
        mid = (low + high) // 2
        data = CAPACITY_TABLE[mid * 4 + ec_level][encode_mode]
        if(data < target):
            low = mid + 1
        else:
            high = mid
    return low + 1

def get_max_capacity(version, ec_level) -> int:
    return BLOCK_TABLE[(version - 1) * 4 + ec_level][0] * 8

def get_generator_polynomial(version, ec_level):
    ec_code_words = BLOCK_TABLE[(version - 1) * 4 + ec_level][1]
    return caculate_generator_polynomial(ec_code_words)

def caculate_generator_polynomial(ec_code_words):
    if(ec_code_words == 1):
        return [0,0]
    return mul(caculate_generator_polynomial(ec_code_words - 1), [0, ec_code_words - 1])

def mul(a, b):
    result = [None] * (b[1] + 2)
    for i,item1 in enumerate(a):
        for j, item2 in enumerate(b):
            if(result[i+j] == None):
                result[i+j] = item1 + item2
            else:
                #AlphaNumber = getAlpha(result[i+j]) ^ getAlpha(item1 + item2)
                if(result[i+j] > 255):
                    result[i+j] = result[i+j] % 255
                alpha_number = ALPHA_TABLE[result[i+j]] ^ ALPHA_TABLE[item1 + item2]
                #result[i+j] = getAlphaIndex(AlphaNumber)
                result[i+j] = ALPHA_TABLE.index(alpha_number)
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


def get_message_polynomial(data):
    messagePolynomial = []
    for i in range(0, len(data), 8):
        a = int(data[i:i+8], 2)
        messagePolynomial.append(a)
    return messagePolynomial


def get_polynomial_division(message_polynomial, generator_polynomial, deepth):
    if(deepth == 0):
        return message_polynomial
    M = np.array(message_polynomial)
    G = np.array(generator_polynomial)
    if(M[0] == 0):
        M = np.delete(M,0)
        return get_polynomial_division(M, G, deepth-1)
    #first = getAlphaIndex(M[0])
    first = ALPHA_TABLE.index(M[0])
    a = G + first

    a[a > 255 ] = a[a > 255] % 255

    for i in range(0,len(a)):
        a[i] = ALPHA_TABLE[a[i]]
        #a[i] = getAlpha(a[i])

    if(len(a) < len(M)):
        a = np.pad(a, (0, len(M)-len(a)), 'constant', constant_values = (0,0))
    else:
        M = np.pad(M, (0, len(a)-len(M)), 'constant', constant_values = (0,0))    
    
    a = a ^ M

    if(a[0] == 0):
        a = np.delete(a,0)
    
    return get_polynomial_division(a,G,deepth - 1)


def get_error_correct_codes(data, version, ec_level):
    message_polynomial = get_message_polynomial(data)
    generator_polynomial = get_generator_polynomial(version, ec_level)
    block = BLOCK_TABLE[(version - 1) * 4 + ec_level]
    block_length = len(block)
    index = 0
    result = []

    if(block_length == 4 and block[2] == 1):
        return get_polynomial_division(message_polynomial, generator_polynomial, len(message_polynomial))
    for _ in range(0,block[2]):
        message = message_polynomial[index : index+block[3]]
        index += block[3]
        result.append(get_polynomial_division(message, generator_polynomial, len(message)))
    if(block_length == 6):
        for _ in range(0,block[4]):
            message = message_polynomial[index : index+block[5]]
            index += block[5]
            result.append(get_polynomial_division(message, generator_polynomial, len(message)))

    return result



def interleave(data, version, ec_level, ec_code_words):  # need a better method :-(
    ec_codes_array = np.array(ec_code_words)
    block_table = BLOCK_TABLE[(version - 1) * 4 + ec_level]
    m = []
    n = []
    index = 0
    result = ""
    if(ec_codes_array.ndim == 1):
        for i in range(0, len(ec_codes_array)):
            data += bin(ec_code_words[i])[2:].zfill(8)
        return add_remainder_bits(data, version)
    else:
        m = get_message_polynomial(data)
        for _ in range(0, block_table[2]):
            n.append(m[index:index + block_table[3]])
            index += block_table[3]
        for _ in range(0, block_table[4]):
            n.append(m[index:index + block_table[5]])
            index += block_table[5]
        for i in range(0, max(block_table[3], block_table[5])):
            for j in range(0,block_table[2] + block_table[4]):
                if(i > len(n[j])-1):
                    continue
                result += bin(n[j][i])[2:].zfill(8)
        # add error correct codewords
        for i in range(0, block_table[1]):
            for j in range(0, block_table[2] + block_table[4]):
                result += bin(ec_codes_array[j][i])[2:].zfill(8)
    return add_remainder_bits(result, version)
    
def add_remainder_bits(result, version):
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

def get_initialized_map(version):
    size = ((version - 1) * 4) + 21
    map = np.full((size, size), 2, dtype=int)
    
    # set finder mask_pattern
    finder_pattern = np.array([[1,1,1,1,1,1,1],[1,0,0,0,0,0,1],[1,0,1,1,1,0,1],[1,0,1,1,1,0,1],
                             [1,0,1,1,1,0,1],[1,0,0,0,0,0,1],[1,1,1,1,1,1,1]])
    for i in ((0, 0), (size-7, 0), (0, size-7)):
        map[i[0]:i[0]+7, i[1]:i[1]+7] = finder_pattern
    
    # set seperator mask_pattern
    map[7, 0:8] = map[0:8, 7] = 0
    map[7, size-8:size] = map[size-8:size, 7] = 0
    map[0:8, size-8] = map[size-8, 0:8] = 0

    # set alignment mask_pattern
    align_pattern = np.array([[1,1,1,1,1], [1,0,0,0,1], [1,0,1,0,1], [1,0,0,0,1], [1,1,1,1,1]])
    if(version > 1):
        for i in ALIGNMENT_TABLE[version - 2]:
            for j in ALIGNMENT_TABLE[version -2]:
                if((i-2) < 8 and (j-2) < 8):
                    continue
                elif((i-2) < 8 and (j+2) > (size - 8)):
                    continue
                elif((i+2) > (size-8) and (j-2) < 8 ):
                    continue
                else:
                    map[i-2:i+3, j-2:j+3] = align_pattern
    
    # set timing patterns
    flag = True
    for i in range(8,size - 8):
        map[6, i] = map[i, 6] = 1 if flag else 0
        flag = not flag

    # set dark module
    map[(version * 4)+9, 8] = 1

    # set reserved area
    map[8, 0:6] = map[0:6, 8] = map[8, 7:9] = map[7:9, 8] = 0
    map[8, size-8:size] = map[size-7:size, 8] = 0
    if(version >= 7):
        map[0:6, size-11:size-7] = map[size-11:size-7, 0:6] = 0    

    get_sequence(map) # get data position sequence

    return map

def get_sequence(map):
    global sequence
    for i in range(0, map.shape[0]):
        for j in range(0, map.shape[1]):
            if(map[i, j] != 2):
                continue
            else:
                sequence.append((i, j))
    return 

def padding_data(map, data):
    m = 0
    j = map.shape[0] - 1 
    flag = True
    while(j > 0):
        if(j == 6):
            j -= 1
            continue
        if(flag):
            for i in range(map.shape[0]-1, -1, -1):
                if(map[i, j] != 2 and map[i, j-1] != 2):
                    continue
                elif(map[i, j] != 2):
                    map[i, j-1] = data[m]
                    m += 1
                elif(map[i, j-1] != 2):
                    map[i, j] = data[m]
                    m += 1
                else:
                    map[i, j] = data[m]
                    map[i, j-1] = data[m+1]
                    m += 2
        else:
            for i in range(0, map.shape[0]):
                if(map[i, j] != 2 and map[i, j-1] != 2):
                    continue
                elif(map[i, j] != 2):
                    map[i, j-1] = data[m]
                    m += 1
                elif(map[i, j-1] != 2):
                    map[i, j] = data[m]
                    m += 1
                else:
                    map[i, j] = data[m]
                    map[i, j-1] = data[m+1]
                    m += 2
    
        j -= 2
        flag = not flag
    return map

def get_masked_map(map, version, ec_level):
    min_score = 0
    result = np.array([])
    for i in range(0, 8):
        formula = get_mask_formula(i)
        copy_map = copy.deepcopy(map)
        masked_map = mask(copy_map, formula)
        final_map = padding_version_format(masked_map, version, ec_level, i)
        score = evaluation(final_map)
        if((score < min_score) or i == 0):
            min_score = score
            result = masked_map
    return result


def get_mask_formula(i):
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

def mask(map, formula):
    global sequence
    for i, j in sequence:
        if(formula(i, j)):
            map[i, j] = map[i, j] ^ 1
    return map

def evaluation(final_map):
    score = get_penalty_by_rule1(final_map)
    score += get_penalty_by_rule2(final_map)
    score += get_penalty_by_rule3(final_map)
    score += get_penalty_by_rule4(final_map)
    return score 

def padding_version_format(map, version, ec_level, mask_pattern):
    #Format Information
    format_info = get_format_info(ec_level, mask_pattern)
    #Version Information
    if(version >= 7):
        version_info = get_version_info(version)
    #padding format infomation
    index = 0
    for i, j in FORMAT_INFO_TABLE:
        map[i, j] = format_info[index]
        index += 1
    map[8, map.shape[0]-8:map.shape[0]] = format_info[7:15] 
    format_info = format_info[::-1]
    map[map.shape[0]-7:map.shape[0], 8] = format_info[8:15]
    #padding version information
    if(version >= 7):
        # bottom-left version block
        index = 0
        version_info = version_info[::-1]
        for i in range(0,6):
            for j in range(map.shape[0]-11,map.shape[0]-8):
                map[i, j] = version_info[index]
                map[j, i] = version_info[index]
                index += 1

    return map


def get_format_info(ec_level, mask_pattern):
    format = ""
    if(ec_level == 0): format = "01"
    elif(ec_level == 1): format = "00"
    elif(ec_level == 2): format = "11"
    else: format = "10"

    format += bin(mask_pattern)[2:].zfill(3)

    format = np.array(list(format), dtype=int)
    M = np.pad(format, (0,15-len(format)), 'constant', constant_values =(0,0))

    ec_codes = ReedSolomon(M, (10, [1,0,1,0,0,1,1,0,1,1,1]))

    format = np.concatenate((format,ec_codes), axis=0)
    mask = np.array([1,0,1,0,1,0,0,0,0,0,1,0,0,1,0])
    format = format ^ mask

    return format

def get_version_info(version):
    version = bin(version)[2:].zfill(6)
    version = np.array(list(version), dtype=int)
    M = np.pad(version, (0, 18-len(version)), 'constant', constant_values =(0, 0))
    ec_codes = ReedSolomon(M,(12, [1,1,1,1,1,0,0,1,0,0,1,0,1]))
    version = np.concatenate((version, ec_codes), axis=0)
    return version

def ReedSolomon(M, info):
    G = np.array(info[1])
    M = np.trim_zeros(M, 'f')
    if(M.shape[0] <= info[0]):
        M = np.pad(M, (info[0]-len(M), 0), 'constant', constant_values=(0, 0))
        return M

    if(G.shape[0] < M.shape[0]):
        G = np.pad(G, (0, M.shape[0]-G.shape[0]), 'constant', constant_values = (0,0))

    M = M ^ G

    return ReedSolomon(M, info)

def get_penalty_by_rule1(map):
    score_x = score_y = 0
    last_color_x = last_color_y = map[0, 0]
    count_x = count_y = 1
    for i in range(0, map.shape[0]):
        for j in range(1, map.shape[1]):
            # evaluate row
            if(map[i, j] == last_color_x):
                count_x += 1
            else:
                last_color_x = map[i, j]
                count_x = 1
            if(count_x >= 5):
                score_x += (3 + (count_x - 5))
            # evaluate column
            if(map[j, i] == last_color_y):
                count_y += 1
            else:
                last_color_y = map[j, i]
                count_y = 1
            if(count_y >= 5):
                score_y += (3 + (count_y - 5))
    return score_x + score_y

def get_penalty_by_rule2(map):
    score = 0
    for i in range(0, map.shape[0] - 1):
        for j in range(0, map.shape[1] - 1):
            module = map[i, j]
            if (map[i, j+1] == module) and (map[i+1, j] == module) and (map[i+1, j+1] == module):
                score += 3
    return score

def get_penalty_by_rule3(map):
    score = 0
    pattern1 = np.array([1,0,1,1,1,0,1,0,0,0,0])
    pattern2 = np.array([0,0,0,0,1,0,1,1,1,0,1])
    for i in range(0, map.shape[0] - 11):
        for j in range(0, map.shape[1] - 11):
            if (map[i:i+11, j] == pattern1).all() or (map[i:i+11, j] == pattern2).all():
                score += 40
            if (map[i, j:j+11] == pattern1).all() or (map[i, j:j+11] == pattern2).all():
                score += 40
    return score

def get_penalty_by_rule4(map):
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
    image = Image.new('1', [(len(map)+8)*block_len]*2, 'white')
    for i in range(0, map.shape[0]):
        for j in range(0, map.shape[1]):
            if(map[i, j] == 1):
                draw_bit(image, x, y, block_len)
            x += block_len
        x, y = block_len*4, y+block_len
    image.save("out.png") 
    return

def draw_bit(image, x, y, le):
    for i in range(le):
        for j in range(le):
            image.putpixel((x+i, y+j),0)
    return


    
