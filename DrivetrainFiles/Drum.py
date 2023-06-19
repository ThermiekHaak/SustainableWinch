from parapy.core import*
from parapy.geom import*
import numpy as np
class Drum(GeomBase):
    radius: float = Input()   # outer drum radius [m]
    axel_radius = Input()
    width: float = Input()    # width from guard to guard [m]
    material: dict = Input()  # dictionary with material properties
    efficiency: float = Input(0.99)
    position = Input()

    @Attribute
    def mass(self): # TODO check drum design especially the thicknesses and coupling to the main axel
        guard_height = 0.15 # height above drum of the guards preventing cable to run alongside the drum
        guard_thickness = 0.015
        drumwallthickness = 0.02
        axelslotthickness = 0.015
        density = self.material['density']

        # Assuming Mel winch type drums with solid side panals
        volumedrumside = np.pi * ((self.radius + guard_height)**2 - self.axel_radius**2 )  * guard_thickness
        volume_axelslot = self.width * np.pi * ((self.axel_radius + axelslotthickness)**2 - self.axel_radius**2)
        volumedrumcylinder = self.width *  np.pi * (self.radius**2 - (self.radius-drumwallthickness)**2)
        internal_volume = 2 * volumedrumside + volume_axelslot + volumedrumcylinder
        m = internal_volume * density
        return m

    @Part
    def Cylinder(self):
        return Cylinder(radius = self.radius * 1000, height = self.width * 1000, position= self.position)



