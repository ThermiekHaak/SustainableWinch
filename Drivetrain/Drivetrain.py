from typing import Callable

import numpy as np
import scipy as sc
from parapy.core import*
from MotorInverter import MotorInverter
from Gear import Gear
from ElectricalMotor import ElectricalMotor
from Drum import Drum
import OperationParameters as op


class Drivetrain(Base):
    velocityprofile: Callable = Input()  # callable velocity-time function with input t[s] ,output v in [m/s]
    cableforceprofile: Callable = Input()  # Callable Force-time function with input t [s],output force in [N]
    starts_per_hour: float = Input()

    @Attribute
    def numberofdrums(self):
        average_time = 3600/self.starts_per_hour # required average start time to get enough starts per hour
        Constant_handeling_time = op.coupling + op.tightening + op.launchtime + op.spoolingin
        drums = ((average_time - Constant_handeling_time) * (op.spoolingout_speed / op.winchfieldlenght)) ** -1

        if average_time <= Constant_handeling_time or drums > 8:
            print("The amount of starts per hour is unfeasible, the amount of drums will be fixed at TBD") # TODO TBD
            drums = 6
        return round(drums +1)

    @Attribute
    def drivetrainrequirements(self):
        def power(t: float, force_func: Callable, velocity_func: Callable) -> Callable:
            return force_func(t) * velocity_func(t)

        #Finding max power by finding the power interval and doing bisection
        x_0 = 30  # estimate 1 of when the winch start including reeling in is over
        x_1 = 60  # estimate 2 of when the winch start including reeling in is over
        t_max = sc.optimize(power, x_0, fprime=None, args = (self.cableforceprofile, self.velocityprofile), x1 = x_1, tol = 1)
        max_power = -sc.optimize.golden(-1*(power), args =(self.cableforceprofile, self.velocityprofile))
        max_force = -sc.optimize.golden(-1*(self.cableforceprofile))
        max_velo  = -sc.optimize.golden(-1*(self.velocityprofile))
        continous_power  = sc.integrate.quad(power, 0, t_max)[0]/t_max

        requirements = {'max_force':  max_force,  # max of spline
                        'max_velocity': max_velo,  # max radial cable velocity
                        'peak_power': max_power,   # power
                        'continous_power': continous_power,  # power to be sustained longer than 3 seconds
                        }
        return requirements

    @Part
    def drum(self):
        # TODO calculate radius, axel radius, with and material
        radius = .30
        axel_radius = .8
        width = 0.40
        return Drum(radius = radius, axel_radius = axel_radius, width = width,
        material = material, quantify = self.numberofdrums )

    @Part
    def gear(self):
        # TODO implement find req gear ratio
        self.motor.eficiencymap
        gear_ratio = None
        max_velocity =
        return Gear()

    @Part
    def axel(self):
        pass

    @Part
    def motor(self):
        pass

    @Part
    def inverter(self):
        pass
