from parapy.core import *


class OperatorCabin(Base):
    dualcontrol: bool = Input(True)

    @Attribute
    def dimensions(self):
        # TODO implement dimension and geometry creation
        dimensions = None
        return dimensions
