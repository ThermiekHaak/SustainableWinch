from parapy.core import *
import numpy as np

class PressureRegulator(Base):
    FC_power = Input(150)       # Power of the fuel cell system
    H2_energy_density = 120e6   # Energy present in one kg of hydrogen [J]
    efficiency = 0.5            # Electrical efficiency of the entire system

    @Attribute
    def H2_massflow(self):
        # Calculate the required massflow needed to supply the fuel cell system with enough hydrogen.
        m_dot = self.FC_power*1e3/(self.efficiency*self.H2_energy_density)

    @Attribute
    def mass(self):
        return pressure_reg_select()[0]

    @Attribute
    def dimensions(self):
        return pressure_reg_select()[1]


    def pressure_reg_select(self):
        return [500*self.H2_massflow,[0.02,0.02,0.02]]