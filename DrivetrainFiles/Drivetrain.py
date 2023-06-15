import numpy as np
from parapy.core import*
#from MotorInverter import MotorInverter
from DrivetrainFiles.Gear import Gear
from DrivetrainFiles.ElectricalMotor import ElectricalMotor
from DrivetrainFiles.Drum import Drum


class Drivetrain(Base):
    powerprofiles: np.ndarray = Input()  # torque-velocity curve cubic spline??
    starts_per_hour: float = Input()

    @Attribute
    def numberofdrums(self):  # TODO Implment number of drums based on starts per hour
        coupling = 30  # [s] average_time of coupling a plane
        tightening = 10 # [s] time to tighten the rope
        launchtime = 30 # [s] average_time from ground to decoupling of the plane
        spoolingin  = 20 # [s] time
        spoolingout_speed = 30 / 3.6 # [m/s] average speed of car pulling the cables to the planes
        winchfieldlenght = 1000 # [m]
        average_startime = 3600/self.starts_per_hour # required average start time to get enough starts per hour
        Constant_handeling_time = coupling + tightening + launchtime + spoolingin

        drums = ((average_startime - (tightening + launchtime + spoolingin)) * (
                    spoolingout_speed / winchfieldlenght)) ** -1
        if average_startime <= Constant_handeling_time or drums > 8:
            print("The amount of starts per hour is unfeasible, the amount of drums will be fixed at TBD") # TODO TBD
            drums = 6
        return drums

    @Attribute
    def minimal_drivetrainrequirements(self):
        # TODO add calculation based on power profiles what the minimal drive_train req are
        requirements = {'max_torque': None,  # max of spline
                        'max_velocity': None,  # max radial cable velocity
                        'peak_power': None,   # power
                        'continous_power': None,  # power to be sustained longer than 3 seconds
                        }
        return requirements

    # @Part
    # def drum(self):
    #     return pass
    #
    # @Part
    # def gear(self):
    #     # TODO implement find req gear ratio
    #     self.motor.eficiencymap
    #     gear_ratio = None
    #     max_velocity = 1000
    #     return Gear()
    #
    # @Part
    # def axel(self):
    #     return pass
    #
    # @Part
    # def motor(self):
    #     return pass
    #
    # @Part
    # def inverter(self):
    #     return pass
