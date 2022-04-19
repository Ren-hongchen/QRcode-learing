# QRcode version-1 M
import numpy
import turtle
import copy

QRcodeIndex = {
    '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
    'A':10,'B':11,'C':12,'D':13,'E':14,'F':15,'G':16,'H':17,'I':18,
    'J':19,'K':20,'L':21,'M':22,'N':23,'O':24,'P':25,'Q':26,'R':27,
    'S':28,'T':29,'U':30,'V':31,'W':32,'X':33,'Y':34,'Z':35,' ':36,
    '$':37,'%':38,'*':39,'+':40,'-':41,'.':42,'/':43,':':44
}

AlphaTable = [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19, 38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96, 192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159, 35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222, 161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120, 240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113, 226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103, 206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 
51, 102, 204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42, 84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183, 115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241, 255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174, 65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83, 166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 
155, 43, 86, 172, 69, 138, 9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11, 22, 44, 88, 176, 125, 250, 233, 207, 131, 
27, 54, 108, 216, 173, 71, 142, 1]

# def getAlphaTable():
#     AlphaTable = [1]
#     for n in range(1,256):
#         alpha = AlphaTable[n-1]*2
#     while(alpha > 255):
#         alpha = alpha ^ 285
#     AlphaTable.append(alpha)

#     return AlphaTable

maskmode = 0

def getIndex(string):   #根据输入字符串获取对应索引
    Index=[]
    for word in string:
        Index.append(QRcodeIndex[word])
    Single=[]
    Double=[]
    if len(Index) % 2 ==0:
        for i in range(0,len(Index)):
            if i % 2 == 0:
                Double.append(Index[i])
            else:
                Single.append(Index[i])
    
        NewIndex = zip(Double,Single) #0开头，顺序调换一下
        NewIndex = list(NewIndex)

    else:
        lastnumber = Index[-1]
        del(Index[-1])
        for i in range(0,len(Index)):
            if i % 2 == 0:
                Double.append(Index[i])
            else:
                Single.append(Index[i])
        newIndex = zip(Double,Single)
        NewIndex = list(newIndex)
        NewIndex.append(lastnumber)
    return NewIndex     #返回索引数组

def getStringLength(string):   #根据输入字符串获取字符串长度并转成9位二进制
    length = len(string)
    B_lengthString = bin(length)[2:]
    while(len(B_lengthString) < 9):
        B_lengthString = '0' + B_lengthString

    return '0010' + B_lengthString    #补上字符模式编码0010返回

def getDataCode(Index):   #生成数据码
    NewIndex=[]
    if type(Index[-1]) == tuple:
        for x in Index:
            IndexPairNumber = x[0]*45+x[1]
            B_IndexPairNumber = bin(IndexPairNumber)[2:]
            while(len(B_IndexPairNumber)< 11):
                B_IndexPairNumber = '0' + B_IndexPairNumber
            NewIndex.append(B_IndexPairNumber)
    else:
        TheSingleNumber = Index[-1]
        B_TheSingleNumber = bin(TheSingleNumber)[2:]
        while (len(B_TheSingleNumber)< 6):
            B_TheSingleNumber = '0' + B_TheSingleNumber
        del(Index[-1])

        for x in Index:
            IndexPairNumber = x[0]*45+x[1]
            B_IndexPairNumber = bin(IndexPairNumber)[2:]
            while(len(B_IndexPairNumber)< 11):
                B_IndexPairNumber = '0' + B_IndexPairNumber
            NewIndex.append(B_IndexPairNumber)
        NewIndex.append(B_TheSingleNumber)

    return NewIndex

def CheckDataCode(String,Index):   #检查数据码 拼接
    Indexstring = ""
    for x in Index:
        Indexstring = Indexstring + x
    datacode = String + Indexstring
    length = len(datacode)
    if 128-length >= 4:
        datacode = datacode + '0000'
        length = len(datacode)
    if length < 128:
        while(length % 8 != 0):
            datacode = datacode + '0'
            length = len(datacode)
        if(length < 128):
            i = 0
            while(len(datacode) != 128):
                if(i%2 == 0):
                    datacode = datacode + '11101100'
                else:
                    datacode = datacode + '00010001'
                i=i+1
            
    return datacode

