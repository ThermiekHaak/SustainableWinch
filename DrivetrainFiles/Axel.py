from parapy.core import*
import numpy as np

class Axel(Base):
    Torque = Input()
    numberofdrums = Input(2)
    drumwidth = Input(0.25)
    material = Input()

    @Attribute
    def lenght(self):
        return self.numberofdrums * self.drumwidth +  (self.numberofdrums - 1) * 0.5 + .25  #drums 50 cm appart + one end of 25 cm for gearing

    @Attribute
    def radius(self): # mean radius
        Am = self.torque/ 2 / self.wall_thickness / self.material['shearmodules'] # mean area
        return np.sqrt(Am/np.pi)
    @Attribute
    def wall_thickness(self): # TODO if kept constant remove as attribute
        return 0.01
    @Attribute
    def mass(self):
        return 2 * np.pi * self.radius * self.wall_thickness * self.lenght * self.material['density']




