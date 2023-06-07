from parapy.core import *
import numpy as np



class Truck(Base):
    winchmass: float = Input()
    winchdimensions: np.ndarray = Input()

    @Attribute
    def type(self):
        return self.truckselection()["type"]

    @Attribute
    def cost(self):
        return self.truckselection()["cost"]

    @Attribute
    def depreciation(self):
        def function(cost): #TODO Implement depreciation function
            return cost * 0.5
        return function(self.cost)

    @Attribute
    def mass(self):
       return self.truckselection()['mass']

    @Attribute
    def geometry(self):
        #TODO create parapy geometry from parametric geometry
        geom = self.truckselection()['geometry']
        return geom

    def truckselection(self): # Check if dependecy-tracking by the attributes on self.data is working
        truck = {"type": None,
                 "mass": None,
                 "cost": None,
                 "depreciation": None,
                 "geometry": None,
                 }
        #TODO implment sql database truck selection querry
        return truck
    





