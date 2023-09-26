"""Модуль содержит классы плоских фигур."""
 
from math import pi, pow
 
 
class Rectangle:
    """Класс Прямоугольник."""
 
    def __init__(self, a, b):
        """Конструктор принимает длину и ширину."""
        self.w = a
        self.h = b
 
    def square(self):
        """Метод для вычисления площади."""
        return round(self.w * self.h, 2)
 
    def perimeter(self):
        """Метод для вычисления периметра"""
        return 2 * (self.w + self.h)
 
 
class Circle:
    """Класс Круг."""
 
    def __init__(self, radius):
        """Конструктор принимает радиус."""
        self.r = radius
 
    def square(self):
        """Метод для вычисления
        площади круга."""
        return round(pi * pow(self.r, 2), 2)
 
    def length(self):
        """Метод для вычисления
        длины окружности."""
        return round(2 * pi * self.r)