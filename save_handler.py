# -*- coding: utf-8 -*-
"""
Created on Tues Oct 12 23:13:25 2021

@author: Skezza
"""

TEMPLATE_SAVE = {"GameVersion":"v20211008-31c08af-sw","Timestamp":"2022-01-01 01:01:01","Singletons":{"MapSize":{"Size":{"X":4,"Y":4}},"TerrainMap":{"Heights":{"Array":"4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4"}},"CameraStateRestorer":{"SavedCameraState":{"Target":{"X":0.0,"Y":0.0,"Z":0.0},"ZoomLevel":0.0,"HorizontalAngle":30.0,"VerticalAngle":70.0}},"WaterMap":{"WaterDepths":{"Array":"0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"},"Outflows":{"Array":"0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0 0:0:0:0"}},"SoilMoistureSimulator":{"MoistureLevels":{"Array":"0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"}}},"Entities":[]}

import json  # to save the map dictionary to json
from zipfile import ZipFile  # For zipping the save file, required for newer versions of the game
from io import StringIO  # To hold the json file in memory so we can save it in the zip without creating another file


def generate_depth_map_string(depth_map):
    # For each row in the map, join all the columns together in the form `5 5 6`, being their height value
    return " ".join(
                    " ".join(str(element) for element in row)
                    for row in depth_map
                   )


def save_map_to_file(map_object, water_map, entities, map_length, map_width, config):

    map_json = TEMPLATE_SAVE  # Steal most of the data from a template (so we don't have to recreate a bunch of stuff)

    # Change the map's size to be our map_length and map_width 
    map_json["Singletons"]["MapSize"]["Size"] = {"X": map_length, "Y": map_width}

    # We need to convert the 2d height map array into a single string to be saved in the json file
    height_map = generate_depth_map_string(map_object)
    map_json["Singletons"]["TerrainMap"]["Heights"]["Array"] = height_map

    # Water map, to enable the water depth, from 0/0.0 water to x water (in cubes, e.g. 4 would be 4 cubes high)
    water_map = generate_depth_map_string(water_map)
    map_json["Singletons"]["WaterMap"]["WaterDepths"]["Array"] = water_map

    # Moisture map is required, but shouldn't be modified, otherwise errors will occure.
    moisture_map = ("0 "*map_length*map_width).rstrip()
    # This should be left as empty, as the game will measure moisture levels on loadup
    map_json["Singletons"]["SoilMoistureSimulator"]["MoistureLevels"]["Array"] = moisture_map
    
    # Flow/Water Map, not sure what the values represent yet
    # Could be the 4 corners, value 0-100? Setting this seems to have no effect
    # This should also be left how it is, as removing it will cause the game to crash, seems to go up past 2?
    flow_map = ("0:0:0:0 "*map_length*map_width).rstrip()  # same as water_map, but four 0s for each tile
    map_json["Singletons"]["WaterMap"]["Outflows"]["Array"] = flow_map

    # Set up all the entities, trees, bushes, slopes, ruins, barriers, water sources, as well as buildings and beavers
    map_json["Entities"] = entities

    # Add staircases to the list of researched buildings
    if config["auto_unlock_staircases"]:
        map_json["Singletons"]["BuildingUnlockingService"] = {"UnlockedBuildingIds":["WoodenStairs.Folktails"]}

    use_old_system = True
    if use_old_system:
        with open(f"{config['map_name']}.json", "w") as file:   
            json.dump(map_json, file)

    else:
        with open(f"world.json", "w") as file:
            json.dump(map_json, file)
        #memory_file = StringIO()  # Holds a file in memory
        #memory_file.write(" Welcome to geeksforgeeks.")
        #json.dump(map_json, memory_file)

        #memory_file = ZipFile(self.inMemoryOutputFile, 'a')
        #memory_file.writestr(inzipfilename, data)
        #memory_file.close()

        with ZipFile(f"{config['map_name']}.timber", 'w') as zip_file:
            zip_file.write(f"world.json")

    
    print(f"Saved file as '{config['map_name']}")

    
    
