import numpy as np
import copy
import re

AlphanumericModeMap = {
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




class QRcode:
    __str = ""
    __strLength = 0
    __encodeMode = 1
    __ECLevel = 'M' # Error Correction Level
    __version = 1 # QRcode size
    __data = "" # encoded data

    def __init__(self,str,version=1,ECLevel='M') -> None:
        self.__str = str
        self.__strLength = len(str)
        self.__version = version
        self.__ECLevel = ECLevel
        # if version.capacity < strlength return ERROR
        

    # 0 Numeric mode 
    # 1 Alphanumeric mode 
    # 2 Byte mode 
    # 3 Kanji mode is not supply
    # Extended Channel Interpretation (ECI) mode is not supply
    # Structured Append mode is not supply
    # FNC1 mode is not supply
    def __setEncodeMode(self) -> int:  
        # to do 
        return

    def __setVersion(self) -> int:
        #to do
        return

    def __setModeIndicator(self) -> None:
        if(self.__encodeMode == 0):
            self.__data = "0001"
        elif(self.__encodeMode == 1):
            self.__data = "0010"
        elif(self.__encodeMode == 2):
            self.__data = "0100"
        else:
            self.__data = "1000"

    def __setIndicator(self,CCIndicatorLength) -> None:
        CCIndicator = bin(self.__strLength)[2:].zfill(CCIndicatorLength)
        self.__data += CCIndicator

    def __setCCIndicator(self) -> None: #set character count indicator
        if(self.__version <= 9):
            if(self.__encodeMode == 0): self.setIndicator(10)
            if(self.__encodeMode == 1): self.setIndicator(9)
            if(self.__encodeMode == 2): self.setIndicator(8)
            if(self.__encodeMode == 3): self.setIndicator(8)
        if(self.__version <= 26):
            if(self.__encodeMode == 0): self.setIndicator(12)
            if(self.__encodeMode == 1): self.setIndicator(11)
            if(self.__encodeMode == 2): self.setIndicator(16)
            if(self.__encodeMode == 3): self.setIndicator(10)
        if(self.__version <= 40):
            if(self.__encodeMode == 0): self.setIndicator(14)
            if(self.__encodeMode == 1): self.setIndicator(13)
            if(self.__encodeMode == 2): self.setIndicator(16)
            if(self.__encodeMode == 3): self.setIndicator(12)

    def __encodeInputText(self):
        if(self.__encodeMode == 0):
            self.__NumericModeEncoding()
        elif(self.__encodeMode == 1):
            self.__AlphanumericModeEncoding()
        elif(self.__encodeMode == 2):
            self.__ByteModeEncoding()
        else:
            return
        # else:
        #     self.KanjiModeEncoding()

    def __NumericModeEncoding(self) -> list:
        data = []
        strlist = re.findall(r'/d{3}', self.__str)
        if(self.__strLength % 3 == 1):
            strlist.append(self.__str[-1])
        elif(self.__strLength % 3 == 2):
            strlist.append(self.__str[-2:])
        for i in strlist:
            if(i[0] == 0 and i[1] == 0):
                data.append(bin(int(i))[2:].zfill(4))
            elif(i[0] == 0):
                data.append(bin(int(i))[2:].zfill(7))
            else:
                data.append(bin(int(i))[2:].zfill(10))
        return data

    def __AlphanumericModeEncoding(self) -> list:
        data = []
        strlist = re.findall(r'.{2}', self.__str)
        for i in strlist:
                data.append(
                    bin(AlphanumericModeMap[i[0]]*45 + AlphanumericModeMap[i[1]])[2:].zfill(11)
                )
        if(self.__strLength % 2 == 1):
            data.append(bin(AlphanumericModeMap[self.__str[-1]]).zfill(6))
        return data

    def __ByteModeEncoding(self) -> list:
        data = []
        self.__str.encode(encoding='ISO 8859-1')
        for i in self.__str:
            data.append(bin(i)[2:].zfill(8))

    
    

    

    
        