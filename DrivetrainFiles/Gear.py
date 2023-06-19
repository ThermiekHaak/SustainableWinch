from parapy.core import*
from parapy.geom import*
class Gear(GeomBase): #TODO decide how to determine/estimate stuff
    gearratio = Input()  # motorpm/axelrpm
    max_torque = Input(500)
    max_rpm = Input(5000)
    efficiency = Input(.95)

    @Attribute
    def mass(self):
        m = 2
        return m

