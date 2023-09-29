class Array:
    def __init__(self,data):
        self.data = data
    
    def __repr__(self):
        return f"Array({self.data})"
    
    def __getitem__(self,index):
        return self.data[index]
    
    def __setitem__(self,index,value):
        self.data[index] = value
    
    def __add__(self,other=0.0):
        if isinstance(other,int) or isinstance(other,float):
            return [x + other for x in self.data]
        elif isinstance(other,Array):
            if len(self.data) != len(other.data):
                raise ValueError("Arrays must have the same length for addition.")
            return Array([x + y for x,y in zip(self.data,other.data)])
        else:
            raise TypeError(f"Unsupported operand type for +: 'Array' and `{type(other).__name__}`")

    def __sub__(self,other=0.0):
        if isinstance(other,int) or isinstance(other,float):
            return [x - other for x in self.data]
        elif isinstance(other,Array):
            if len(self.data) != len(other.data):
                raise ValueError("Arrays must have the same length for subtraction.")
            return Array([x - y for x,y in zip(self.data,other.data)])
        else:
            raise TypeError(f"Unsupported operand type for -: 'Array' and `{type(other).__name__}`")
    
    def __mul__(self,other=1.0):
        if isinstance(other,int) or isinstance(other,float):
            return [x * other for x in self.data]
        elif isinstance(other,Array):
            if len(self.data) != len(other.data):
                raise ValueError("Arrays must have the same length for multiplication.")
            return Array([x * y for x,y in zip(self.data,other.data)])
        else:
            raise TypeError(f"Unsupported operand type for *: 'Array' and `{type(other).__name__}`")
    
    def __truediv__(self,other=1.0):
        if isinstance(other,int) or isinstance(other,float):
            return [x / other for x in self.data]
        elif isinstance(other,Array):
            if len(self.data) != len(other.data):
                raise ValueError("Arrays must have the same length for division.")
            return Array([x / y for x,y in zip(self.data,other.data)])
        else:
            raise TypeError(f"Unsupported operand type for /: 'Array' and `{type(other).__name__}`")
    
    def __floordiv__(self,other=1.0):
        if isinstance(other,int) or isinstance(other,float):
            return [x // other for x in self.data]
        elif isinstance(other,Array):
            if len(self.data) != len(other.data):
                raise ValueError("Arrays must have the same length for floor division.")
            return Array([x // y for x,y in zip(self.data,other.data)])
        else:
            raise TypeError(f"Unsupported operand type for //: 'Array' and `{type(other).__name__}`")
    
    def __pow__(self,scalar=1.0):
        return Array([x ** scalar for x in self.data])
    
    def at(self,index:int):
        return self.data[index]
    
    def add(self,value):
        self.data.append(value)

    def remove(self,index:int):
        if 0 <= index <= len(self.data)-1:
            del self.data[index]
        else:
            raise IndexError("Index out of range")
    
    def toList(self):
        return self.data
    
    def toTuple(self):
        return tuple(self.data)
    
    def length(self):
        return len(self.data)
