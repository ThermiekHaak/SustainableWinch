from parapy.core import*
from parapy.geom import*
class ElectricalMotor(GeomBase):
    name = Input()
    peakpower = Input()
    continouspower = Input()
    efficiency = Input()
    mass = Input()
    dimensions = Input()

    @Part
    def Cylinder(self):
        return Cylinder(radius = self.dimensions[0], height = self.dimensions[1], position= self.position)

