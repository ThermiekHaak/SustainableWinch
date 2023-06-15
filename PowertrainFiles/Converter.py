from parapy.core import *
import numpy as np

class Converter(Base):
    FC_Power = Input(50)        # Power of the fuel cell system [kW]
    max_voltage = Input(600)    # Maximum voltage of the battery pack [V]

    @Attribute
    def dimensions(self):
        return self.dc_dc_select()[0]

    @Attribute
    def mass(self):
        return self.dc_dc_select()[1]


    def dc_dc_select(self):
        #TODO implement integration with SQL database
        return [[3*self.FC_Power,4*self.FC_Power,1*self.FC_Power],0.2*self.FC_Power]

if __name__ == '__main__':
    from parapy.gui import display
    obj = Converter()
    display(obj)