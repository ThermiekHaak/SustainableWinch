from parapy.core import*
class ElectricalMotor(Base):
    name = Input()
    peakpower = Input()
    continouspower = Input()
    efficiency = Input()
    mass = Input()
    # dimensions = Input() # TODO remove after dimensions are added in db
    # TODO implement geometry and placement

