class Bar:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "bar"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return Bar(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return Bar(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return Bar(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return Bar(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Pascal):
            other = Bar(other.value/1e5)
        elif isinstance(other,Torr):
            other = Bar(other.value/750.1)
        elif isinstance(other,Atm):
            other = Bar(other.value*1.013)
        return self.value <= other.value
    
    def toPascal(self):
        return Pascal(self.value*1e5)
    
    def toTorr(self):
        return Torr(self.value*750.1)
    
    def toAtm(self):
        return Atm(self.value/1.013)
    

class Pascal:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "p"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return Bar(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return Bar(self.value + other.value)
    
    def __mul__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return Bar(self.value + other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return Bar(self.value + other.value)
    
    def __gt__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Bar):
            other = Pascal(other.value*1e5)
        elif isinstance(other,Torr):
            other = Pascal(other.value*133.3)
        elif isinstance(other,Atm):
            other = Pascal(other.value*1.013)
        return self.value <= other.value
    
    def toBar(self):
        return Bar(self.value/1e5)
    
    def toTorr(self):
        return Torr(self.value/133.3)
    
    def toAtm(self):
        return Atm(self.value/1.013)
    

class Torr:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "torr"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return Torr(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return Torr(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return Torr(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return Torr(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Bar):
            other = Torr(other.value*750.1)
        elif isinstance(other,Pascal):
            other = Torr(other.value/133.3)
        elif isinstance(other,Atm):
            other = Torr(other.value*760)
        return self.value <= other.value
    
    def toPascal(self):
        return Pascal(self.value*133.3)
    
    def toBar(self):
        return Bar(self.value/750.1)
    
    def toAtm(self):
        return Atm(self.value/760)
    
class Atm:
    def __init__(self,value:int|float):
        self.value = value
        self.unit = "atm"

    def __repr__(self):
        return str(float(self.value))

    def __add__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return Atm(self.value + other.value)
    
    def __sub__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return Atm(self.value - other.value)
    
    def __mul__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return Atm(self.value * other.value)
    
    def __truediv__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return Atm(self.value / other.value)
    
    def __gt__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value > other.value
    
    def __lt__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value < other.value
    
    def __eq__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value == other.value
    
    def __ne__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value != other.value
    
    def __ge__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value >= other.value
    
    def __le__(self,other):
        if isinstance(other,Bar):
            other = Atm(other.value/1.013)
        elif  isinstance(other,Pascal):
            other = Atm(other.value/101300)
        elif isinstance(other,Torr):
            other = Atm(other.value/760)
        return self.value <= other.value
    
    def toPascal(self):
        return Pascal(self.value*101300)
    
    def toBar(self):
        return Bar(self.value*1.013)
    
    def toTorr(self):
        return Torr(self.value*760)
