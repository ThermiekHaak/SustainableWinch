from parapy.core import *
import numpy as np

class FuelCellSystem(Base):
    FC_power_required = Input(50)           # Fuel cell power required to drive the winch [kW]

    @Attribute
    def dimensions(self):
        return self.fc_sys_select()[0]

    @Attribute
    def mass(self):
        return self.fc_sys_select()[1]

    def fc_sys_select(self):
        # TODO implement integration with SQL database
        return [[3 * self.FC_power_required, 4 * self.FC_power_required, 1 * self.FC_power_required], 0.2 * self.FC_power_required]