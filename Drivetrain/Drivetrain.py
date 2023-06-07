import numpy as np
from parapy.core import*

class Drivetrain(Base):
    powerprofiles: np.ndarray = Input() # torque-velocity curve cubic spline??
    starts_per_hour: float = Input()

    @Attribute
    def numberofdrums(self): # TODO Implment number of drums based on starts per hour
        return 6

    @Attribute
    def minimal_drivetrainrequirements(self): # TODO add calculation based on power profiles what the minimal drive_train req are
        requirements = {'max_torque': None,  # max of spline
                        'max_velocity': None, # max radial cable velocity
                        'peak_power': None,   # power
                        'continous_power': None, # power to be sustained longer than 3 seconds
                         }
        return requirements

    @Part
    def drum(self):
        pass

    @Part
    def gear(self):
        pass

    @Part
    def axel(self):
        pass

    @Part
    def motor(self):
        pass

    @Part
    def inverter(self):
        pass




