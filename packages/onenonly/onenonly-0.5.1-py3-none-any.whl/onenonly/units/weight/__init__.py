class KiloGram:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "kg"
    
    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return KiloGram(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return KiloGram(self.value - other.value)

    def __mul__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return KiloGram(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return str(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Gram):
            other = KiloGram(other.value/1000)
        elif isinstance(other,Pound):
            other = KiloGram(other.value/2.205)
        return self.value <= other.value
    
    def toGram(self):
        return Gram(self.value*1000)
    
    def toPound(self):
        return Pound(self.value*2.205)


class Gram:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "g"

    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return Gram(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return Gram(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return Gram(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return str(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,KiloGram):
            other = Gram(other.value*1000)
        elif isinstance(other,Pound):
            other = Gram(other.value*543.6)
        return self.value <= other.value
    
    def toKiloGram(self):
        return KiloGram(self.value/1000)
    
    def toPound(self):
        return Pound(self.value/453.6)


class Pound:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "lbs"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return Pound(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return Pound(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return Pound(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return str(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,KiloGram):
            other = Pound(other.value*2.205)
        elif isinstance(other,Gram):
            other = Pound(other.value/453.6)
        return self.value <= other.value
    
    def toKiloGram(self):
        return KiloGram(self.value/2.205)
    
    def toGram(self):
        return Gram(self.value*453.6)
