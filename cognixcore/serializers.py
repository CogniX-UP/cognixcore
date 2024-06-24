"""A collection of what might prove to be usefull serializers"""

from .base import TypeSerializer, BasicSerializer
from fractions import Fraction

class ComplexSerializer(BasicSerializer):
    
    def __init__(self):
        super().__init__(complex)
    
    def serialize(self, obj: complex) -> dict:
        return {
            'real': obj.real,
            'imag': obj.imag,
        }
    
    def deserialize(self, data) -> complex:
        return complex(real=data['real'], imag=data['imag'])

class FractionSerializer(BasicSerializer):
    
    def __init__(self):
        super().__init__(Fraction)
    
    def serialize(self, obj: Fraction):
        return {
            'num': obj.numerator,
            'denom': obj.denominator,
        }
    
    def deserialize(self, data) -> Fraction:
        return Fraction(
            numerator=data['num'], 
            denominator=data['denom']
        )