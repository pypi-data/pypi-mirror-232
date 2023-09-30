"""
particle (wet) volume, key attribute for coalescence
in simulation involving mixed-phase clouds, positive values correspond to
liquid water and negative values to ice
"""
from PySDM.attributes.impl.extensive_attribute import ExtensiveAttribute


class Volume(ExtensiveAttribute):
    def __init__(self, builder):
        super().__init__(builder, name="volume")
