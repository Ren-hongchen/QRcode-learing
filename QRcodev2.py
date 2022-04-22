from constant import *
import re
import utils

class QRcode:
    __str = ""
    __strLength = 0
    __encodeMode = 1
    __ECLevel = 1 # Error Correction Level 0 L 1 M 2 Q 3 H
    __version = 1 # QRcode size
    __data = "" # encoded data

    def __init__(self,str,version=0,ECLevel=1) -> None:
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
    def __setEncodeMode(self) -> None:  
        if(self.__str.isdigit()):
            self.__encodeMode = 0

        AlphanumericModePattern = re.compile(b"^["+ re.escape(AlphanumericModeStr) + rb"]*\Z")
        middleStr = self.__str   # avoid modifying self.__str 
        if(AlphanumericModePattern.match(middleStr.encode("ISO 8859-1"))):
            self.__encodeMode = 1
        
        self.__encodeMode = 2

    # 1-40 versions
    def __setVersion(self) -> int:
        self.__version == utils.bisect(self.__encodeMode,self.__ECLevel,self.__strLength)    
        return

    def __checkVersion(self):
        capacities = CapacityTable[(self.__version - 1) * 4 + self.__ECLevel]
        maxcapacity = capacities[self.__encodeMode]
        if(maxcapacity < self.__strLength):
            raise Exception(
                "The version you entered is small!"
            )
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

    def make(self):
        self.__setEncodeMode()
        if(self.__version == 0):
            self.__setVersion()
        self.__checkVersion()
        self.__setModeIndicator()
        

    
    

    

    
        