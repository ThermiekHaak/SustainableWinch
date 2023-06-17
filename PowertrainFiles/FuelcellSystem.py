from parapy.core import *
from parapy.geom import *
import numpy as np

class FuelCellSystem(GeomBase):
    FC_power_required = Input(50)           # Fuel cell power required to drive the winch [kW]

    @Attribute
    def dimensions(self):
        return [self.fc_sys_select()['length'],self.fc_sys_select()['width'],self.fc_sys_select()['height']]

    @Attribute
    def mass(self):
        return self.fc_sys_select()['mass']

    @Part
    def geom(self):
        return Box(multiplicity = self.fc_sys_select()['number'],length = self.fc_sys_select()['length'],
                   width = self.fc_sys_select()['width'], height = self.fc_sys_select()['height'],
                   position = translate(self.position if child.index == 0 else child.previous.position,
                                        'x',self.fc_sys_select()['length']+50))


    def fc_sys_select(self):
        # Create a couple different fuel cell modules
        PC_30 = {
            'Power': 30,
            'length': 665,
            'width': 462,
            'height': 696,
            'mass': 150,
            'min_vol': 105,
            'max_vol': 210,
            'DCDC': False,
            'number': 1
        }

        Zepp_Y50 = {
            'Power': 50,
            'length': 585,
            'width': 445,
            'height': 903,
            'mass': 180,
            'min_vol': 450,
            'max_vol': 750,
            'DCDC': True,
            'number': 1

        }

        Toyota_80 = {
            'Power': 80,
            'length': 890,
            'width': 630,
            'height': 690,
            'mass': 240,
            'min_vol': 400,
            'max_vol': 750,
            'DCDC': True,
            'number': 1
        }

        Horizon_135 = {
            'Power': 135,
            'length': 1200,
            'width': 670,
            'height': 780,
            'mass': 233,
            'min_vol': 400,
            'max_vol': 750,
            'DCDC': True,
            'number': 1
        }


        # With all the fuel cell systems defined we are going to select the correct system based on the fuel cell power
        number = 1
        if self.FC_power_required < 30:
            FC = PC_30
        elif self.FC_power_required < 50:
            FC = Zepp_Y50
        elif self.FC_power_required < 80:
            FC = Toyota_80
        elif self.FC_power_required < 135:
            FC = Horizon_135
        else:
            number = np.ceil(self.FC_power_required/50)
            FC = Zepp_Y50
        return FC