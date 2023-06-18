import numpy as np
import scipy as sc
from parapy.core import*
from parapy.geom import *
import OperationParameters
from MotorInverter import MotorInverter
from Gear import Gear
from ElectricalMotor import ElectricalMotor
from Drum import Drum
from Axel import Axel
import OperationParameters as op
from Database.electric_drives import Electrical_engines


class Drivetrain(GeomBase):
    powerprofile = Input()
    system_Voltage = Input(400)
    material = Input()

    @Attribute
    def numberofdrums(self):
        average_time = 3600/self.starts_per_hour # required average start time to get enough starts per hour
        Constant_handeling_time = op.coupling + op.tightening + op.launchtime + op.spoolingin
        drums = ((average_time - Constant_handeling_time) * (op.spoolingout_speed / op.winchfieldlenght)) ** -1

        if average_time <= Constant_handeling_time or drums > 8:
            print("The amount of starts per hour is unfeasible, the amount of drums will be fixed at 6") # TODO TBD
            drums = 6
        return round(drums +1)

    @Attribute
    def mass(self):
        return self.drum.mass + self.gear.mass + self.axel.mass + self.motor.mass + self.inverter.mass

    @Attribute
    def efficiency(self):
        return self.drum.efficiency * self.gear.efficiency * self.motor.efficiency * self.inverter.efficiency

    @Attribute
    def component_selection_and_sizing(self) -> dict:
        feasible_selection = []
        for i in Electrical_engines:  # filter_out engines based on peak power
            if i['peakpower'] >= self.powerprofile['maxPower']:
                feasible_selection.append(i)

        if not feasible_selection:
            raise Exception("electrical_drives db does not contain a option that can provide the peak power")

        gearing = 20
        selected_engine = None
        for i in feasible_selection:
            required_gearing = np.sqrt(
                self.powerprofile['Force'] / i['ratedTorque'] * self.powerprofile['ratedRPM'] / self.powerprofile[
                    'Vmaxf'])  # required gearing to achieve max_force, V, at rated rpm,torque of the engine
            drumradius = self.powerprofile['Force'] / i['ratedTorque'] / required_gearing
            if required_gearing > gearing and drumradius < 1:
                gearing = required_gearing
                selected_engine = i
        if selected_engine:  # TODO
            return {'Gearing': gearing,
                    'Engine': selected_engine,
                    'Drumradius': drumradius}

        raise Exception(
            'The rated Rpm of the engines listed in electrical_drives db do not provide sufficient torque '
            'to maintain a  gearratio larger than 1/20')


    @Part
    def drum(self):
        return Drum(radius = self.component_selection_and_sizing["Drumradius"], axel_radius = self.axel_radius,
                    width = 0.4, material = self.material, quantify = self.numberofdrums )

    @Part
    def gear(self):
        return Gear(self.component_selection_and_sizing['Gearing']) # TODO

    @Part
    def axel(self):
        Torque = self.powerprofile["maxforce"]/self.component_selection_and_sizing["Drumradius"] # Note can't reference to object drum as this creates a reference loop
        return Axel(Torque, self.numberofdrums, self.drum.width, self.material) # TODO

    @Part
    def motor(self):
        name = self.component_selection_and_sizing['Engine']['name']
        peakpower = self.component_selection_and_sizing['Engine']['peakpower']
        continouspower = self.component_selection_and_sizing['Engine']['continouspower']
        efficiency = self.component_selection_and_sizing['Engine']['efficiency']
        mass = self.component_selection_and_sizing['Engine']['mass']
        # dimensions = # TODO add dimensions in the db
        return ElectricalMotor(name = name, peakpower = peakpower, continouspower = continouspower,
                               efficiency = efficiency, mass = mass)

    @Part
    def inverter(self):
        currentdraw = self.powerprofile['maxPower']/self.system_Voltage
        return MotorInverter(maxcurrentdraw = currentdraw, voltage = self.system_Voltage)

if __name__ is "__main__":
    from parapy.gui import display
    obj = Drivetrain
    display(obj)