def getMessagePolynomial(string):  #生成消息多项式,仅系数
    MessagePolynomial = []
    for x in range(0,121,8):
        s = string[x:x+8]
        coefficient = int(s,2)
        MessagePolynomial.append(coefficient)
    
    return MessagePolynomial


def getGeneratorPolynomial():    #生成生成多项式
    GeneratorPolynomial = [0,251,67,46,61,118,70,
                            64,94,32,45]   #纠错码个数为10的生成多项式系数
    return GeneratorPolynomial

def getErrorCorrectionCode(MessagePolynomial,GeneratorPolynomial,deepth):   #生成最终纠错码    
    if deepth == 0:
        return MessagePolynomial
    M = numpy.array(MessagePolynomial)
    G = numpy.array(GeneratorPolynomial)
    FirstCoefficient = AlphaTable.index(MessagePolynomial[0])
    a1 = G + FirstCoefficient

    a1[a1 > 255] = a1[a1 > 255] % 255    # a1中所有大于255的数全部对255求模替换
    for n in range(0,len(a1)):
        a1[n] = AlphaTable[a1[n]]

    if len(M) < len(a1):    #此步必须在将α系数表示法转为十进制表示法之后进行，因为程序使用的多项式表示法只表示了系数
        n = len(a1) - len(M)
        while(n != 0):
            M = numpy.append(M,0)
            n-=1
    else:
        n = len(M)-len(a1)
        while(n != 0):
            a1 = numpy.append(a1,0)
            n-=1
    b1 = a1 ^ M
    if b1[0]==0:    #去掉系数为0的首项
        b1 = numpy.delete(b1,0)
    #print(b1)
    return getErrorCorrectionCode(b1,GeneratorPolynomial,deepth-1)

def getMixedCode(DataCode,ErrorCode):   #将数据码和纠错码拼接并转为二进制
    datacode = numpy.array(DataCode)
    MixedCode = numpy.concatenate([datacode,ErrorCode],axis = 0)
    MixedCodeString = ""
    for n in range(0,len(MixedCode)):
        bincode = bin(MixedCode[n])[2:]
        while( len(bincode)< 8):    #都补齐到8位
            bincode = '0' + bincode
        MixedCodeString =  MixedCodeString+bincode
    return MixedCodeString

def darwQRcode(binstring):     #绘制二维码点阵，不包括版本信息
    QRcodemap = numpy.full((21,21),0)
    for X in range(0,21):
        for Y in range(0,21):
            #绘制定位符
            if ((X==0 or X==6) and Y in range(0,7)) or ((X==0 or X==6) and Y in range(14,21)):
                QRcodemap[X,Y] = 1
            if ((X==1 or X==5) and Y in (0,6,14,20)):
                QRcodemap[X,Y] = 1
            if ((X==2 or X==3 or X==4) and Y in (0,2,3,4,6,14,16,17,18,20)):
                QRcodemap[X,Y] = 1
            if (X==14 or X==20 and Y in range(0,7)):
                QRcodemap[X,Y] = 1
            if ((X==15 or X==19) and Y in (0,6)):
                QRcodemap[X,Y] = 1
            if ((X==16 or X==17 or X==18) and Y in (0,2,3,4,6)):
                QRcodemap[X,Y] = 1
            #绘制分隔符
            if (X in range(0,7) and (Y==7 or Y == 13)):
                QRcodemap[X,Y] = 0
            if (X==7  and (Y in range(0,8) or Y in range(7,21))):
                QRcodemap[X,Y] = 0
            if (X==13 and Y in range(0,8)) or (X in range(14,21) and Y==7):
                QRcodemap[X,Y] = 0
            #添加暗模块
            if (X==13 and Y==8):
                QRcodemap[X,Y] = 1
            #设置保留区域
            if (X in range(0,7) or X in range(14,21)) and Y==8:
                QRcodemap[X,Y] = 0
            if X==8 and (Y in range(0,9) or Y in range(13,21)):
                QRcodemap[X,Y] = 0
            #绘制时序图
            if (X==6 and Y in (8,10,12)):
                QRcodemap[X,Y] = 1
            if (X in (8,10,12) and Y==6):
                QRcodemap[X,Y] = 1
    n = 0  
    for X in range(20,8,-1):
        Y=20
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2

    for X in range(9,21):
        Y=18
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2
 
    for X in range(20,8,-1):
        Y=16
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2

    for X in range(9,21):
        Y=14
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2

    for X in range(20,-1,-1):
        Y=12
        if(X==6):
            continue
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2
    
    for X in range(0,21):
        Y=10
        if(X==6):
            continue
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2
    
    for X in range(12,8,-1):
        Y=8
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2

    for X in range(9,13):
        Y=5
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2
    
    for X in range(12,8,-1):
        Y=3
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2

    for X in range(9,13):
        Y=1
        QRcodemap[X,Y] = binstring[n]
        QRcodemap[X,Y-1] = binstring[n+1]
        n+=2
    print(n)
    return QRcodemap

