# -*- coding: utf-8 -*-
"""
Created on Tues Oct 12 23:13:25 2021

@author: Skezza
"""

from entities import Tree, Cattail, Spadderdock, BlueberryBush, Ruin, Barrier, WaterSource, DistrictCenter, Slope, Beaver
import numpy as np

ADJACENT_NEIGHBOURS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

ALL_NEIGHBOURS = [(-1, -1), (0, -1), (1, -1),
                  (-1,  0),          (1,  0),
                  (-1,  1), (0,  1), (1,  1)]

ONE_OFF_NEIGHBOURS = [(x, y) for x in range(-2, 3) for y in range(-2, 3) if (x, y) != (0, 0) and (x, y) not in ALL_NEIGHBOURS]
TWO_OFF_NEIGHBOURS = [(x, y) for x in range(-3, 4) for y in range(-3, 4) if (x, y) != (0, 0) and (x, y) not in ALL_NEIGHBOURS and (x, y) not in ONE_OFF_NEIGHBOURS]

ROTATIONS = [0, 90, 180, 270]

ROTATION_TO_OFFSET = {0: (-1, 0),
                      90: (0, -1),
                      180: (1, 0),
                      270: (0, 1)
}

def generate_ponds(map_array, water_map, map_length, map_width, water_level):
    for x in range(1, map_length-1):
        for y in range(1, map_width-1):
            if map_array[x, y] <= water_level:
                water_map[x, y] = water_level-map_array[x, y]

    return water_map

def generate_trees(map_array, water_map, entities, map_length, map_width, config):
    for x in range(1, map_length-1):
        for y in range(1, map_width-1):
            if water_map[x, y] < 0.01:  # If the current tile isn't water
                # If any of the neighbours have a water level of > 0.01
                if any([water_map[x+x_offset, y+y_offset] > 0.01 for x_offset, y_offset in ALL_NEIGHBOURS]):
                    new_tree = Tree(x, y, int(map_array[x, y]), tree_type="Pine")
                    entities.append(new_tree.to_dict())
               
    return entities

def generate_lake_vegetation(map_array, water_map, entities, map_length, map_width, config):
    for x in range(1, map_length-1):
        for y in range(1, map_width-1):
            # If the water is 1 tile deep
            if map_array[x, y] == config["water_level"]-1:
                #new_spadderdock = Spadderdock(x, y, int(map_array[x, y]))
                #entities.append(new_spadderdock.to_dict())
                new_cattail = Cattail(x, y, int(map_array[x, y]))
                entities.append(new_cattail.to_dict())
                
    return entities

def generate_berries(map_array, water_map, entities, map_length, map_width, config):
    for x in range(3, map_length-3):
        for y in range(3, map_width-3):
            if water_map[x, y] < 0.01:  # If the current tile isn't water
                # If any of the neighbours have a water level of > 0.01
                if any([water_map[x+x_offset, y+y_offset] > 0.01 for x_offset, y_offset in ONE_OFF_NEIGHBOURS+TWO_OFF_NEIGHBOURS]):
                    new_blueberry_bush = BlueberryBush(x, y, int(map_array[x, y]))
                    entities.append(new_blueberry_bush.to_dict())
               
    return entities

def generate_wall(map_array, water_map, entities, map_length, map_width, config):
    for x in range(map_length):
        for y in range(map_width):
            if (x == 0 or x == map_length-1) or (y == 0 or y == map_width-1):
                map_array[x, y] = max(map_array[x, y], config["water_level"])
                        
    return entities


def generate_streams(map_array, water_map, entities, map_length, map_width, config):
    np.random.seed(0)
    max_height = int(map_array.max())   
    update_after = []
    for x in range(1, map_length-1):
        for y in range(1, map_width-1):
            if map_array[x, y] == max_height:  # If it's a mountain top
                # If the tile is completely surrounded by other tiles
                if all([map_array[x, y] == map_array[x+x_offset, y+y_offset] for x_offset, y_offset in ALL_NEIGHBOURS]):
                    # Add it to a list to update after the processing, otherwise the terrain will be lowered 
                    # and the neighbouring tiles won't be surrounded by other tiles anymore, so won't pass the `any`
                    update_after.append((x, y))

    # For all the tiles we want to update
    for x, y in update_after:
        map_array[x, y] -= 1  # Reduce their terrain height by one (to make room for the water and source)
        water_map[x, y] = 1  # Add some water

        new_water_source = WaterSource(x, y, int(map_array[x, y]), strength=0.03)
        entities.append(new_water_source.to_dict())  # Add the water source

    # Get one of the mountain top water sources and remove a hole for the water to flow out of
    for _ in range(2):
        x, y = update_after[np.random.randint(len(update_after))]
        for x_offset, y_offset in ADJACENT_NEIGHBOURS:
            if map_array[x+x_offset, y+y_offset] == max_height:
                map_array[x+x_offset, y+y_offset] -= 1
                break            
    
    return entities

