from parapy.core import *
from parapy.geom import *
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as sp
from PowertrainFiles.BatteryPack import BatteryPack
from PowertrainFiles.FuelcellSystem import FuelCellSystem
from PowertrainFiles.H2Tank import H2Tank
from PowertrainFiles.Converter import Converter
from PowertrainFiles.PressureRegulator import PressureRegulator



class Powertrain(GeomBase):
    energy_source = Input()                     # Energy Source for the winch (either FC or BEV)
    op_param = Input()
    n_drum = Input(6)                               # Amount of drums on the winch
    v_max_inverter = Input(600)                     # Maximum voltage of the motor inverter [V]
    p_max = Input(150)                              # Maximum power needed during the start [kW]
    p_avg = Input(100)                              # Average power needed during the start [kW]
    t_start = Input(30)                             # Duration of the start [s]
    max_tank_length = Input(5)

    # Constants
    efficiency = 0.5                                # Efficiency of the fuel cell system [-]
    specific_energy_h2 = 120e6                      # Available energy in hydrogen per kg of mass [J/kg]

    def power_calc(self):
        sets_per_day = np.ceil(self.op_param['starts_day']/self.n_drum)
        energy_per_set = self.p_avg*1e3*self.t_start* self.n_drum
        FC_power = 0
        H2_mass = 0


        if self.energy_source == 'BEV':
            charging_per_set = (self.n_drum-1)*self.op_param['start2start']*self.op_param['p_grid']
            net_energy_per_set = energy_per_set-charging_per_set
            energy_per_day = (net_energy_per_set -(2*self.op_param['t_hook']+self.op_param['winch_distance']/self.op_param['v_cc'])*
                              self.op_param['p_grid'])*sets_per_day
            overnight_charging_energy = self.op_param['p_charge_on']*1e3*self.op_param['t_charge_on']*3600
            # Calculate the battery capacity needed
            BAT_capacity = energy_per_day*self.op_param['cons_op']-(overnight_charging_energy*
                                                                          (self.op_param['cons_op']-1))
            BAT_power = self.p_max
            # Resample the power profile:
            energy_profile = self.energy_profile(FC_power)
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
            power_ratio = 0.3
            FC_power = power_ratio*self.p_avg               # Fuel cell power in [kW]
            battery_power_start = (self.p_avg-FC_power)*1e3 # Battery Power in [W]
            battery_energy_set = self.n_drum*(battery_power_start*self.t_start)- (self.n_drum-1)*FC_power*1e3*self.op_param['start2start']
            print('Battery Energy per set: ',battery_energy_set/3.6e6,' kWh ')
            # while battery_energy_set > FC_power*1e3*(self.op_param['winch_distance']/self.op_param['v_cc']+2*self.op_param['t_hook']):
            #     #print(battery_energy_set - FC_power*1e3*(self.op_param['winch_distance']/self.op_param['v_cc']+2*self.op_param['t_hook']))
            #     power_ratio = power_ratio+0.0001
            #     FC_power = power_ratio * self.p_avg
            #     battery_power_start = self.p_avg - FC_power * 1e3
            #     battery_energy_set = self.n_drum * (battery_power_start * self.t_start) - (
            #                 self.n_drum - 1) * FC_power * 1e3 * self.op_param['start2start']
            # while battery_energy_set <  FC_power*1e3*(self.op_param['winch_distance']/self.op_param['v_cc']+2*self.op_param['t_hook']):
            #     power_ratio = power_ratio - 0.01
            #     FC_power = power_ratio * self.p_avg
            #     battery_power_start = self.p_avg - FC_power * 1e3
            #     battery_energy_set = self.n_drum * (battery_power_start * self.t_start) - (
            #                 self.n_drum - 1) * FC_power * 1e3 * self.op_param['start2start']
            # Apply a safety factor to the battery energy, so we make sure we have enough
            BAT_capacity = battery_energy_set/0.8
            BAT_power = self.p_max-FC_power
            FC_energy = (FC_power*1e3*self.t_start+FC_power*1e3*self.op_param['start2start'])*self.op_param['starts_day'] + (
                battery_energy_set*sets_per_day)
            H2_energy = FC_energy/self.efficiency
            H2_mass = H2_energy/self.specific_energy_h2*self.op_param['cons_op']
            # With all the powers set it now becomes time to generate the energy profile of the FC power rig
            # First give the right battery power command.
            energy_profile = self.energy_profile(FC_power)

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
                           energy_profile = self.powertrain_sizes[4],
                           position = translate(self.position, 'z',-30,'y',6060,'x',1200))


    @Part
    def fc(self):
        return FuelCellSystem(quantify = 0 if self.energy_source == 'BEV' else 1, hidden = True
        if self.energy_source == 'BEV' else False, FC_power_required = self.powertrain_sizes[2],
                              position = translate(self.position, 'z',30,'y',7000,'x',1200))

    @Part
    def tanks(self):
        return H2Tank(quantify = 0 if self.energy_source == 'BEV' else 1, hidden = True
        if self.energy_source == 'BEV' else False, H2_mass = self.powertrain_sizes[3],
                      max_length = self.max_tank_length,position = translate(self.position, 'z',30,'y',6060,'x',1200))


    @Part
    def converter(self):
        return Converter(quantify = 0 if self.energy_source == 'BEV' else 1, hidden = True
        if self.energy_source == 'BEV' else False, FC_Power = self.powertrain_sizes[2],
                         max_voltage = self.v_max_inverter)

    @Part(in_tree= False if energy_source=='BEV'else True)
    def pressure_regulator(self):
        return PressureRegulator(quantify = 0 if self.energy_source == 'BEV' else 1, hidden = True
        if self.energy_source == 'BEV' else False ,FC_power = self.powertrain_sizes[2])


    def energy_profile(self,FC_Power):
        # Create a power profile for the battery to cope with (prepare for a clusterfuck of code :)

        # Define charging powers based on FC or Battery
        if FC_Power > 0:
            charge_power_1 = FC_Power
            charge_power_2 = 0
            pp_bat = np.zeros(24 * 3600 * (self.op_param['cons_op']))
            energy_profile = np.zeros(24 * 3600 * (self.op_param['cons_op']))
            t = np.arange((self.op_param['cons_op']) * 24 * 3600)
            p_bat = self.p_avg-FC_Power
        else:
            charge_power_1 = self.op_param['p_grid']
            charge_power_2 = self.op_param['p_charge_on']
            pp_bat = np.zeros(24 * 3600 * (self.op_param['cons_op'] + 1))
            energy_profile = np.zeros(24 * 3600 * (self.op_param['cons_op'] + 1))
            t = np.arange((self.op_param['cons_op'] + 1) * 24 * 3600)
            p_bat = self.p_avg

        # Start with the first day, where the winch is fully charged
        # The day will consist of consecutive sets until the amount of starts per day are reached
        n_set = np.ceil(self.op_param['starts_day'] / self.n_drum)

        l_start = int(np.ceil(self.t_start))
        t_start2start = int(np.ceil(self.op_param['start2start']))
        t_between_set = int(self.op_param['winch_distance']/self.op_param['v_cc'] + 2*self.op_param['t_hook'])
        # Now build a power profile assuming each set is done after eachother
        # TODO: Add method for distributing the sets throughout the day
        for d in range(self.op_param['cons_op']):
            first_start = int((d*24 + self.op_param['first_start']) * 3600)
            for s in range(int(n_set)):
                # For each set iterate through the starts
                for i in range(self.n_drum):
                    # Start with the first start taking place at time first_start. That will have the power profile of the start.
                    # Shift the time of the start + time between starts forward in time
                    pp_bat[first_start + i * (l_start + t_start2start):first_start + (
                                i + 1) * l_start + i * t_start2start] = p_bat
                    # Continue (l_start later) with the charging inbetween starts
                    pp_bat[first_start + (i+1) * l_start + i * t_start2start:
                           first_start + (i+1)* (l_start+t_start2start)] = -charge_power_1
                # After all starts are done charge the battery using the grid power or fuel cell power while the cable car
                # is retrieving the cables.
                pp_bat[first_start+self.n_drum*(l_start+t_start2start):
                       first_start+self.n_drum*(l_start+t_start2start)+t_between_set] = -charge_power_1
                # Reset the power to zero if the battery is already full
                pp_bat[pp_bat.cumsum() < -2*charge_power_1] = 0
                # Set the time of the next first start to when the cable car has driven back and the cables have been unhooked
                first_start = int(first_start + self.n_drum * (l_start + t_start2start) + t_between_set)
            if FC_Power>0:
                # For FC winches add a run to charge the battery back up
                pp_bat[first_start:int(2* 3600+ first_start)] = -charge_power_1
                pp_bat[pp_bat.cumsum() < -2*charge_power_1] = 0
            else:
                pp_bat[(d*24 + self.op_param['start_charge']) * 3600:(d*24 + self.op_param['start_charge'] + self.op_param['t_charge_on']) * 3600] = -charge_power_2
        # With the 'gliding' stuff done we need to add a day (or maybe more!) to charge the battery up
        if FC_Power < 1:
            pp_bat[((self.op_param['cons_op']-1)*24 + self.op_param['start_charge'] + self.op_param['t_charge_on']) * 3600:] = -charge_power_2
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