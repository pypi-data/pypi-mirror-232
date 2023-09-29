from onenonly import maths

class Complex:
    def __init__(self,Re:int|float,Img:int|float):
        self.real = Re
        self.imaginary = Img
    
    def __repr__(self):
        return f"Re({self.real}) Img({self.imaginary})"
    
    def __add__(self,other):
        if not isinstance(other,Complex):
            raise TypeError(f"Unsupported operand type for +: 'Complex' and '{type(other).__name__}'")
        ReSum = self.real + other.real
        ImgSum = self.imaginary + other.imaginary
        return Complex(ReSum,ImgSum)
    
    def __sub__(self,other):
        if not isinstance(other,Complex):
            raise TypeError(f"Unsupported operand type for -: 'Complex' and '{type(other).__name__}'")
        ReSub = self.real - other.real
        ImgSub = self.imaginary - other.imaginary
        return Complex(ReSub,ImgSub)
    
    def __mul__(self,other):
        if not isinstance(other,Complex):
            raise TypeError(f"Unsupported operand type for *: 'Complex' and '{type(other).__name__}'")
        ReMult = (self.real * other.real) - (self.imaginary * other.imaginary)
        ImgMult = (self.real * other.imaginary) - (self.imaginary * other.real)
        return Complex(ReMult,ImgMult)
    
    def __truediv__(self,other):
        if not isinstance(other,Complex):
            raise TypeError(f"Unsupported operand type for /: 'Complex' and '{type(other).__name__}'")
        denominator = other.real ** 2 + other.imaginary ** 2
        ReDiv = (self.real * other.real + self.imaginary * other.imaginary)/denominator
        ImgDiv = (self.imaginary * other.real - self.real * other.imaginary)/denominator
        return Complex(ReDiv,ImgDiv)
    
    def magnitude(self):
        return maths.sqrt(self.real ** 2 + self.imaginary ** 2)
    
    def conjugate(self):
        return Complex(self.real,-self.imaginary)
    
    def toList(self):
        return [self.real,self.imaginary]
    
    def toTuple(self):
        return (self.real,self.imaginary)
