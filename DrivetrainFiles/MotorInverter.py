from parapy.core import*
from parapy.geom import*
from Database.inverters import HVI, LVI
class MotorInverter(GeomBase):
    maxcurrentdraw = Input()
    voltage = Input(400)
    position = Input((0,0,0))

    @Attribute
    def specs(self):
        return self.selectInverter()

    @Attribute
    def name(self):
        return self.specs['name']

    @Attribute
    def mass(self):
        return self.specs['mass']

    @Attribute
    def efficiency(self):
        return self.specs['efficiency']

    def selectInverter(self):
        # TODO Implement selection from db
        if self.voltage > 400:
            candidates = HVI
        else:
            candidates = LVI

        efficiency = 0
        selected = None
        for i in candidates:
            if i['peakcurrent'] > self.maxcurrentdraw and i["efficiency"] > efficiency:
                selected = i
        if selected:
            return selected

        raise Exception("No Inverter in the database is worthy")

    @Part
    def geometry(self):
        return Box(width = self.specs['dimensions'][0], length=self.specs['dimensions'][1],
                   height = self.specs['dimensions'][2], position=self.position)