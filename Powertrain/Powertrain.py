from parapy.core import *
import numpy as np

class Powertrain(Base):
    energy_source = Input('FC')                     # Energy Source for the winch (either FC or BEV)
    n_drum = Input(6)                               # Amount of drums on the winch
    v_max_inverter = Input(600)                     # Maximum voltage of the motor inverter
    grid_power = Input(0)                           # Charging power available from the grid [kW]
    p_profile = Input(np.ones(3000)*8.5e3*110/3.6)  # Power profile from the heaviest glider
    t_between_start = Input(30)                     # Minimum time between two starts of the same set [s]
    cable_length = Input(1000)                      # Length of the cable of the winch [m]
    cable_car_speed = Input(10)                     # Speed the cable car is driving with when driving back to the field
    t_hook_cable = Input(30)                        # Time it takes to hook all the cables to the cable car
    starts_per_day = Input(80)                      # Amount of starts made per flying day
    consecutive_operation = Input(2)                # Amount of consecutive days of operation
    overnight_charging_time = Input(10*3600)        # Amount of time we can charge the winch overnight
    overnight_charging_power = Input(11)            # Charging power available overnight [kW]

    def power_calc(self):
        idle_time_per_set = self.n_drum*self.t_between_start+self.t_hook_cable+self.cable_length/self.cable_car_speed +self.t_hook_cable
        sets_per_day = self.starts_per_day/self.n_drum
        energy_per_set = np.trapz(self.p_profile) * self.n_drum
        FC_power = 0
        H2_mass = 0

        if energy_source == 'BEV':
            charging_per_set = idle_time_per_set*self.grid_power
            net_energy_per_set = energy_per_set-charging_per_set
            energy_per_day = net_energy_per_set*sets_per_day
            overnight_charging_energy = self.overnight_charging_power*self.overnight_charging_time
            BAT_capacity = energy_per_day*self.consecutive_operation-(overnight_charging_energy*self.consecutive_operation-1)
            BAT_power = max(self.p_profile)
            print('Battery System sizing complete:\nBattery capacity: ',BAT_capacity/3600000,' [kWh]\n Battery Power: ',BAT_power,' [kW]')

        else:
            # Size the fuel cell system by taking a certain ratio of the maximum power
            power_ratio = 0.5
            FC_power = power_ratio*max(self.p_profile)
            battery_power_start = self.p_profile-FC_power
            battery_energy_start = np.trapz(battery_power_start)-FC_power*self.t_between_start
            battery_energy_set = self.n_drum*battery_energy_start
            while battery_energy_set < FC_power*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable)
                power_ratio = power_ratio+0.1
                FC_power = power_ratio * max(self.p_profile)
                battery_power_start = self.p_profile - FC_power
                battery_energy_start = np.trapz(battery_power_start) - FC_power * self.t_between_start
                battery_energy_set = self.n_drum * battery_energy_start
            # Apply a safety factor to the battery energy so we make sure we have enough
            BAT_capacity = battery_energy_set/0.8
            BAT_power = max(battery_power_start)
            FC_energy = (idle_time_per_set*self.starts_per_day/self.n_drum+0.01*len(self.p_profile))*FC_power
            H2_energy = FC_energy/self.efficiency
            H2_mass = H2_energy/self.specific_energy_h2*self.consecutive_operation
            print('Fuel cell system sized:\nFC Power: ',FC_power,' [kW]\nHydrogen storage: ',H2_mass,' [kg]\nBattery capacity: ',BAT_capacity/3600000,' [kWh]\nBattery'
                'Power: ',BAT_power/1000,' [kW]')

        return [BAT_power,BAT_capacity,FC_power,H2_mass]

    @Attribute
    def powertrain_sizes(self):
        return power_calc()

    @Part
    def batterypack(self):
        return pass


