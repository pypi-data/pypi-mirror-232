def isBinary(binary_string):
    binary_string = list(binary_string)
    for i in  range(len(binary_string)):
        if binary_string[i] == "0" or binary_string[i] == "1":
            continue
        else:
            return False
    return True

def int2bin(integer):
    if integer == 0:
        return "0b0"
    elif integer > 0:
        binary_str = ""
        while integer > 0:
            binary_str = str(integer % 2) + binary_str
            integer //= 2
        return "0b"+binary_str
    else:
        binary_str = ""
        integer = abs(integer)
        while integer > 0:
            binary_str = str(integer % 2) + binary_str
            integer //= 2
        return "1b"+binary_str

def bin2int(binary_string):
    if not isBinary(binary_string):
        raise ValueError(f"binary strings must contain 0 or 1 characters")

    result = 0
    for digit in binary_string[2:]:
        if digit == "1":
            result = result*2+1
        elif digit == "0":
            result = result*2
        else:
            raise ValueError("Input is not a binary string")
    return result

def str2bin(text):
    binary = ""
    for char in text:
        ascii_value = ord(char)
        binary_char = bin(ascii_value)[2:].zfill(8)
        binary += binary_char+" "
    return binary

def bin2str(binary_string):
    if not isBinary(binary_string):
        raise ValueError(f"binary strings must contain 0 or 1 characters")

    binary_string = binary_string.replace(" ","")
    binary_segments = [binary_string[i:i+8] for i in range(0,len(binary_string),8)]
    decimal_values = [int(segment,2) for segment in binary_segments]
    result = "".join([chr(value) for value in decimal_values])
    return result

def bin2oct(binary_string):
    if not isBinary(binary_string):
        raise ValueError(f"binary strings must contain 0 or 1 characters")

    while len(binary_string) % 3 != 0:
        binary_string = "0" + binary_string
    binary_to_octal_dict = {
        "000": "0",
        "001": "1",
        "010": "2",
        "011": "3",
        "100": "4",
        "101": "5",
        "110": "6",
        "111": "7"
    }
    octal = ""
    i = 0
    while i < len(binary_string):
        octal += binary_to_octal_dict[binary_string[i:i+3]]
        i += 3
    return octal

def bin2hex(binary_string):
    if not isBinary(binary_string):
        raise ValueError(f"binary strings must contain 0 or 1 characters")
    
    while len(binary_string) % 4 != 0:
        binary_string = "0" + binary_string
    binary_to_hex_dict = {
        "0000": "0",
        "0001": "1",
        "0010": "2",
        "0011": "3",
        "0100": "4",
        "0101": "5",
        "0110": "6",
        "0111": "7",
        "1000": "8",
        "1001": "9",
        "1010": "A",
        "1011": "B",
        "1100": "C",
        "1101": "D",
        "1110": "E",
        "1111": "F"
    }
    hexadecimal = ""
    i = 0
    while i < len(binary_string):
        hexadecimal += binary_to_hex_dict[binary_string[i:i+4]]
        i += 4
    return hexadecimal

def onesComplement(binary_string:str):
    if not isBinary(binary_string):
        raise ValueError(f"binary strings must contain 0 or 1 characters")
    complement = "".join(["1" if bit == "0" else "0" for bit in binary_string])
    return complement

def twosComplement(binary_string:str):
    inverted = "".join("1" if bit == "0" else "0" for bit in binary_string)
    carry = 1
    result = ""
    for bit in reversed(inverted):
        if bit == "1" and carry == 1:
            result = "0" + result
        elif bit == "0" and carry == 1:
            result = "1" + result
            carry = 0
        else:
            result = bit + result
    return result
