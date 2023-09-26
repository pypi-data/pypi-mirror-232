from math import pi, pow
 
 
class Cuboid:
    def __init__(self, a, b, c):
        self.length = a
        self.width = b
        self.height = c
 
    def S(self):
        sq = 2 * (self.length * self.width +
                  self.length * self.height +
                  self.width * self.height)
        return round(sq, 2)
 
    def V(self):
        v = self.length * self.width * self.height
        return round(v, 2)
 
 
class Ball:
    def __init__(self, radius):
        self.r = radius
 
    def S(self):
        s = 4 * pi * pow(self.r, 2)
        return round(s, 2)
 
    def V(self):
        v = (4 / 3) * pi * pow(self.r, 3)
        return round(v, 2)