def generate_ruins(map_array, water_map, entities, map_length, map_width, config):
    for x in range(1, map_length-1):
        for y in range(1, map_width-1):
            # If the tile is in the middle height of the map
            if map_array[x, y] == int((map_array.max()-map_array.min())//2):
                # If all it's adjacent neighbours are the same height (flat)
                if all([map_array[x, y] == map_array[x+x_offset, y+y_offset] for x_offset, y_offset in ALL_NEIGHBOURS]):
                    new_ruin = Ruin(x, y, int(map_array[x, y]), height=np.random.randint(1, 6))
                    entities.append(new_ruin.to_dict())  # Add a ruins structure there, with a random height
    return entities

def generate_district_center(map_array, water_map, entities, map_length, map_width, config):

    checked_tiles = []

    while len(checked_tiles) < map_length*map_width:
        x = np.random.randint(2, map_length-2)
        y = np.random.randint(2, map_width-2)
        if (x, y) in checked_tiles:
            continue
        # We need to make sure it's completely flat, since we need a 3x3 area for the district, and another tile to be able to walk or put trees
        if all([map_array[x, y] == map_array[x+x_offset, y+y_offset] for x_offset, y_offset in ALL_NEIGHBOURS+ONE_OFF_NEIGHBOURS]):
            new_district_center = DistrictCenter(x-1, y-1, int(map_array[x, y]), rotation=180, inventory_contents={"Berries": config["starting_berries"]})
            entities.append(new_district_center.to_dict())  # Add a district center with the amount of berries from config
            break
        checked_tiles.append((x, y))

    if len(checked_tiles) >= map_length*map_width:
        raise ValueError("Error, could not find viable space for district center!")
    else:
        # Add some trees so the game isn't completely impossible
        for x_offset, y_offset in ONE_OFF_NEIGHBOURS[:2]+ONE_OFF_NEIGHBOURS[3:]:
            new_tree = Tree(x+x_offset, y+y_offset, int(map_array[x+x_offset, y+y_offset]), tree_type="Maple")
            entities.append(new_tree.to_dict())        
    
    return entities

def generate_slopes(map_array, water_map, entities, map_length, map_width, config):
    # Loop over every 16x16 "chunk", and put a few slopes in if possible
    for x_chunk in range(map_length//16):
        for y_chunk in range(map_width//16):
            slopes = []
            for _ in range(5):  # Try and place 5 slopes per chunk
                x = x_chunk*16+np.random.randint(0, 15)
                y = y_chunk*16+np.random.randint(0, 15)

                # Stop 2 slopes appearing in one tile
                if (x, y) in slopes:
                    continue

                np.random.shuffle(ROTATIONS)  # We shuffle the rotation to stop a bunch of slopes all facing north
                for rotation in ROTATIONS:
                    x_offset, y_offset = ROTATION_TO_OFFSET[rotation]
                    # If the neigbour is one higher
                    if map_array[x, y]+1 == map_array[x+x_offset, y+y_offset] and map_array[x, y]+1 != map_array[x-x_offset, y-y_offset]:
                        slope = Slope(x, y, int(map_array[x, y]), rotation=rotation)
                        entities.append(slope.to_dict())
                        slopes.append((x, y))
                        continue
            
    return entities

def generate_beavers(map_array, water_map, entities, map_length, map_width, config):
    district_center = [x for x in entities if x["Template"] == "DistrictCenter.Folktails"]
    if district_center:
        coords = district_center[0]["Components"]["BlockObject"]["Coordinates"]
        x, y = (coords["X"]+1, coords["Y"]-2)
    else:
        x, y = (1, 1)

    for i in range(config["starting_beavers"]):
        beaver = Beaver(x, y, int(map_array[x, y]), name=str(i+1))
        entities.append(beaver.to_dict())
        
    return entities