def getMaskCode(QRcodemap):     #获取进行最佳掩码后的二维码点阵
    #drawFinalQRCode(QRcodemap)
    global maskmode
    map1 = copy.deepcopy(QRcodemap)
    map2 = copy.deepcopy(QRcodemap)
    map3 = copy.deepcopy(QRcodemap)
    map4 = copy.deepcopy(QRcodemap)
    map5 = copy.deepcopy(QRcodemap)
    map6 = copy.deepcopy(QRcodemap)
    map7 = copy.deepcopy(QRcodemap)
    map8 = copy.deepcopy(QRcodemap)

    score = []
    masked_map = []
    
    masked_map1 = MaskMode1(map1)
    maskmode = 0
    versionstring1 = getVersionMessage()
    new_masked_map1 = getFinalQRcodemap(versionstring1,masked_map1)
    score.append(assess(new_masked_map1))
    masked_map.append(new_masked_map1)

    masked_map2 = MaskMode2(map2)
    maskmode = 1
    versionstring2 = getVersionMessage()
    new_masked_map2 = getFinalQRcodemap(versionstring2,masked_map2)
    score.append(assess(new_masked_map2))
    masked_map.append(new_masked_map2)
    
    masked_map3 = MaskMode3(map3)
    maskmode = 2
    versionstring3 = getVersionMessage()
    new_masked_map3 = getFinalQRcodemap(versionstring3,masked_map3)
    score.append(assess(new_masked_map3))
    masked_map.append(new_masked_map3)

    masked_map4 = MaskMode4(map4)
    maskmode = 3
    versionstring4 = getVersionMessage()
    new_masked_map4 = getFinalQRcodemap(versionstring4,masked_map4)
    score.append(assess(new_masked_map4))
    masked_map.append(new_masked_map4)

    masked_map5 = MaskMode5(map5)
    maskmode = 4
    versionstring5 = getVersionMessage()
    new_masked_map5 = getFinalQRcodemap(versionstring5,masked_map5)
    score.append(assess(new_masked_map5))
    masked_map.append(new_masked_map5)

    masked_map6 = MaskMode6(map6)
    maskmode = 5
    versionstring6 = getVersionMessage()
    new_masked_map6 = getFinalQRcodemap(versionstring6,masked_map6)
    score.append(assess(new_masked_map6))
    masked_map.append(new_masked_map6)

    masked_map7 = MaskMode7(map7)
    maskmode = 6
    versionstring7 = getVersionMessage()
    print(versionstring7)
    new_masked_map7 = getFinalQRcodemap(versionstring7,masked_map7)
    score.append(assess(new_masked_map7))
    masked_map.append(new_masked_map7)

    masked_map8 = MaskMode8(map8)
    maskmode = 7
    versionstring8 = getVersionMessage()
    new_masked_map8 = getFinalQRcodemap(versionstring8,masked_map8)
    score.append(assess(new_masked_map8))
    masked_map.append(new_masked_map8)

    index = score.index(min(score))
    maskmode = index
    # for x in masked_map:
    #     print (x)
    return masked_map[index]

