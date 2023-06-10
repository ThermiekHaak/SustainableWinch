from parapy.core import*
class Gear(Base):
    gearratio = Input()
    torque = Input()
    gear_type = Input() # spur, Helical, planetary
    # TODO add statistics for weight and efficiency based on type, torque and speed

    @Attribute
    def mass(self):
        return None

    @Attribute
    def efficiency(self):
        return None

    @Attribute
    def dimensions(self):
        return None
