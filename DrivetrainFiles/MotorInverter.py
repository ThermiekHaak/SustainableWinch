from parapy.core import*
class MotorInverter(Base):
    maxcurrentdraw = Input()
    powerrequired = Input()

    @Attribute
    def specs(self):
        return self.selectInverter(self.maxcurrentdraw,self.powerrequired)

    @Attribute
    def name(self):
        return self.specs['name']

    @Attribute
    def cost(self):
        return self.specs['cost']

    @Attribute
    def mass(self):
        return self.specs['mass']

    @Attribute
    def efficiency(self):
        return self.specs['efficiency']

    def selectInverter(self):
        # TODO Implement selection from db
        specs = dict()
        return specs