from parapy.core import *
import numpy as np
import pandas as pd
from Glider import Glider
from Winch import Winch

class GlidingOperation(Base):
    starts_per_hour = Input(30)         # Maximum amount of starts the club wants to make in one hour
    starts_per_day = Input(100)         # Maximum amount of starst made per day []
    winch_distance = Input(1000)        # Distance from the winch to the starting glider [m]
    flying_window = Input(8)           # Amount of time the club flies on a day (maximum) [hours]
    consecutive_operation = Input(2)    # Number of days flying after eachother (without refueling)
    overnight_charging_power = Input(11)# Power available to charge overnight (especially for BEV winches) [kW]
    overnight_charging_time = Input(10) # Amount of time available to charge each night [hours]
    grid_power = Input(11)              # Electric power available on the airstrip (used for BEV winches) [KW]
    first_start = Input(10.5)           # Time at which the first start of the day happens [hours]
    charge_start = Input(21)            # Time at which the winch is plugged in the charger [hours]
    t_start2start = Input(30)           # Time between two starts [s]
    t_hook = Input(30)                  # Time it takes to put the cables on the winch unwinding trailer and get them off [s]
    v_cablecar = Input(30/3.6)          # Speed of the unspooling car [m/s]
    csv = Input('DSA_Fleet.csv')



    @Attribute
    def fleet(self):
        return self.load_fleet(self.csv)

    @Attribute
    def op_param(self):
        param = {
            'starts_hour':self.starts_per_hour,
            'starts_day': self.starts_per_day,
            'winch_distance': self.winch_distance,
            'flying_window': self.flying_window,
            'cons_op': self.consecutive_operation,
            'p_charge_on':self.overnight_charging_power,
            't_charge_on':self.overnight_charging_time,
            'p_grid':self.grid_power,
            'start_charge':self.charge_start,
            'first_start':self.first_start,
            'v_cc':  self.v_cablecar,
            'start2start': int(self.t_start2start),
            't_hook':self.t_hook
        }
        return param
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
    def gliders(self):
        # TODO implement return multiple gliders pass down winch_distance and
        # TODO required_altitude
        return Glider(quantify = len(self.fleet), mass = self.fleet.iloc[child.index][1], max_force = self.fleet.iloc[child.index][2],
                      glideratio = self.fleet.iloc[child.index][3], V = self.fleet.iloc[child.index][4]/3.6, label =
                      self.fleet.iloc[child.index][0])



    @Part
    def fuel_cell_winch(self):
        return Winch(energy_source = 'FC',operation_parameters = self.op_param,fleet = self.fleet,P_param =
        self.critical_launch())

    @Part
    def battery_winch(self):
        return Winch(energy_source='BEV', operation_parameters= self.op_param, fleet=self.fleet,P_param =
        self.critical_launch())

    def critical_launch(self):
        p_max = np.zeros(self.gliders.size[-1])
        p_avg = np.zeros(self.gliders.size[-1])
        t_start = np.zeros(self.gliders.size[-1])

        for i in range(self.gliders.size[-1]):
            p_max[i] = self.gliders[i].P_profile['maxPower']
            p_avg[i] = self.gliders[i].P_profile['avgPower']
            t_start[i] = self.gliders[i].P_profile['time']
        energy = p_avg*t_start
        # The powertrain will be sized for the max power and max energy so these are returned
        return [max(p_max)/1e3,p_avg[np.argmax(energy)]/1e3,t_start[np.argmax(energy)]]





if __name__ == '__main__':
    from parapy.gui import display
    obj = GlidingOperation()
    display(obj)




