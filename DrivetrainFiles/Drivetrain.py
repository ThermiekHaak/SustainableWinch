import numpy as np
import scipy as sc
from parapy.core import*
from parapy.geom import *
import OperationParameters
from .MotorInverter import MotorInverter
from .Gear import Gear
from .ElectricalMotor import ElectricalMotor
from .Drum import Drum
from .Axel import Axel
import OperationParameters as op
from Database.electric_drives import Electrical_engines


class Drivetrain(GeomBase):
    powerprofile = Input()
    system_Voltage = Input(400)
    material = Input()
    starts_per_hour = Input(20)

    # @Attribute
    # def peakpower(self):
    #     """max(p_max)/1e3,p_avg[np.argmax(energy)]/1e3,t_start[np.argmax(energy)]"""
    #     return self.powerprofile[0] * 10**3
    #
    # @Attribute
    # def continouspower(self):
    #     """max(p_max)/1e3,p_avg[np.argmax(energy)]/1e3,t_start[np.argmax(energy)]"""
    #     return self.powerprofile[1] * 10**3


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
        return self.drum[0].mass * self.numberofdrums + self.gear.mass + self.axel.mass + self.motor.mass + self.inverter.mass

    @Attribute
    def efficiency(self):
        return self.drum[0].efficiency * self.gear.efficiency * self.motor.efficiency * self.inverter.efficiency

    @Attribute
    def gearratio(self):
       return self.component_selection_and_sizing()['Gearing']

    @Attribute
    def enginefromdb(self):
        return self.component_selection_and_sizing()['Engine']
    @Attribute
    def efficiency(self):
        pass


    @Part
    def drum(self):
        return Drum(radius = self.component_selection_and_sizing()["Drumradius"], axel_radius = self.axel.radius,
                    width = 0.4, material = self.material, quantify = self.numberofdrums, position = translate(self.axel.position, 'z', 500 * child.index + self.drum[0].width * 1000))# position stuff

    @Part
    def gear(self):
        return Gear(gearratio =self.gearratio)

    @Part
    def axel(self):
        return Axel(torque = self.powerprofile["Force"]/self.component_selection_and_sizing()["Drumradius"],
                    numberofdrums =self.numberofdrums, drumwidth = self.drum[0].width, material = self.material,
                    position =  rotate90(translate(self.position, 'z',900,'y',6000,'x',1200),'x'))

    @Part
    def motor(self):
        return ElectricalMotor(name = self.enginefromdb['name'], peakpower = self.enginefromdb['peakpower'] ,
                               continouspower = self.enginefromdb['continuouspower'],
                               efficiency = self.enginefromdb['avg_efficiency'], mass = self.enginefromdb['mass'],
                               dimensions = self.enginefromdb['dimensions'],
                               position = rotate90(translate(self.position, 'z',900,'y',6000 - (self.axel.lenght* 1000) ,'x',1200),'x'))

    @Part
    def inverter(self):
        return MotorInverter(maxcurrentdraw = self.powerprofile['maxPower']/self.system_Voltage,
                             voltage = self.system_Voltage,
                             position = rotate90(translate(self.position, 'z',450,'y',6000 - (self.axel.lenght+self.motor.dimensions[1]) * 1000 - self.motor.dimensions[1] ,'x',1200),'x'))


    def component_selection_and_sizing(self) -> dict:
        feasible_selection = []
        for i in Electrical_engines:  # filter_out engines based on peak power
            if i['peakpower'] * 10**3 >= self.powerprofile['maxPower']:
                feasible_selection.append(i)

        if not feasible_selection:
            raise Exception("electrical_drives db does not contain a option that can provide the peak power")

        gearing = 20
        selected_engine = None
        for i in feasible_selection:
            required_gearing = np.sqrt(
                self.powerprofile['Force'] / i['ratedTorque'] * i['ratedRPM'] / self.powerprofile['Vmaxf'])  # required gearing to achieve max_force, V, at rated rpm,torque of the engine
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


if __name__ is "__main__":
    from parapy.gui import display
    obj = Drivetrain()
    display(obj)
