class Number:
    def __init__(self,value):
        self.value = value

    def __repr__(self):
        return f"Number({str(float(self.value))})"

    def __add__(self,other):
        return Number(self.value+other.value)

    def __sub__(self,other):
        return Number(self.value-other.value)

    def __mul__(self,other):
        return Number(self.value * other.value)

    def __truediv__(self,other):
        return Number(self.value / other.value)

    def __floordiv__(self,other):
        return Number(self.value // other.value)
    
    def __pow__(self,other):
        return Number(self.value ** other.value)

    def __lt__(self,other):
        return self.value < other.value

    def __le__(self,other):
        return self.value <= other.value

    def __eq__(self,other):
        return self.value == other.value

    def __ne__(self,other):
        return self.value != other.value

    def __gt__(self,other):
        return self.value > other.value

    def __ge__(self,other):
        return self.value >= other.value

    def toInt(self):
        return int(self.value)
 
    def toFloat(self):
        return float(self.value)
    
    def toString(self):
        return str(float(self.value))
