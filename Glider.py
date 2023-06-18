from parapy.core import *
from parapy.geom import GeomBase
import numpy as np
from numericallaunch import Power_profile

class Glider(GeomBase):
    mass = Input(350)            # Mass of the glider [kg]
    max_force = Input(6000)      # Max force the cable is allowed pull on the glider [kN]
    glideratio = Input(42)       # max L/D
    V = Input(100/3.6)      # speed to fly to have max L/D
    n_starts_year = Input(300)   # Amount of glider starts per year
    winch_distance = Input(1000) # winch distance lenght of the cable
    required_alt = Input(450)    # required winch launch altitude
    cutt_off = Input(80)         # angle in deg between cable and ground when decoupled


    @Attribute
    def P_profile(self):
        return Power_profile(self.winch_distance, self.required_alt,
                             self.cutt_off, self.mass, self.glideratio,
                             self.V, self.max_force)
