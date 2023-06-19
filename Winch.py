from parapy.core import *
import numpy as np
from PowertrainFiles.Powertrain import Powertrain
from DrivetrainFiles.Drivetrain import Drivetrain
from Other.Truck import Truck
from Other.OperatorCabin import OperatorCabin

class Winch(Base):
    energy_source = Input('FC')         # Energy source the glider winch uses to operate it's electric motor
    operation_parameters = Input()
    fleet = Input()
    P_param = Input()
    profile = Input()
    steel = {"shearmodules": 79.3 * 10**9,
             'density': 7700}
    @Part
    def powertrain(self):
        return Powertrain(energy_source = self.energy_source,op_param = self.operation_parameters,p_max = self.P_param[0],
                          p_avg = self.P_param[1],t_start = self.P_param[2])

    @Part
    def drivetrain(self):
        return Drivetrain(powerprofile = self.profile, system_Voltage = 690, material = self.steel)


    @Part
    def truck(self):
        return Truck()

    @Part
    def operator_cabin(self):
        return OperatorCabin()

if __name__ == '__main__':
    from parapy.gui import display
    obj = Winch()
    display(obj)