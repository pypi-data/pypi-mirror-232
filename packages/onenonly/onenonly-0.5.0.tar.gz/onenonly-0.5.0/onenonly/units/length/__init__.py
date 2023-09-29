class Meter:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "m"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return Meter(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(self.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return Meter(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return Meter(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return Meter(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,CentiMeter):
            other = Meter(other.value/100)
        elif isinstance(other,KiloMeter):
            other = Meter(other.value*1000)
        elif isinstance(other,MilliMeter):
            other = Meter(other.value/1000)
        elif isinstance(other,Feet):
            other = Meter(other.value/3.281)
        elif isinstance(other,Inch):
            other = Meter(other.value/39.37)
        elif isinstance(other,Miles):
            other = Meter(other.value*1609)
        return self.value <= other.value
    
    def toCentiMeter(self):
        return CentiMeter(self.value*100)
    
    def toKiloMeter(self):
        return KiloMeter(self.value/1000)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*1000)

    def toFeet(self):
        return Feet(self.value*3.281)
    
    def toInch(self):
        return Inch(self.value*39.37)
    
    def toMiles(self):
        return Miles(self.value/1609)
    

class CentiMeter:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "cm"

    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(other.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return CentiMeter(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return CentiMeter(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(other.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return CentiMeter(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(other.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return CentiMeter(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value > other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = CentiMeter(self.value*100)
        elif isinstance(other,KiloMeter):
            other = CentiMeter(other.value*100000)
        elif isinstance(other,MilliMeter):
            other = CentiMeter(other.value/10)
        elif isinstance(other,Feet):
            other = CentiMeter(other.value*30.48)
        elif isinstance(other,Inch):
            other = CentiMeter(other.value*2.54)
        elif isinstance(other,Miles):
            other = CentiMeter(other.value/160900)
        return self.value <= other.value
    
    def toMeter(self):
        return Meter(self.value/100)
    
    def toKiloMeter(self):
        return KiloMeter(self.value/100000)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*10)
    
    def toFeet(self):
        return Feet(self.value/30.48)
    
    def toInch(self):
        return Inch(self.value/2.54)
    
    def toMiles(self):
        return Miles(self.value*160900)
    

class KiloMeter:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "km"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self, other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return KiloMeter(self.value + other.value)

    def __sub__(self, other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other,CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return KiloMeter(self.value - other.value)

    def __mul__(self, other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other,CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return KiloMeter(self.value * other.value)

    def __truediv__(self,other):
        if isinstance(other, Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other,CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return KiloMeter(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = KiloMeter(other.value/1000)
        elif isinstance(other, CentiMeter):
            other = KiloMeter(other.value/100000)
        elif isinstance(other,MilliMeter):
            other = KiloMeter(other.value/1000000)
        elif isinstance(other,Feet):
            other = KiloMeter(other.value/3281)
        elif isinstance(other,Inch):
            other = KiloMeter(other.value/39370)
        elif isinstance(other,Miles):
            other = KiloMeter(other.value*1.609)
        return self.value <= other.value

    def toMeter(self):
        return Meter(self.value*1000)

    def toCentiMeter(self):
        return CentiMeter(self.value*100000)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*1000000)
    
    def toFeet(self):
        return Feet(self.value*3281)
    
    def toInch(self):
        return Inch(self.value*39370)
    
    def toMiles(self):
        return Miles(self.value/1.609)


class MilliMeter:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "mm"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self, other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return MilliMeter(self.value + other.value)

    def __sub__(self, other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return MilliMeter(self.value - other.value)

    def __mul__(self, other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return MilliMeter(self.value * other.value)

    def __truediv__(self, other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return MilliMeter(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other, Meter):
            other = MilliMeter(other.value*1000)
        elif isinstance(other, CentiMeter):
            other = MilliMeter(other.value*10)
        elif isinstance(other, KiloMeter):
            other = MilliMeter(other.value*1000000)
        elif isinstance(other,Feet):
            other = MilliMeter(other.value*304.8)
        elif isinstance(other,Inch):
            other = MilliMeter(other.value*25.4)
        elif isinstance(other,Miles):
            other = MilliMeter(other.value*1.609e+6)
        return self.value <= other.value

    def toMeter(self):
        return Meter(self.value/1000)

    def toCentiMeter(self):
        return CentiMeter(self.value/10)

    def toKiloMeter(self):
        return KiloMeter(self.value/1000000)
    
    def toFeet(self):
        return Feet(self.value/304.8)
    
    def toInch(self):
        return Inch(self.value/25.4)
    
    def toMiles(self):
        return Miles(self.value/1.609e+6)


class Feet:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "ft"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.280)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return Feet(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.280)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return Feet(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.280)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return Feet(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return Feet(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = Feet(other.value*3.281)
        elif isinstance(other,MilliMeter):
            other = Feet(other.value/304.8)
        elif isinstance(other,KiloMeter):
            other = Feet(other.value*3281)
        elif isinstance(other,CentiMeter):
            other = Feet(other.value/30.48)
        elif isinstance(other,Inch):
            other = Feet(other.value/12)
        elif isinstance(other,Miles):
            other = Feet(other.value*5280)
        return self.value <= other.value
    
    def toMeter(self):
        return Meter(self.value/3.281)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*304.8)
    
    def toCentiMeter(self):
        return CentiMeter(self.value*30.48)
    
    def toKiloMeter(self):
        return KiloMeter(self.value/3281)
    
    def toInch(self):
        return Inch(self.value*12)
    
    def toMiles(self):
        return Miles(self.value/5280)


class Inch:
    def __init__(self,value):
        self.value = value
        self.unit = "inch"
    
    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return Inch(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return Inch(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return Inch(self.value * other.value)

    def __truediv__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return Inch(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = Inch(other.value*39.37)
        elif isinstance(other,KiloMeter):
            other = Inch(other.value*39370)
        elif isinstance(other,CentiMeter):
            other = Inch(other.value/2.54)
        elif isinstance(other,MilliMeter):
            other = Inch(other.value/25.4)
        elif isinstance(other,Feet):
            other = Inch(other.value*12)
        elif isinstance(other,Miles):
            other = Inch(other.value*63360)
        return self.value <= other.value
    
    def toMeter(self):
        return Meter(self.value/39.37)
    
    def toKiloMeter(self):
        return KiloMeter(self.value/39370)
    
    def toCentimeter(self):
        return CentiMeter(self.value*2.54)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*25.4)
    
    def toFeet(self):
        return Feet(self.value/12)
    
    def toMiles(self):
        return Miles(self.value/63360)


class Miles:
    def __init__(self,value):
        self.value = value
        self.unit = "miles"
    
    def __repr__(self):
        return str(float(self.value))
    
    def __add__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return Miles(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return Miles(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return Miles(self.value * other.value)

    def __truediv__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return Miles(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Meter):
            other = Miles(other.value/1609)
        elif isinstance(other,KiloMeter):
            other = Miles(other.value/1.609)
        elif isinstance(other,CentiMeter):
            other = Miles(other.value/160900)
        elif isinstance(other,MilliMeter):
            other = Miles(other.value/1.609e+6)
        elif isinstance(other,Feet):
            other = Miles(other.value/5280)
        elif isinstance(other,Inch):
            other = Miles(other.value/63360)
        return self.value <= other.value
    
    def toMeter(self):
        return Meter(self.value*1609)
    
    def toKiloMeter(self):
        return KiloMeter(self.value*1.609)
    
    def toCentiMeter(self):
        return CentiMeter(self.value*160900)
    
    def toMilliMeter(self):
        return MilliMeter(self.value*1.609e+6)
    
    def toFeet(self):
        return Feet(self.value*5280)
    
    def toInch(self):
        return Inch(self.value*63360)
