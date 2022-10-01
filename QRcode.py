from constant import *
import re
import utils

class QRcode:
    # 0 Numeric mode 
    # 1 Alphanumeric mode 
    # 2 Byte mode 
    # 3 Kanji mode is not supply
    # Extended Channel Interpretation (ECI) mode is not supply
    # Structured Append mode is not supply
    # FNC1 mode is not supply
    NUMERIC_MODE = 0
    ALPHANUMERIC_MODE = 1
    BYTE_MODE = 2
    KANJI_MODE = 3

    def __init__(self, input_data, version=0, ec_level=1):
        self.input_data = input_data
        self.input_data_length = len(str)
        self.version = version # QRcode size
        self.ec_level = ec_level # Error Correction Level 0-L 1-M 2-Q 3-H
        self.encode_mode = self.ALPHANUMERIC_MODE
        self.encoded_data = ""  #encoded data
        
    
    def __set_encode_mode(self):  
        if(self.input_data.isdigit()):
            self.encode_mode = self.NUMERIC_MODE
            return

        alphanumeric_mode_pattern = re.compile(b"^["+ re.escape(ALPHANUMERIC_MODE_STRING) + rb"]*\Z") 
        if(alphanumeric_mode_pattern.match(self.input_data.encode("ISO 8859-1"))):
            self.encode_mode = self.ALPHANUMERIC_MODE
        else:
            self.encode_mode = self.BYTE_MODE

    # 1-40 versions
    def __set_version(self):
        self.version = utils.get_suitable_version(self.encode_mode,self.ec_level, self.input_data_length)    
        return

    def __check_version(self):
        capacities = CAPACITY_TABLE[(self.version - 1) * 4 + self.ec_level]
        max_capacity = capacities[self.encode_mode]
        if(max_capacity < self.input_data_length):
            raise Exception(
                "The version you entered is too small!"
            )
        return

    def __set_mode_indicator(self) -> None:
        if(self.encode_mode == self.NUMERIC_MODE):
            self.encoded_data = "0001"
        elif(self.encode_mode == self.ALPHANUMERIC_MODE):
            self.encoded_data = "0010"
        elif(self.encode_mode == self.BYTE_MODE):
            self.encoded_data = "0100"
        else:
            self.encoded_data = "1000"

    def __set_char_count_indicator(self):
        if(self.version <= 9):
            self.__set_indicator((10,9,8,8))
            return
        if(self.version <= 26):
            self.__set_indicator((12,11,16,10))
            return
        if(self.version <= 40):
            self.__set_indicator((14,13,16,12))
            return

    def __set_indicator(self, char_count_indicator_length_list: tuple) -> None:
        if(self.encode_mode == self.NUMERIC_MODE):
            self.__set_indicator_impl(char_count_indicator_length_list[0])
        elif(self.encode_mode == self.ALPHANUMERIC_MODE):
            self.__set_indicator_impl(char_count_indicator_length_list[1])
        elif(self.encode_mode == self.BYTE_MODE):
            self.__set_indicator_impl(char_count_indicator_length_list[2])
        else:
            self.__set_indicator_impl(char_count_indicator_length_list[3])
            

    def __set_indicator_impl(self, char_count_indicator_length):
        char_count_indicator = bin(self.input_data_length)[2:].zfill(char_count_indicator_length)
        self.encoded_data += char_count_indicator

    def __encode_input_data(self):
        if(self.encode_mode == self.NUMERIC_MODE):
            self.__numeric_mode_encode()
        elif(self.encode_mode == self.ALPHANUMERIC_MODE):
            self.__alphanumeric_mode_encode()
        elif(self.encode_mode == self.BYTE_MODE):
            self.__byte_mode_encode()
        else:
            return
        # else:
        #     self.KanjiModeEncoding()

    def __numeric_mode_encode(self):
        str_list = re.findall(r'/d{3}', self.input_data)
        if(self.input_data_length % 3 == 1):
            str_list.append(self.input_data[-1])
        elif(self.input_data_length % 3 == 2):
            str_list.append(self.input_data[-2:])
        for i in str_list:
            if(i[0] == 0 and i[1] == 0):
                self.encoded_data += bin(int(i))[2:].zfill(4)
            elif(i[0] == 0):
                self.encoded_data += bin(int(i))[2:].zfill(7)
            else:
                self.encoded_data += bin(int(i))[2:].zfill(10)
        return

    def __alphanumeric_mode_encode(self):
        str_list = re.findall(r'.{2}', self.input_data)
        for i in str_list:
            self.encoded_data += bin(ALPHANUMERIC_MODE_MAP[i[0]]*45 + ALPHANUMERIC_MODE_MAP[i[1]])[2:].zfill(11)
        if(self.input_data_length % 2 == 1):
            self.encoded_data += bin(ALPHANUMERIC_MODE_MAP[self.input_data[-1]])[2:].zfill(6)
        return

    def __byte_mode_encode(self):
        for i in self.input_data.encode(encoding="ISO 8859-1"):
            self.encoded_data += bin(i)[2:].zfill(8)

    def __add_pad_bytes_to_data(self):
        # add terminator if necessary
        max_capacity = utils.get_max_capacity(self.version, self.ec_level)
        n = max_capacity - len(self.encoded_data)
        if(n < 0):
            raise Exception("data > maxCapacity")
        elif(n >= 4):
            for i in range(0,4): self.encoded_data += '0'
        else:
            for i in range(0,n): self.encoded_data += '0'
        # Add More 0s to Make the Length a Multiple of 8
        while(len(self.encoded_data) % 8 != 0):
            self.encoded_data += '0'
        # Add Pad Bytes if the String is Still too Short
        flag = True
        while((max_capacity - len(self.encoded_data)) > 0):
            self.encoded_data += '11101100' if flag else '00010001'
            flag = not flag

        return

    def __set_error_correct_codes(self):
        ec_codes = utils.get_error_correct_codes(self.encoded_data, self.version, self.ec_level)
        self.encoded_data = utils.interleave(self.encoded_data, self.version, self.ec_level, ec_codes)
        return

    def __padding_data(self):
        map = utils.get_initialized_map(self.version)
        return utils.padding_data(map, self.encoded_data)

    def __get_masked_map(self, map):
        return utils.get_masked_map(map, self.version, self.ec_level)

    def __draw(self, map):
        utils.draw(map)
        return

    def make(self):
        self.__set_encode_mode()
        if(self.version == 0):
            self.__set_version()
        self.__check_version()
        self.__set_mode_indicator()
        self.__set_char_count_indicator()
        self.__encode_input_data()
        self.__add_pad_bytes_to_data()
        self.__set_error_correct_codes()
        map = self.__padding_data()
        masked_map = self.__get_masked_map(map)
        self.__draw(masked_map)
        

    
    

    

    
        