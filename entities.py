# -*- coding: utf-8 -*-
"""
Created on Tues Oct 13 23:56:25 2021

@author: Skezza
"""
from uuid import uuid4
from random import randint, random, choice

def random_difference():
    return 0.75+(0.5*random())

HAS_MOD = True
MAX_SIZE = 1024 if HAS_MOD else 256
MAP_HEIGHT = 64 if HAS_MOD else 16

class Entity:
    """
    A generic entity class. All other classes inherit from this one.
    You should never have to instantiate this class yourself, it should be done
    for you when creating other entities.
    """
    def __init__(self, entity_type, x, y, z, rotation=None):
        # Doing it like that makes everything a million times easier, even if it's massively bodged.
        # It means you can loop over the length and then width and everything will work.
        # y coord represents how left to right the enitity is, and x how far back they are
        # Z coord represents how high up the entity is,
        y, x, z = (x, y, z)
        assert (isinstance(x, int) and 0 <= x <= MAX_SIZE), f"error, invalid x coordinate, must be an integer between 0 and {MAX_SIZE}!"
        assert (isinstance(y, int) and 0 <= y <= MAX_SIZE), f"error, invalid y coordinate, must be an integer between 0 and {MAX_SIZE}!"
        assert (isinstance(z, int) and 0 <= z <= MAP_HEIGHT),  "error, invalid z coordinate, must be an integer between 0 and {MAP_HEIGHT}!"
        self.id = str(uuid4())
        self.entity_type = entity_type
        if rotation:
            self.components = {"BlockObject": {"Coordinates":{"X":x,"Y":y,"Z":z}, "Orientation": {"Value":f"Cw{rotation}"}}}
        else:
            self.components = {"BlockObject": {"Coordinates":{"X":x,"Y":y,"Z":z}}}
            

    def to_dict(self):
        data = {"Id": self.id, "Template": self.entity_type, "Components": self.components}
        return data

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"{self.entity_type} at {self.x}, {self.y}, {self.z}"

class Plants(Entity):
    def __init__(self, entity_type, x, y, z):
        super().__init__(entity_type, x, y, z)
        # Growth progress, 0.0 to 1.0, 1.0 being fully grown.
        self.components["Growable"] = {"GrowthProgress":1.0}
        # Give each entity a slight offset to make forests less grid based
        self.components["CoordinatesOffseter"] = {"CoordinatesOffset":{"X": 0.0, "Y": 0.0}}
        # This also gives slight differences for natural resources:
        self.components["NaturalResourceModelRandomizer"] = {"Rotation": randint(0, 360),"DiameterScale": random_difference(),"HeightScale": random_difference()-0.25}

class Tree(Plants):
    def __init__(self, x, y, z, tree_type):
        assert tree_type in ("Maple", "Pine", "Birch", "Chestnut"), f"Error, invalid tree type given to tree constructor, expected one of 'Birch', 'Maple', 'Pine' but got {tree_type}"
        super().__init__(tree_type, x, y, z)
        # This is just extra stuff that's needed
        self.components["Yielder:Cuttable"] = {"Yield":{"Good":{"Id":"Log"},"Amount": 8}}
        
        if tree_type == "Chestnut":  # Chestnuts also have a gatherable propery for the chestnuts themselves
            self.components["Yielder:Gatherable"] = {"Yield":{"Good":{"Id":"Chestnut"},"Amount":3}}
            self.components["GatherableYieldGrower"] = {"GrowthProgress":1.0}

class BlueberryBush(Plants):
    def __init__(self, x, y, z):
        super().__init__("BlueberryBush", x, y, z)
        # This is just extra stuff that's needed
        self.components["Yielder:Gatherable"] = {"Yield": {"Good": {"Id": "Berries"}, "Amount": 8}}
        self.components["GatherableYieldGrower"] = {"GrowthProgress":1.0}

class Cattail(Plants):
    def __init__(self, x, y, z):
        super().__init__("Cattail", x, y, z)
        # This is just extra stuff that's needed
        self.components["Yielder:Cuttable"] = {"Yield": {"Good": {"Id": "CattailRoot"}, "Amount": 3}}
        self.components["WateredNaturalResource"] = {"DryingProgress": 0.0}
        self.components["LivingWaterNaturalResource"] = {"DyingProgress": 0.0, "DeathByFlooding": False}

class Spadderdock(Plants):
    def __init__(self, x, y, z):
        super().__init__("Spadderdock", x, y, z)
        # This is just extra stuff that's needed
        self.components["Yielder:Cuttable"] = {"Yield": {"Good": {"Id": "Spadderdock"}, "Amount": 3}}
        self.components["WateredNaturalResource"] = {"DryingProgress": 0.0}
        self.components["LivingWaterNaturalResource"] = {"DyingProgress": 0.0, "DeathByFlooding": False}

class Ruin(Entity):
    # Can have rotation, but I don't think it's important
    def __init__(self, x, y, z, height):
        assert isinstance(height, int) and 0 < height <= 8, "error, ruin height must be an integer between 1 and 8."
        super().__init__(f"RuinColumnH{height}", x, y, z)
        # How much scrap metal each ruin should give
        self.components["Yielder:Ruin"] = {"Yield": {"Good": {"Id": "ScrapMetal"}, "Amount": height*15}}
        # Model variety
        self.components["RuinModels"] = {"VariantId": choice(["A", "B", "C", "D", "E"])}