def MaskMode1(QRcodemap):   #掩码模式1
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (X + Y) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (X + Y) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (X + Y) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode2(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if X % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if X % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if X % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode3(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if Y % 3 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if Y % 3 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if Y % 3 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode4(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (X + Y) % 3 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (X + Y) % 3 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (X + Y) % 3 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode5(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (numpy.floor(X/2) + numpy.floor(Y/3)) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (numpy.floor(X/2) + numpy.floor(Y/3)) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (numpy.floor(X/2) + numpy.floor(Y/3)) % 2 == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode6(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (((X * Y) % 2) + ((X * Y) % 3)) == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (((X * Y) % 2) + ((X * Y) % 3)) == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (((X * Y) % 2) + ((X * Y) % 3)) == 0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode7(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (((X * Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (((X * Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (((X * Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def MaskMode8(QRcodemap):
    for X in range(0,9):
        for Y in range(9,13):
            if X == 6:
                continue
            if (((X + Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(9,13):
        for Y in range(0,21):
            if Y == 6:
                continue
            if (((X + Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    for X in range(13,21):
        for Y in range(9,21):
            if (((X + Y) % 2) + ((X * Y) % 3)) % 2 ==0:
                if QRcodemap[X,Y] == 0:
                    QRcodemap[X,Y] = 1
                    continue
                if QRcodemap[X,Y] == 1:
                    QRcodemap[X,Y] = 0
                    continue
    return QRcodemap

def assess(map):    #评估进行掩码后的二维码得分
    score1 = 0
    score2 = 0
    score3 = 0
    score4 = 0
    #drawFinalQRCode(map)
    #评估条件一
    n = 1
    row_score = 0
    for X in range(0,21):
        for Y in range(0,20):    #Y+1 到 20
            if map[X,Y] == map[X,Y+1]:
                n += 1
            else:
                n = 1
                score1 = score1 + row_score
                row_score = 0
            if n >= 5:
                row_score = 3 + (n-5) * 1
        if row_score != 0:
            score1 = score1 + row_score
        n = 1

    col_score = 0
    n = 1
    for Y in range(0,21):
        for X in range(0,20):
            if map[X,Y] == map[X+1,Y]:
                n += 1
            else:
                n = 1
                score1 = score1 + col_score
                col_score = 0
            if n >= 5:
                col_score = 3 + (n-5) * 1
        if col_score != 0:
            score1 = score1 + col_score
        n =1
    
    #评估条件2
    for X in range(0,20):   #X+1 Y+1 到20
        for Y in range(0,20):
            if map[X,Y] == map[X,Y+1] == map[X+1,Y] == map[X+1,Y+1]:
                score2 = score2 + 3
    
    #评估条件3
    for X in range(0,21):
        for Y in range(0,11):   #Y+10 到 20:
            if map[X,Y] == map[X,Y+1] == map[X,Y+2]  == map[X,Y+3] == 0:
                if map[X,Y+4]==1 and map[X,Y+5]==0 and map[X,Y+6]==1 and map[X,Y+7]==1 and map[X,Y+8]==1 and map[X,Y+9]==0 and map[X,Y+10]==1:
                    score3 = score3 + 40
            if map[X,Y+7] == map[X,Y+8] == map[X,Y+9]  == map[X,Y+10] == 0:
                if map[X,Y]==1 and map[X,Y+1]==0 and map[X,Y+2]==1 and map[X,Y+3]==1 and map[X,Y+4]==1 and map[X,Y+5]==0 and map[X,Y+6]==1:
                    score3 = score3 + 40
    for Y in range(0,21):
        for X in range(0,11):
            if map[X,Y] == map[X+1,Y] == map[X+2,Y]  == map[X+3,Y] == 0:
                if map[X+4,Y]==1 and map[X+5,Y]==0 and map[X+6,Y]==1 and map[X+7,Y]==1 and map[X+8,Y]==1 and map[X+9,Y]==0 and map[X+10,Y]==1:
                    score3 = score3 + 40
            if map[X+7,Y] == map[X+8,Y] == map[X+9,Y]  == map[X+10,Y] == 0:
                if map[X,Y]==1 and map[X+1,Y]==0 and map[X+2,Y]==1 and map[X+3,Y]==1 and map[X+4,Y]==1 and map[X+5,Y]==0 and map[X+6,Y]==1:
                    score3 = score3 + 40

    #评估条件4
    size = 441 #version 1 模块总数
    darkcode = 0   #暗模块总数
    for X in range(0,21):
        for Y in range(0,21):
            if map[X,Y] == 1:
                darkcode += 1
    darkcodepercents = darkcode/size * 100   #暗模块占总模块数百分比
    last_times_by_5 = (int(darkcodepercents / 5)) * 5
    next_times_by_5 = (int(darkcodepercents / 5) + 1) * 5
    last_score = abs(last_times_by_5 - 50)
    next_score = abs(next_times_by_5 - 50)
    score4 = min(last_score/5,next_score/5) * 10

    totalscore = score1 + score2 +score3 + score4

    return totalscore


def getVersionMessage():    #获取版本信息字符串
    MaskString = [1,0,1,0,1,0,0,0,0,0,1,0,0,1,0]
    M = numpy.array(MaskString)
    global maskmode
    if maskmode == 0:
        a = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        b = numpy.array(a)
        return b ^ M
    binmaskmode = bin(maskmode)[2:]
    while(len(binmaskmode) < 3):
        binmaskmode = '0' + binmaskmode
    formatstring = '00' + binmaskmode   # 00为M的纠错位
    GeneratorPolynomial = [1,0,1,0,0,1,1,0,1,1,1]
    new_formatstring = formatstring
    G = numpy.array(GeneratorPolynomial)
    while(len(new_formatstring) < 15):
        new_formatstring = new_formatstring + '0'
    list_formatstring = list(map(int,list(new_formatstring)))
    F = numpy.array(list_formatstring)
    while(1):
        if F[0] == 0:
            F = numpy.delete(F,0)
        else:
            break
    ErrorCorrectString = getErrorCorrectString(F,G)
    list_string = list(map(int,list(formatstring)))
    newF = numpy.array(list_string)
    FinalFormatString = numpy.concatenate((newF,ErrorCorrectString),axis = 0)

    FinalFormatString = FinalFormatString ^ M

    return FinalFormatString

def getErrorCorrectString(F,G):     #获取版本信息的纠错位
    if (len(F)<=10):
        while(len(F)<10):      #补齐到10位返回
            F = numpy.insert(F,0,0)
        return F
    newG = G
    while(len(newG) < len(F)):
        newG = numpy.append(newG,0)
    
    newF = F ^ newG
    while(1):
        if newF[0] == 0:
            newF = numpy.delete(newF,0)
        else:
            break
    
    return getErrorCorrectString(newF,G)

def getFinalQRcodemap(FinalFormatString,map):   #将版本信息填入二维码点阵
    X = 8
    n = 0
    for Y in range(0,9):
        if Y == 6:
            continue
        map[X,Y] = FinalFormatString[n]
        n+=1
    map[X,13] = FinalFormatString[n-1]
    for Y in range(14,21):
        map[X,Y] = FinalFormatString[n]
        n+=1

    n = 0
    Y = 8
    for X in range(20,13,-1):
        map[X,Y] = FinalFormatString[n]
        n+=1
    for X in range(8,-1,-1):
        if X == 6:
            continue
        map[X,Y] = FinalFormatString[n]
        n+=1
    
    return map


def drawFinalQRCode(map):
    n = 30
    x = -500
    y = 300
    turtle.tracer(0,0)
    turtle.speed(11)
    turtle.pensize(2)
    turtle.penup()
    for i in range(21):
        for j in range(21):
            turtle.goto(x + i * n,y - j *n)
            if map[j,i] == 0:
                #continue
                drawblock(n,'white')
            else: 
                drawblock(n,'black')
    turtle.done()

def drawblock(length,fill_color):
    turtle.pendown()
    turtle.begin_fill()
    turtle.fillcolor(fill_color)
    for index in range(4):
        turtle.forward(length)
        turtle.left(90)
    turtle.end_fill()
    turtle.penup()



    



    



    
    
    




# string = input('Please enter a word only in BIGCASE\n')
string = "HELLO WORLD"
Index = getIndex(string)
stringlength = getStringLength(string)
datacode = getDataCode(Index)
finaldatacode = CheckDataCode(stringlength,datacode)  #二进制
M = getMessagePolynomial(finaldatacode)
G = getGeneratorPolynomial()
errorcode = getErrorCorrectionCode(M,G,16)
mixedcodestring = getMixedCode(M,errorcode)
qrcodemap = darwQRcode(mixedcodestring)
finalmap = getMaskCode(qrcodemap)

# drawFinalQRCode(maskcode)
print (maskmode)
drawFinalQRCode(finalmap)
                
    
        
        
    

