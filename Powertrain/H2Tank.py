from parapy.core import *
import numpy as np

class H2Tank(Base):
    # Constants:
    rho_H2_350 = 22.4478        # Density of hydrogen at 350 bars
    rho_H2_700 = 37.898         # Density of hydrogen at 700 bars
    CF_sigma = 2.3e9
    rho_CF = 1580               # Density of carbon fiber used for the tank
    rho_lin = 960               # Density of the liner used to line the tank from the inside
    H2_mass = Input(20)         # Hydrogen mass stored in the tanks [kg]
    max_length = Input(5)
    max_diameter = Input(0.4)
    pressure = Input(350)

    # In principle, it is preferred to have one larger volume tank compared to multiple smaller volume tanks especially
    # below ~500 liters. Furthermore, the more round a tank is, the better, however the volume effect seems to be dominant.
    # For now the tanks are assumed to be of the same size
    @Attribute
    def tank_properties(self):
        return self.tank_sizing()

    def tank_sizing(self):
        if self.pressure>350:
            V = self.H2_mass/self.rho_H2_700
        else:
            V = self.H2_mass/self.rho_H2_350
        n_tank = 1
        R_i = self.max_diameter/2*0.90
        l_tank = (V - 4 / 3 * np.pi * (R_i) ** 3) / (np.pi * (R_i) ** 2)/n_tank
        while l_tank > self.max_length-self.max_diameter:
            n_tank = n_tank + 1
            l_tank = (V - 4 / 3 * np.pi * (R_i) ** 3) / (np.pi * (R_i) ** 2) / n_tank
        print('Tank sized:\nVolume: ',V*1000,' [L]\nLength: ',l_tank,' [m]\nMultiplicity: ',n_tank)
        print('Moving on to weight estimation')

        t_tank = (self.pressure * 1e5 * R_i)/(self.CF_sigma/2.25)
        print('Tank thickness: ',t_tank,' [m]')
        t_l = 0.005
        R_0 = t_l+t_tank+R_i
        R_l = R_i+t_l
        #m_comp = self.rho_CF*(np.pi*(R_i+t_tank+t_l)**2*(4/3*(R_i+t_tank+t_l)+l_tank)-np.pi*(R_0-t_tank)**2*(4/3*(R_0-t_tank)+l_tank))
        m_comp = self.rho_CF*(np.pi*R_0**2*(4/3*R_0+l_tank)-np.pi*(4/3*R_l+l_tank)*R_l**2)
        print(m_comp)
        m_liner = self.rho_lin*(np.pi*(R_i+t_l)**2*(4/3*(R_i+t_l)+l_tank)-np.pi*R_i**2*(4/3*R_i+l_tank))
        print(m_liner)
        m_tank = m_comp+m_liner
        print('Tank mass: ',m_tank,' [kg]')
        return [m_tank,n_tank,l_tank,R_0]

if __name__ == '__main__':
    from parapy.gui import display
    obj = H2Tank()
    display(obj)