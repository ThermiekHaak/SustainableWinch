from parapy.core import *
import numpy as np


class BatteryPack(Base):
    BAT_power = Input(150.)          # Battery power in [kW]
    BAT_energy = Input(100.)         # Battery energy in [kWh]
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
    def battery_configuration(self):
        return self.build_bat()
    def build_bat(self):
        # Start with initial sizing of the battery based on power requirements
        n_cell_series = np.floor(self.max_voltage / self.max_cell_voltage)
        n_cell_parallel = np.ceil(self.BAT_power*1000 / (self.max_cell_current * self.min_cell_voltage* n_cell_series))
        energy = self.cell_capacity * n_cell_parallel * self.cell_nominal_voltage * n_cell_series/1000
        while energy < self.BAT_energy:
            print('increasing capacity for energy purposes')
            n_cell_parallel = n_cell_parallel + 1
            energy = self.cell_capacity*n_cell_parallel*self.cell_nominal_voltage*n_cell_series/1000
        print('First sizing complete battery stats:\nCells in series: ',n_cell_series,'\nCells in parallel: ',
              n_cell_parallel,'\nBattery capacicity:',energy,'\nMoving on to degradation calculations...')
        # TODO Add interface with external tool
        return [n_cell_series, n_cell_parallel]
    def cell_select(self):
        return [4.2,30,3,2.9,3.6]


if __name__ == '__main__':
    from parapy.gui import display
    obj = BatteryPack()
    display(obj)