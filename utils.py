from constant import *

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