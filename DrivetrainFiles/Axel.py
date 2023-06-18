from parapy import*
import numpy as np

class Axel(Base):
    Torque = Input()
    numberofdrums = Input(2)
    drumwidth = Input(0.25)
    material = Input()

    @Atribute
    def lenght(self):
        return self.numberofdrums * self.drumwidth +  (self.numberofdrums - 1) * 0.5 + .25  #drums 50 cm appart + one end of 25 cm for gearing

    @Atribute
    def radius(self):
        Am = self.torque/ 2 / self.wall_thickness / self.material['shearmodules'] # mean area
        return np.sqrt(Am/np.pi)
    @Atribute
    def wall_thickness(self): # TODO if kept constant remove as attribute
        return 0.01
    @Atribute
    def mass(self):
        return np.pi * self.radius**2 * self.lenght * self.material['density']




