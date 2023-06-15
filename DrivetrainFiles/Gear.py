from parapy.core import*
class Gear(Base):
    gearratio = Input()  # motorpm/axelrpm
    max_torque = Input()
    max_rpm = Input()
    operating_angle = Input(0)  # Angle between motor and axel

    @Attribute
    def gear_type(self):  # TODO implement rule to decide gear type based on ratio, max_torque and max rpm
        gear_type = 'Helical'  # spur, Helical, planetary, bevel
        return gear_type

    @Attribute
    def mass(self):
        # TODO add statistics for weight and efficiency based on type, torque and speed
        return None

    @Attribute
    def efficiency(self):
        return None

    @Attribute
    def dimensions(self):
        return None
