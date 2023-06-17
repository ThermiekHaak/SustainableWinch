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
    energy_source = Input('FC')                     # Energy Source for the winch (either FC or BEV)
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
        sets_per_day = np.ceil(self.starts_per_day/self.n_drum)
        energy_per_set = np.trapz(self.p_profile)*0.01 * self.n_drum
        max_power = max(self.p_profile)
        FC_power = 0
        H2_mass = 0


        if self.energy_source == 'BEV':
            charging_per_set = idle_time_per_set*self.grid_power*1e3
            net_energy_per_set = energy_per_set-charging_per_set
            energy_per_day = net_energy_per_set*sets_per_day
            overnight_charging_energy = self.overnight_charging_power*1e3*self.overnight_charging_time*3600
            # Calculate the battery capacity needed and make it 10% bigger so we are sure we can handle all flying days
            BAT_capacity = 1.1*(energy_per_day*self.consecutive_operation-(overnight_charging_energy*
                                                                          (self.consecutive_operation-1)))
            BAT_power =max_power/1e3
            # Resample the power profile:
            powerprofile_func = sp.interp1d(np.arange(0,len(self.p_profile)*0.01,0.01),self.p_profile)
            p_profile_resample = powerprofile_func(np.arange(0,len(self.p_profile)*0.01))
            energy_profile = self.energy_profile(p_profile_resample,FC_power)
            # With the power profile ready it is time to integrate it to convert it into an energy drawn cycle
            # energy_profile = pp_bat.cumsum()
            # energy_profile[energy_profile<0] = 0
            # plt.subplot(2,1,1)
            # plt.plot(t/3600,pp_bat)
            # plt.grid()
            # plt.ylabel('kW delivered')
            # plt.subplot(2,1,2)
            # plt.plot(t/3600,energy_profile/3600)
            # plt.grid()
            # plt.ylabel('Energy used [kWh]')
            # plt.show()
            print('Final value of energy profile: ',max(energy_profile)/3600,' [kWh]')
            print('Battery System sizing complete:\nBattery capacity: ',BAT_capacity/3600000,' [kWh]\n Battery Power: ',BAT_power,' [kW]')

        else:
            # Size the fuel cell system by taking a certain ratio of the maximum power
            power_ratio = 0.5
            FC_power = power_ratio*max_power/1e3
            battery_power_start = self.p_profile-FC_power*1e3
            battery_energy_set = self.n_drum*(np.trapz(battery_power_start)*0.01)- (self.n_drum-1)*FC_power*1e3*self.t_between_start
            print('Battery Energy per set: ',battery_energy_set/1e6,' MJ ')
            while battery_energy_set > FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable):
                print(battery_energy_set - FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable))
                power_ratio = power_ratio+0.0001
                FC_power = power_ratio * max_power/1e3
                battery_power_start = self.p_profile - FC_power*1e3
                battery_energy_set = self.n_drum*(np.trapz(battery_power_start)*0.01)- (self.n_drum-1)*FC_power*1e3*self.t_between_start
            while battery_energy_set < 0.5 * FC_power*1e3*(self.cable_length/self.cable_car_speed+2*self.t_hook_cable):
                power_ratio = power_ratio - 0.01
                FC_power = power_ratio * max_power / 1e3
                battery_power_start = self.p_profile - FC_power * 1e3
                battery_energy_set = self.n_drum*(np.trapz(battery_power_start)*0.01)- (self.n_drum-1)*FC_power*1e3*self.t_between_start
            # Apply a safety factor to the battery energy so we make sure we have enough
            BAT_capacity = battery_energy_set/0.8
            BAT_power = max(battery_power_start)/1e3
            FC_energy = (FC_power*1e3*len(self.p_profile)*0.01+FC_power*1e3*self.t_between_start)*self.starts_per_day + (
                battery_energy_set*sets_per_day)
            H2_energy = FC_energy/self.efficiency
            H2_mass = H2_energy/self.specific_energy_h2*self.consecutive_operation
            # With all the powers set it now becomes time to generate the energy profile of the FC power rig
            # First give the right battery power command.
            powerprofile_func = sp.interp1d(np.arange(0, len(battery_power_start) * 0.01, 0.01), battery_power_start)
            p_profile_resample = powerprofile_func(np.arange(0, len(self.p_profile) * 0.01))
            energy_profile = self.energy_profile(p_profile_resample,FC_power)

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


    def energy_profile(self,p_profile_resample,FC_Power):
        # Create a power profile for the battery to cope with (prepare for a clusterfuck of code :)

        # Define charging powers based on FC or Battery
        if FC_Power > 0:
            charge_power_1 = FC_Power
            charge_power_2 = 0
            pp_bat = np.zeros(24 * 3600 * (self.consecutive_operation))
            energy_profile = np.zeros(24 * 3600 * (self.consecutive_operation))
            t = np.arange((self.consecutive_operation) * 24 * 3600)
        else:
            charge_power_1 = self.grid_power
            charge_power_2 = self.overnight_charging_power
            pp_bat = np.zeros(24 * 3600 * (self.consecutive_operation + 1))
            energy_profile = np.zeros(24 * 3600 * (self.consecutive_operation + 1))
            t = np.arange((self.consecutive_operation + 1) * 24 * 3600)

        # Start with the first day, where the winch is fully charged
        # The day will consist of consecutive sets until the amount of starts per day are reached
        n_set = np.ceil(self.starts_per_day / self.n_drum)

        l_start = int(len(self.p_profile) * 0.01)
        t_between_set = int(self.cable_length/self.cable_car_speed + 2*self.t_hook_cable)
        # Now build a power profile assuming each set is done after eachother
        # TODO: Add method for distributing the sets throughout the day
        for d in range(self.consecutive_operation):
            first_start = int((d*24 + self.first_start) * 3600)
            for s in range(int(n_set)):
                # For each set iterate through the starts
                for i in range(self.n_drum):
                    # Start with the first start taking place at time first_start. That will have the power profile of the start.
                    # Shift the time of the start + time between starts forward in time
                    pp_bat[first_start + i * (l_start + self.t_between_start):first_start + (
                                i + 1) * l_start + i * self.t_between_start] = p_profile_resample / 1e3
                    # Continue (l_start later) with the charging inbetween starts
                    pp_bat[first_start + (i+1) * l_start + i * self.t_between_start:
                           first_start + (i+1)* (l_start+self.t_between_start)] = -charge_power_1
                # After all starts are done charge the battery using the grid power or fuel cell power while the cable car
                # is retrieving the cables.
                pp_bat[first_start+self.n_drum*(l_start+self.t_between_start):
                       first_start+self.n_drum*(l_start+self.t_between_start)+t_between_set] = -charge_power_1
                pp_bat[pp_bat.cumsum() < -2*charge_power_1] = 0
                # Set the time of the next first start to when the cable car has driven back and the cables have been unhooked
                first_start = int(first_start + self.n_drum * (l_start + self.t_between_start) + t_between_set)
            if FC_Power>0:
                # For FC winches add a run to charge the battery back up
                pp_bat[first_start:int(.5* 3600+ first_start)] = -charge_power_1
                pp_bat[pp_bat.cumsum() < -2*charge_power_1] = 0
            else:
                pp_bat[(d*24 + self.charge_start) * 3600:(d*24 + self.charge_start + self.overnight_charging_time) * 3600] = -charge_power_2
        # With the 'gliding' stuff done we need to add a day (or maybe more!) to charge the battery up
        if FC_Power < 1:
            pp_bat[((self.consecutive_operation-1)*24 + self.charge_start + self.overnight_charging_time) * 3600:] = -charge_power_2
            # If the battery is not full after that charging day we charge it even more
            while pp_bat.cumsum()[-1] > 0:
                pp_bat = np.append(pp_bat,np.ones(24*3600)*-charge_power_2)
                t = np.arange(len(pp_bat))

        # With the power profile ready it is time to integrate it to convert it into an energy drawn cycle
        energy_profile = pp_bat.cumsum()
        energy_profile[energy_profile < 0] = 0
        plt.figure('Power&Energy Profile')
        plt.subplot(2, 1, 1)
        plt.plot(t / 3600, pp_bat)
        plt.grid()
        plt.ylabel('kW delivered')
        plt.subplot(2, 1, 2)
        plt.plot(t / 3600, energy_profile / 3600)
        plt.grid()
        plt.ylabel('Energy used [kWh]')
        plt.show()
        return energy_profile




if __name__ == '__main__':
    from parapy.gui import display
    obj = Powertrain()
    display(obj)