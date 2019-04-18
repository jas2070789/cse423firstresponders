# Created by Patrick Archer on 15 April 2019

"""
@file defines the firstResponder object structure.
"""


class firstResponder():

    # object constructor
    def __init__(self, b_id, closest_anchor, current_floor):
        # beacon ID
        self.b_id = b_id
        # current floor that the beacon is on
        self.current_floor = current_floor
        # closest anchor that the beacon is near
        self.closest_anchor = closest_anchor

    # get ID of wearable device
    def getID(self):
        return self.b_id

    # change current floor of FR beacon
    def changeCurrentFloor(self, new_cf):
        self.current_floor = new_cf
        return self.current_floor

    # change what the closest anchor to the beacon is
    def changeClosestAnchor(self, new_ca):
        self.closest_anchor = new_ca
        return self.closest_anchor



