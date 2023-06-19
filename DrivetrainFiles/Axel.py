from parapy.core import*
from parapy.geom import*
import numpy as np

class Axel(GeomBase):
    torque = Input()
    numberofdrums = Input(2)
    drumwidth = Input(250)
    material = Input()
    position = Input()

    @Attribute
    def lenght(self):
        return (self.numberofdrums * self.drumwidth +  (self.numberofdrums - 1) * 0.5 + .25) * 1000  #drums 50 cm appart + one end of 25 cm for gearing

    @Attribute
    def radius(self): # mean radius
        # Am = self.torque/ 2 / self.wall_thickness / self.material['shearmodules'] # mean area
        # np.sqrt(Am/np.pi)
        return 0.04 * 1000
    @Attribute
    def wall_thickness(self): # TODO if kept constant remove as attribute
        return 0.01 * 1000
    @Attribute
    def mass(self):
        return (2 * np.pi * self.radius * self.wall_thickness * self.lenght) / 1000**2  * self.material['density']

    @Part
    def Cylinder(self):
        return Cylinder(radius = self.radius, height = self.lenght, position= self.position)

