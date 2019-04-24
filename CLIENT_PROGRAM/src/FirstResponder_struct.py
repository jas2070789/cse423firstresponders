# Created by Patrick Archer on 15 April 2019

"""
@file defines the firstResponder wearable beacon data transmit object structure.
"""


class firstResponder():

    # object constructor
    def __init__(self, uuid, timestamp, quadrant, steps):
        # beacon UUID
        self.uuid = uuid
        # timestamp of last known communication
        self.timestamp = timestamp
        # current quadrant heading (set to 0 upon init.)
        self.quadrant = quadrant
        # step count of current operational session (set to 0 upon init.)
        self.steps = steps
        # # current floor that the beacon is on (set to "None" upon object init.)
        # self.current_floor = current_floor
        # # closest anchor that the beacon is near (set to "None" upon object init.)
        # self.closest_anchor = closest_anchor

    # get UUID of beacon object
    def getUUID(self):
        return self.uuid

    # change UUID of beacon object
    def changeUUID(self, newUUID):
        self.uuid = newUUID
        return self.uuid

    # # get location_id
    # def getLocationID(self):
    #     return self.location_id
    #
    # # change location_id of beacon object
    # def changeLocationID(self, newLocID):
    #     self.location_id = newLocID
    #     return self.location_id

    # get timestamp of last known communication
    def getTimestamp(self):
        return self.timestamp

    # change timestamp of last known communication
    def changeTimestamp(self, newTime):
        self.timestamp = newTime
        return self.timestamp

    # get current quadrant heading
    def getQuadrant(self):
        return self.quadrant

    # change current quadrant heading
    def changeQuadrant(self, newQuad):
        self.quadrant = newQuad
        return self.quadrant

    # get step count
    def getSteps(self):
        return self.steps

    # change step count
    def changeSteps(self, newSteps):
        self.steps = newSteps
        return self.steps

    # # get current floor of physical beacon
    # def getCurrentFloor(self):
    #     return self.current_floor
    #
    # # change current floor of physical beacon
    # def changeCurrentFloor(self, new_cf):
    #     self.current_floor = new_cf
    #     return self.current_floor
    #
    # # get current closest-proximity anchor to beacon
    # def getClosestAnchor(self):
    #     return self.closest_anchor
    #
    # # change what the closest anchor to the beacon is
    # def changeClosestAnchor(self, new_ca):
    #     self.closest_anchor = new_ca
    #     return self.closest_anchor



