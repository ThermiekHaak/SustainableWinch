from parapy.core import*
class ElectricalMotor(Base):
    required_peakpower = Input()
    required_continouspower = Input()
    required_peaktorque = Input()
    required_maxrpm= Input()

    @Attribute
    def mass(self):
        return None
    @Attribute
    def dimensions(self):
        return

    @Attribute
    def efficiency(self):
        return