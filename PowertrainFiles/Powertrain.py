from parapy.core import *
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as sp
from PowertrainFiles.BatteryPack import BatteryPack
from PowertrainFiles.FuelcellSystem import FuelCellSystem
from PowertrainFiles.H2Tank import H2Tank
from PowertrainFiles.Converter import Converter
from PowertrainFiles.PressureRegulator import PressureRegulator



class Powertrain(Base):
    energy_source = Input('BEV')                     # Energy Source for the winch (either FC or BEV)
    n_drum = Input(6)                               # Amount of drums on the winch
    v_max_inverter = Input(600)                     # Maximum voltage of the motor inverter [V]
    grid_power = Input(11)                           # Charging power available from the grid [kW]
    p_profile = Input(np.ones(3000)*8.5e3*110/3.6)  # Power profile from the heaviest glider
    t_between_start = Input(30)                     # Minimum time between two starts of the same set [s]
    cable_length = Input(1000)                      # Length of the cable of the winch [m]
    cable_car_speed = Input(10)                     # Speed the cable car is driving with when driving back to the field [m/s]
    t_hook_cable = Input(30)                        # Time it takes to hook all the cables to the cable car [s]
    starts_per_day = Input(80)                      # Amount of starts made per flying day
    consecutive_operation = Input(2)                # Amount of consecutive days of operation [days]
    overnight_charging_time = Input(10)             # Amount of time we can charge the winch overnight [hours]
    overnight_charging_power = Input(11)            # Charging power available overnight [kW]
    max_tank_length = Input(5)
    first_start = Input(10.5)                       # Time at which the first winch launch is performed [h]
    charge_start = Input(21)                        # Time at which the winch starts the overnight charge [h]

    # Constants
    efficiency = 0.5                                # Efficiency of the fuel cell system [-]
    specific_energy_h2 = 120e6                      # Available energy in hydrogen per kg of mass [J/kg]

    def power_calc(self):
        idle_time_per_set = self.n_drum*self.t_between_start+self.t_hook_cable+self.cable_length/self.cable_car_speed +self.t_hook_cable
        sets_per_day = self.starts_per_day/self.n_drum
        energy_per_set = np.trapz(self.p_profile)*0.01 * self.n_drum
        max_power = max(self.p_profile)
        FC_power = 0
        H2_mass = 0
        pp_bat = np.zeros(24 * 3600*self.consecutive_operation)
        energy_profile = np.zeros(24*3600*self.consecutive_operation)

        if self.energy_source == 'BEV':
            charging_per_set = idle_time_per_set*self.grid_power*1e3
            net_energy_per_set = energy_per_set-charging_per_set
            energy_per_day = net_energy_per_set*sets_per_day
            overnight_charging_energy = self.overnight_charging_power*1e3*self.overnight_charging_time*3600
            BAT_capacity = energy_per_day*self.consecutive_operation-(overnight_charging_energy*(self.consecutive_operation-1))
            BAT_power =max_power/1e3
            # Resample the power profile:
            powerprofile_func = sp.interp1d(np.arange(0,len(self.p_profile)*0.01,0.01),self.p_profile)
            p_profile_resample = powerprofile_func(np.arange(0,len(self.p_profile)*0.01))
            # Create a power profile for the battery to cope with
            # Start with the first day where the winch is fully charged
            # It is assumed the winch is still fully charged
            # The day will consist of consecutive sets until the amount of starts per day are reached
            n_set = np.ceil(self.starts_per_day/self.n_drum)
            # The first set is done at 10:30
            first_start = int(self.first_start*3600)
            l_start = int(len(self.p_profile)*0.01)
            # Now build a power profile for the first set.
            # TODO: Add method for distributing the sets throughout the day
            for s in range(int(n_set)):
                for i in range(self.n_drum):
                    pp_bat[first_start+i*(l_start+self.t_between_start):first_start+(i+1)*l_start+i*self.t_between_start] = p_profile_resample/1e3
                    pp_bat[first_start+i*l_start+ (i+1)*self.t_between_start:int(first_start+ self.cable_length/
                                                                                 self.cable_car_speed+2*self.t_hook_cable
                                                                                 +(i+1)*(l_start+self.t_between_start))] = -self.grid_power
                first_start = int(first_start+self.n_drum*(l_start+self.t_between_start)+2*self.t_hook_cable+self.cable_length/self.cable_car_speed)
            pp_bat[self.charge_start*3600:(self.charge_start+self.overnight_charging_time)*3600] = -self.overnight_charging_power
            # Now do all the days inbetween the first and second days (if there are any)
            if self.consecutive_operation > 2:
                for d in range(self.consecutive_operation-2):
                    first_start = int(self.first_start * 3600 + (d+1)*24*3600)
                    for s in range(int(n_set)):
                        for i in range(self.n_drum):
                            pp_bat[first_start + i * (l_start + self.t_between_start):first_start + (
                                        i + 1) * l_start + i * self.t_between_start] = p_profile_resample / 1e3
                            pp_bat[first_start + i * l_start + (i + 1) * self.t_between_start:int(
                                first_start + self.cable_length / self.cable_car_speed + 2 * self.t_hook_cable
                                + (i + 1) * (l_start + self.t_between_start))] = -self.grid_power
                        first_start = int(first_start + self.n_drum * (
                                    l_start + self.t_between_start) + 2 * self.t_hook_cable + self.cable_length / self.cable_car_speed)
                    pp_bat[((d+1)*24+self.charge_start) * 3600:((d+1)*24+self.charge_start + self.overnight_charging_time) * 3600] = -self.overnight_charging_power
            # Now construct the final day of the consectutive days
            first_start = int(self.first_start*3600 + (self.consecutive_operation-1)*24*3600)



            # plt.plot(pp_bat[int(10.5*3600):first_start+500])
            # plt.show()
            # With the power profile ready it is time to integrate it to convert it into an energy drawn cycle
            energy_profile = pp_bat.cumsum()
            print('Final value of energy profile: ',self.consecutive_operation*energy_profile/3600,' [kWh]')
            print('Battery System sizing complete:\nBattery capacity: ',BAT_capacity/3600000,' [kWh]\n Battery Power: ',BAT_power,' [kW]')

        else:
            # Size the fuel cell system by taking a certain ratio of the maximum power
            power_ratio = 0.5
            FC_power = power_ratio*max_power/1e3
            battery_power_start = self.p_profile-FC_power*1e3
            battery_energy_start = np.trapz(battery_power_start)*0.01-FC_power*1e3*self.t_between_start
            print('Battery Energy per start: ',battery_energy_start/1e6,' MJ ')
            battery_energy_set = self.n_drum*battery_energy_start
            while battery_energy_set > FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable):
                print(battery_energy_set < FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable))
                power_ratio = power_ratio+0.1
                FC_power = power_ratio * max_power/1e3
                battery_power_start = self.p_profile - FC_power*1e3
                battery_energy_start = np.trapz(battery_power_start)*0.01 - FC_power*1e3 * self.t_between_start
                battery_energy_set = self.n_drum * battery_energy_start
            while battery_energy_set < 0.5*FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable):
                power_ratio = power_ratio - 0.01
                FC_power = power_ratio * max_power / 1e3
                battery_power_start = self.p_profile - FC_power * 1e3
                battery_energy_start = np.trapz(battery_power_start) * 0.01 - FC_power * 1e3 * self.t_between_start
                battery_energy_set = self.n_drum * battery_energy_start
            # Apply a safety factor to the battery energy so we make sure we have enough
            BAT_capacity = battery_energy_set/0.8
            BAT_power = max(battery_power_start)/1e3
            FC_energy = (FC_power*1e3*len(self.p_profile)*0.01+FC_power*1e3*self.t_between_start)*self.starts_per_day + (
                battery_energy_set*sets_per_day)
            H2_energy = FC_energy/self.efficiency
            H2_mass = H2_energy/self.specific_energy_h2*self.consecutive_operation
            print('Fuel cell system sized:\nFC Power: ',FC_power,' [kW]\nHydrogen storage: ',H2_mass,' [kg]\nBattery capacity: ',BAT_capacity/3600000,' [kWh]\nBattery'
                'Power: ',BAT_power,' [kW]')

        return [BAT_power,BAT_capacity,FC_power,H2_mass,energy_profile]

    @Attribute
    def powertrain_sizes(self):
        return self.power_calc()

    @Part
    def battery_pack(self):
        return BatteryPack(BAT_power_req = self.powertrain_sizes[0],
                           BAT_energy_req = self.powertrain_sizes[1],
                           max_voltage = self.v_max_inverter,
                           energy_profile = self.powertrain_sizes[4])

    @Part
    def fc(self):
        return FuelCellSystem(FC_power_required = self.powertrain_sizes[2])

    @Part
    def tanks(self):
        return H2Tank(H2_mass = self.powertrain_sizes[3],
                      max_length = self.max_tank_length)


    @Part
    def converter(self):
        return Converter(FC_Power = self.powertrain_sizes[2],
                         max_voltage = self.v_max_inverter)

    @Part
    def pressure_regulator(self):
        return PressureRegulator(FC_power = self.powertrain_sizes[2])


if __name__ == '__main__':
    from parapy.gui import display
    obj = Powertrain()
    display(obj)