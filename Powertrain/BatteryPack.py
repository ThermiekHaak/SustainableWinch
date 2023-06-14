from parapy.core import *
import numpy as np


class BatteryPack(Base):
    BAT_power_req = Input(150.)          # Battery power in [kW]
    BAT_energy_req = Input(100.)         # Battery energy in [kWh]
    max_voltage = Input(600.)        # Maximum voltage when the battery is fully charged [V]

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
            # print('increasing capacity for energy purposes')
            n_cell_parallel = n_cell_parallel + 1
            energy = self.cell_capacity*n_cell_parallel*self.cell_nominal_voltage*n_cell_series*3600
        print('First sizing complete battery stats:\nCells in series: ',n_cell_series,'\nCells in parallel: ',
              n_cell_parallel,'\nBattery capacicity:',energy,'\nMoving on to degradation calculations...')
        # TODO Add interface with external tool
        return [n_cell_series, n_cell_parallel]
    def cell_select(self):
        return [4.2,30,3,2.9,3.6,0.045]


if __name__ == '__main__':
    from parapy.gui import display
    obj = BatteryPack()
    display(obj)