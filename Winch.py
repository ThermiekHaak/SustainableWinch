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
    @Part
    def powertrain(self):
        return Powertrain(energy_source = self.energy_source, n_drum = self.drivetrain.numberofdrums,)



    @Part
    def drivetrain(self):
        return Drivetrain(starts_per_hour = self.operation_parameters[0])


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