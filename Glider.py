from parapy.core import *
import numpy as np

class Glider(Base):
    mass = Input(350)           # Mass of the glider [kg]
    max_force = Input(6000)     # Max force the cable is allowed pull on the glider [kN]
    polar = Input()             # Glider lift-drag polar
    n_starts_year = Input(300)  # Amount of glider starts per year

    @Attribute
    def P_profile(self):
# TODO Implement power profile calculation
        return np.ones(1,3000)*self.max_force*110/3.6
