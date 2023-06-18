from parapy.core import *
from parapy.geom import *
import numpy as np


class PressureRegulator(GeomBase):
    FC_power = Input(150)       # Power of the fuel cell system [kW]
    H2_energy_density = 120e6   # Energy present in one kg of hydrogen [J]
    efficiency = 0.5            # Electrical efficiency of the entire system

    @Attribute
    def H2_massflow(self):
        # Calculate the required mass flow needed to supply the fuel cell system with enough hydrogen.
        m_dot = self.FC_power*1e3/(self.efficiency*self.H2_energy_density)
        return m_dot

    @Attribute
    def mass(self):
        return self.pressure_reg_select()['Mass']

    @Attribute
    def dimensions(self):
        return [self.pressure_reg_select()['Length'],self.pressure_reg_select()['Width'],
                self.pressure_reg_select()['Height']]

    @Part
    def geom(self):
        return Box(length = self.dimensions[0],width = self.dimensions[1],height = self.dimensions[2])

    def pressure_reg_select(self):
        PT = {
            'Length':71 ,
            'Width':71,
            'Height': 139.25,
            'Massflow': 0.01115,
            'Mass': 1.8,
        }

        Meatron = {
            'Length': 140,
            'Width': 150,
            'Height': 60,
            'Massflow': 0.0032,
            'Mass': 1.4,
        }

        if self.H2_massflow < 0.0032:
            PR = Meatron
        elif self.H2_massflow < 0.01115:
            PR = PT
        return PT