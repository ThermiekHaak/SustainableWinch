from parapy.core import*
class Gear(Base): #TODO decide how to determine/estimate stuff
    gearratio = Input()  # motorpm/axelrpm
    max_torque = Input()
    max_rpm = Input()
    efficiency = Input(.95)

    @Attribute
    def mass(self):
        m = 2
        return m

