class Celsius:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "C"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Kelvin):
            other = Celsius(other.value-273.15)
        elif isinstance(other,Fahrenheit):
            other = Celsius((other.value-32)*5/9)
        return Celsius(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Kelvin):
            other = Celsius(other.value-273.15)
        elif isinstance(other,Fahrenheit):
            other = Celsius((other.value-32)*5/9)
        return Celsius(self.value - other.value)
    
    def __gt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value <= other.value
    
    def toKevin(self):
        return Kelvin(self.value+273.15)
    
    def toFahrenheit(self):
        return Fahrenheit((self.value*9/5)+32)


class Kelvin:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "K"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Celsius):
            other = Kelvin(other.value+273.15)
        elif isinstance(other,Fahrenheit):
            other = Kelvin((other.value-32)*5/9+273.15)
        return Kelvin(self.value + other.value)

    def __sub__(self,other):
        if isinstance(other,Celsius):
            other = Kelvin(other.value+273.15)
        elif isinstance(other,Fahrenheit):
            other = Kelvin((other.value-32)*5/9+273.15)
        return Kelvin(self.value - other.value)
    
    def __gt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value <= other.value
    
    def toCelsius(self):
        return Celsius(self.value-273.15)
    
    def toFahrenheit(self):
        return Fahrenheit((self.value-273.15)*9/5+32)
    

class Fahrenheit:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "F"

    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return Fahrenheit(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return Fahrenheit(self.value - other.value)
    
    def __gt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Celsius):
            other = Fahrenheit((other.value*9/5)+32)
        elif isinstance(other,Kelvin):
            other = Fahrenheit((other.value-273.15)*9/5+32)
        return self.value <= other.value
    
    def toKevin(self):
        return Kelvin((self.value-32)*5/9+273.15)
    
    def toCelsius(self):
        return Celsius((self.value-32)*5/9)
    