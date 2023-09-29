class Tesla:
    def __init__(self,value:int|float):
        self.value = value
        self.units = "T"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return Tesla(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return Tesla(self.value - other.value)
    
    def __gt__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Gauss):
            other = Tesla(self.value/10000)
        return self.value <= other.value
    
    def toGauss(self):
        return Gauss(self.value*10000)
    

class Gauss:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "G"

    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return Gauss(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return Gauss(self.value - other.value)
    
    def __gt__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Tesla):
            other = Gauss(other.value/10000)
        return self.value <= other.value
    
    def toTesla(self):
        return Tesla(self.value*10000)
