from parapy.core import *
import numpy as np
import matplotlib.pyplot as plt
from BLAST.python.lfp_gr_SonyMurata3Ah_2018 import Lfp_Gr_SonyMurata3Ah_Battery
from tqdm import tqdm

class BatteryPack(Base):
    BAT_power_req = Input(150.)          # Battery power in [kW]
    BAT_energy_req = Input(100.)         # Battery energy in [J]
    max_voltage = Input(600.)        # Maximum voltage when the battery is fully charged [V]
    energy_profile = Input()
    gliding_weeks = Input(35)

    @Attribute
    def max_cell_voltage(self):
        return self.cell_select()[0]

    @Attribute
    def min_cell_voltage(self):
        return self.cell_select()[3]

    @Attribute
    def cell_nominal_voltage(self):
        return self.cell_select()[4]

    @Attribute
    def max_cell_current(self):
        return self.cell_select()[1]

    @Attribute
    def cell_capacity(self):
        return self.cell_select()[2]


    @Attribute
    def cell_mass(self):
        return self.cell_select()[5]

    @Attribute
    def battery_configuration(self):
        return self.build_bat()

    @Attribute
    def battery_capacity(self):             # Battery capacity in kWh
        return self.battery_configuration[1]*self.battery_configuration[0]*self.cell_nominal_voltage*self.cell_capacity

    @Attribute
    def battery_mass(self):
        return self.battery_configuration[0]*self.battery_configuration[1]*self.cell_mass

    def build_bat(self):
        # Start with initial sizing of the battery based on power requirements
        n_cell_series = np.floor(self.max_voltage / self.max_cell_voltage)
        n_cell_parallel = np.ceil(self.BAT_power_req*1000 / (self.max_cell_current * self.min_cell_voltage*n_cell_series))
        energy = self.cell_capacity * n_cell_parallel * self.cell_nominal_voltage * n_cell_series*3600
        while energy < self.BAT_energy_req:
            n_cell_parallel = n_cell_parallel + 1
            energy = self.cell_capacity*n_cell_parallel*self.cell_nominal_voltage*n_cell_series*3600
        print('First sizing complete battery stats:\nCells in series: ',n_cell_series,'\nCells in parallel: ',
              n_cell_parallel,'\nBattery capacicity:',energy,'\nMoving on to degradation calculations...')
        # TODO Add interface with external tool
        remaining_capacity = self.cell_deg(energy,4)
        while remaining_capacity < 0.8:
            n_cell_parallel = n_cell_parallel + 5
            energy = self.cell_capacity * n_cell_parallel * self.cell_nominal_voltage * n_cell_series * 3600
            remaining_capacity = self.cell_deg(energy,10)

        return [n_cell_series, n_cell_parallel]
    def cell_select(self):
        return [4.2,30,3,2.9,3.6,0.045]


    def cell_deg(self,energy,years):
        hours = years * 365 * 24
        seconds = hours * 3600
        t_hours = np.arange(hours + 1)
        t_seconds = np.arange(seconds + 1)
        gliding_week = np.zeros(7 * 24 * 3600)
        soc_gliding = 1 - self.energy_profile * 1e3 / energy
        plt.figure('Gliding days SoC')
        plt.plot(np.arange(len(soc_gliding)) / (24 * 3600), soc_gliding)
        plt.grid()
        plt.xlabel('time [days]')
        plt.ylabel('State of Charge [-]')
        # With the initial battery sized it is time to calculate the degradation of the cells over the period of
        # 10 flying seasons. First make a week of flying, start with the amount of days that are not flown.
        # Here we assume the batteries are stored fully charged.
        T = 20 * np.ones(len(t_seconds))
        soc_non_gliding = np.ones((7 * 24 * 3600 - len(soc_gliding)))
        gliding_week[:len(soc_non_gliding)] = soc_non_gliding
        gliding_week[len(soc_non_gliding):] = soc_gliding
        # Assuming each season is consisting of weeks with the same amount of starts on each flying day and the same
        # amount of flying weeks per year (about 35)
        non_gliding_weeks = 52 - self.gliding_weeks
        soc_life = np.zeros(len(t_seconds))
        for y in range(years):
            for i in range(52):
                if i < np.ceil(non_gliding_weeks / 2):
                    soc_life[(i * 7 + y * 365) * 24 * 3600:((i + 1) * 7 + y * 365) * 24 * 3600] = 1
                elif i < np.ceil(non_gliding_weeks / 2) + self.gliding_weeks:
                    soc_life[(i * 7 + y * 365) * 24 * 3600:((i + 1) * 7 + y * 365) * 24 * 3600] = gliding_week
                else:
                    soc_life[(i * 7 + y * 365) * 24 * 3600:((i + 1) * 7 + y * 365+1) * 24 * 3600] = 1
        # With one year defined we can check the degradation in one year
        plt.plot(t_seconds/(24*3600),soc_life)
        plt.xlim((1160,1180))
        plt.show()


        cell = Lfp_Gr_SonyMurata3Ah_Battery()
        t_days = np.arange(365 * years)
        for day in tqdm(t_days):
            hour_start = day * 24 * 3600
            hour_end = ((day + 1) * 24 + 1) * 3600
            cell.update_battery_state(t_secs=t_seconds[hour_start:hour_end], soc=soc_life[hour_start:hour_end],
                                      T_celsius=T[hour_start:hour_end])
        print('Remaining capacity after ', years, ' years: ', cell.outputs['q'][-1])
        return cell.outputs['q'][-1]


if __name__ == '__main__':
    from parapy.gui import display
    obj = BatteryPack()
    display(obj)