from constant import *
import re
import utils
import numpy

class QRcode:
    __str = ""
    __strLength = 0
    __encodeMode = 1
    __ECLevel = 1 # Error Correction Level 0-L 1-M 2-Q 3-H
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
            return

        AlphanumericModePattern = re.compile(b"^["+ re.escape(AlphanumericModeStr) + rb"]*\Z") 
        if(AlphanumericModePattern.match(self.__str.encode("ISO 8859-1"))):
            self.__encodeMode = 1
        else:
            self.__encodeMode = 2

    # 1-40 versions
    def __setVersion(self) -> int:
        self.__version = utils.bisect(self.__encodeMode,self.__ECLevel,self.__strLength)    
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
            if(self.__encodeMode == 0): self.__setIndicator(10)
            elif(self.__encodeMode == 1): self.__setIndicator(9)  
            elif(self.__encodeMode == 2): self.__setIndicator(8)  
            elif(self.__encodeMode == 3): self.__setIndicator(8)
            return
        if(self.__version <= 26):
            if(self.__encodeMode == 0): self.__setIndicator(12)
            elif(self.__encodeMode == 1): self.__setIndicator(11)
            elif(self.__encodeMode == 2): self.__setIndicator(16)
            elif(self.__encodeMode == 3): self.__setIndicator(10)
            return
        if(self.__version <= 40):
            if(self.__encodeMode == 0): self.__setIndicator(14)
            elif(self.__encodeMode == 1): self.__setIndicator(13)
            elif(self.__encodeMode == 2): self.__setIndicator(16)
            elif(self.__encodeMode == 3): self.__setIndicator(12)
            return

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

    def __NumericModeEncoding(self):
        strlist = re.findall(r'/d{3}', self.__str)
        if(self.__strLength % 3 == 1):
            strlist.append(self.__str[-1])
        elif(self.__strLength % 3 == 2):
            strlist.append(self.__str[-2:])
        for i in strlist:
            if(i[0] == 0 and i[1] == 0):
                self.__data += bin(int(i))[2:].zfill(4)
            elif(i[0] == 0):
                self.__data += bin(int(i))[2:].zfill(7)
            else:
                self.__data += bin(int(i))[2:].zfill(10)
        return

    def __AlphanumericModeEncoding(self):
        strlist = re.findall(r'.{2}', self.__str)
        for i in strlist:
            self.__data += bin(AlphanumericModeMap[i[0]]*45 + AlphanumericModeMap[i[1]])[2:].zfill(11)
        if(self.__strLength % 2 == 1):
            self.__data += bin(AlphanumericModeMap[self.__str[-1]])[2:].zfill(6)
        return

    def __ByteModeEncoding(self):
        for i in self.__str.encode(encoding="ISO 8859-1"):
            self.__data += bin(i)[2:].zfill(8)

    def __addPadBytestoData(self):
        # add terminator if necessary
        maxCapacity = utils.getMaxCapacity(self.__version, self.__ECLevel)
        n = maxCapacity - len(self.__data)
        if(n < 0):
            raise Exception("data > maxCapacity")
        elif(n >= 4):
            for i in range(0,4): self.__data += '0'
        else:
            for i in range(0,n): self.__data += '0'
        # Add More 0s to Make the Length a Multiple of 8
        for i in range(0,(8 - (len(self.__data) % 8))):
            self.__data += '0'
        # Add Pad Bytes if the String is Still too Short
        flag = True
        while((maxCapacity - len(self.__data)) > 0):
            if(flag): self.__data += '11101100'
            else: self.__data += '00010001'
            flag = not flag

        return

    def __setErrorCorrectCodes(self):
        eccodes = utils.getErrorCorrectCodes(self.__data,self.__version,self.__ECLevel)
        self.__data = utils.interleave(self.__data,self.__version,self.__ECLevel,eccodes)
        return

    def __paddingData(self):
        map = utils.getInitializedMap(self.__version)
        return utils.paddingData(map,self.__data)

    def __getMaskedMap(self,map):
        return utils.getMaskedMap(map,self.__version,self.__ECLevel)

    def __draw(self,map):
        utils.draw(map)
        return

    def make(self):
        self.__setEncodeMode()
        if(self.__version == 0):
            self.__setVersion()
        self.__checkVersion()
        self.__setModeIndicator()
        self.__setCCIndicator()
        self.__encodeInputText()
        self.__addPadBytestoData()
        self.__setErrorCorrectCodes()
        map = self.__paddingData()
        maskedMap = self.__getMaskedMap(map)
        self.__draw(maskedMap)
        

    
    

    

    
        