class Barrier(Entity):
    def __init__(self, x, y, z):
        super().__init__("Barrier", x, y, z)

# Water sources seem to sit one above what you put, so it might be worth trying the height-1?
class WaterSource(Entity):
    def __init__(self, x, y, z, strength=1.0):
        # I don't know if this is limited to 1 or 8
        assert isinstance(strength, (float, int)) and 0.0 <= strength <= 1.0, "error, strength must be a float between 0.0 and 1.0"
        
        super().__init__("WaterSource", x, y, z, rotation=180)
        self.components["WaterSource"] = {"SpecifiedStrength": strength, "CurrentStrength": strength}

class Slope(Entity):
    def __init__(self, x, y, z, rotation):
        assert (rotation in {0, 90, 180, 270}), "error, rotation must be one of '0', '90', '180', '270'!"
        super().__init__("Slope", x, y, z, rotation)
        self.components["ConstructionSite"] = {"BuildTimeProgressInHoursKey":1.0}
        self.components["Constructible"] = {"Finished": True}

#=======================
        
# This is the one entity I don't think is needed to be editable (apart from x, y and z), if I add more buildings in the future I will
class DistrictCenter(Entity):
    # Inventory contents is a dictionary of item ids and amounts
    def __init__(self, x, y, z, rotation, inventory_contents={}):
        # x and y represent the "south-west" corner, i.e. the center will the x+1, y+1 of the given inputs
        super().__init__("DistrictCenter.Folktails", x, y, z)#, rotation=rotation)
        self.components['ConstructionSite'] = {"BuildTimeProgressInHoursKey": 1.0}
        self.components['DistrictCenter'] = {'DistrictName': 'District 1'}
        self.components['Workplace'] = {'DesiredWorkers': 2}
        self.components['Constructible'] = {'Finished': True}
        self.components['DistrictDistributionLimits'] = {"LowLimits":[], "HighLimits":[], "DeactivatedHighLimits":[]}
        self.components['LaborWorkplaceBehavior'] = {'IsOn': True}
        if inventory_contents:
            goods = [{"Good":{"Id":item},"Amount": amount} for item, amount in inventory_contents.items()]
            self.components['Inventory:SimpleOutputInventory'] = {"Storage":{"Goods": goods}}

# This is used so we don't have to re-create every attribute of the beaver manually, we just copy all this over to save effort
BASE_BEAVER_DATA = {
    'CharacterModel':        {'Rotation': {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'W': 0.5}},
    'MovementAnimator':      {'Position': {'X': 1.0, 'Y': 1.0, 'Z': 1.0}, 'LeftTimeInSeconds': 1.0, 'AnimationName': 'Walking', 'AnimationSpeed': 4.0},
    'NeedBehaviorPicker':    {'NeedsBeingCriticallySatisfied': []},
    'NeedManager':           {'Needs': [{'Name': name, 'Points': 0.1} for name in ["Hunger", "Sleep", "SocialLife", "Fun", "NutritionI", "NutritionII", "NutritionIII", "Comfort", "Knowledge", "Spirituality", "Esthetics", "AweI", "AweII", "AweIII"]]+[{'Name': "Thirst", 'Points': 1.0}]},
    'LifeExpectancyManager': {'SumOfLifeExpectancyObservations': 0, 'NumberOfLifeExpectancyObservations': 0, 'BaseLifeExpectancy': 0.5},
    'BehaviorManager':       {'RunningBehaviorId': 'AttractionNeedBehavior', 'RunningBehaviorOwner': 'c62bcf4b-db47-4ec5-bff1-bcbf5596f779', 'ReturnToBehavior': True, 'RunningExecutorId': 'WalkInsideExecutor', 'RunningExecutorElapsedTime': 0.0, 'TimestampedBehaviorLog': []},
    'AttractionAttender':    {'FirstVisit': True},
    'MortalNeeder':          {'DeathDays': []},    
    'MortalRootBehavior':    {'WentToDeathPosition': False},
    'SleepNeedBehavior':     {'WalkedToSleepingPosition': False},
    'WanderRootBehavior':    {'Walked': False}
}

class Beaver(Entity):
    # The devs thought it was a good idea to make every other object use x and y to do horizontal displacement
    # and then use Z to use height, but beavers are the one thing that use y as height, and x+z as horizontal displacement...
    def __init__(self, x, y, z, name):
        self.id = str(uuid4())
        self.entity_type = "BeaverAdult"
        self.components = {"Beaver": {"Position": {'X': x, 'Y': z, 'Z': y}, "Name": name, "DayOfBirth": 1, "Alive": True}}
        # These all need to be empty
        for string in ['Mortal', 'Worker', 'Enterer', 'GoodCarrier', 'Dweller', 'Citizen', 'GoodReserver', 'WalkInsideExecutor', 'Walker', 'Demolisher', 'YielderRemover', 'Builder', 'Planter']:
            self.components[string] = {}
        for key, value in BASE_BEAVER_DATA.items():
            self.components[key] = value       
