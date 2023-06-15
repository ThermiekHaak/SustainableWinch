from parapy.core import *
import numpy as np
import pandas as pd
from Glider import Glider
from Winch import Winch

class GlidingOperation(Base):
    starts_per_hour = Input(30)         # Maximum amount of starts the club wants to make in one hour
    winch_distance = Input(1000)        # Distance from the winch to the starting glider [m]
    flying_window = Input(10)           # Amount of time the club flies on a day (maximum) [hours]
    consecutive_operation = Input(2)    # Number of days flying after eachother (without refueling)
    overnight_charging_power = Input(11)# Power available to charge overnight (especially for BEV winches)
    overnight_charging_time = Input(10) # Amount of time available to charge each night
    csv = Input('DSA_Fleet.csv')
    p_profile = np.ones(3000)*8.5e3*110/3.6


    @Attribute
    def fleet(self):
        return self.load_fleet(self.csv)
    # Methods
    def load_fleet(self,csv):
        # Function that returns a dataframe including the fleet of the club with for each glider:
        # 1. The name of the model
        # 2. The mass of the glider
        # 3. The maximum cable force allowed on the glider
        # 4. Three points to describe the sink vs speed graph
        fleet = pd.read_csv(csv)
        models = fleet['Name'].to_list()
        print(models)
        print(fleet)
        return fleet

    # for i in range(len(fleet)):
    #     @Part
    #     def gliders(self,fleet):
    #         return Glider(mass = self.fleet[self.name]['Mass [kg]'])


    @Part
    def fuel_cell_winch(self):
        return Winch(energy_source = 'FC',operation_parameters =
                     [self.starts_per_hour,self.winch_distance,self.flying_window,self.consecutive_operation,
                      self.overnight_charging_power,self.overnight_charging_time],fleet = self.fleet,
                     power_profile = self.p_profile
                     )

    @Part
    def battery_winch(self):
        return Winch(energy_source='BEV', operation_parameters=
        [self.starts_per_hour, self.winch_distance, self.flying_window, self.consecutive_operation,
         self.overnight_charging_power, self.overnight_charging_time], fleet=self.fleet,
                     power_profile=self.p_profile
                     )

if __name__ == '__main__':
    from parapy.gui import display
    obj = GlidingOperation()
    display(obj)




