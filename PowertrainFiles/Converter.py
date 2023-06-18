from parapy.core import *
from parapy.geom import *
import numpy as np

class Converter(GeomBase):
    FC_Power = Input(50)        # Power of the fuel cell system [kW]
    max_voltage = Input(600)    # Maximum voltage of the battery pack [V]

    @Attribute
    def dimensions(self):
        return [self.dc_dc_select()['length'],self.dc_dc_select()['width'],self.dc_dc_select()['height']]

    @Attribute
    def mass(self):
        return [self.dc_dc_select()['mass']]


    @Part
    def geom(self):
        return Box(length = self.dimensions[0],width = self.dimensions[1], height = self.dimensions[2],
                   centered = True, position = translate(self.position,'z',self.dimensions[2]/2))

    def dc_dc_select(self):
        COPEC = {
            'max_out_vol': 700,
            'min_out_vol': 0,
            'max_power': 50,
            'length': 315,
            'width': 118,
            'height':130,
            'mass': 7
        }

        BL = {
            'max_out_vol': 950,
            'min_out_vol': 0,
            'max_power': 250,
            'length': 260,
            'width': 280,
            'height': 80,
            'mass': 10.5
        }

        # Now select the proper converter based on FC power
        if self.FC_Power < 50:
            converter = COPEC
        else:
            converter = BL

        return converter

if __name__ == '__main__':
    from parapy.gui import display
    obj = Converter()
    display(obj)