# -*- coding: utf-8 -*-
"""
Created on Tues Oct 12 23:13:25 2021

@author: Skezza
"""

import matplotlib.pyplot as plt
import numpy as np

from perlin_noise_2d import generate_map_array
from save_handler import save_map_to_file
from map_features import generate_ponds, generate_trees, generate_lake_vegetation, generate_berries, generate_wall, generate_streams, generate_ruins, generate_district_center, generate_slopes, generate_beavers
from config import configuration, verify_inputs


def main(config):

    # Make sure the configuration values will hopefully not crash the game
    verify_inputs(config)

    map_length, map_width = config["map_length"], config["map_width"]

    # Used so numpy can generate a world depending on the seed, and that won't change if you pick the same seed
    np.random.seed(config["seed"])
    
    # Generate a our map array, in range min_height to max_height
    map_array = generate_map_array(map_length, map_width, config)

    # Used to display the map as an image
    #plt.imshow(map_array, origin='upper')
    #plt.show()

    water_map = np.zeros((map_length, map_width))
    if config["generate_ponds"]:
        print(f"> Generating Ponds")
        water_map = generate_ponds(map_array, water_map, map_length, map_width, config["water_level"])

    entities = []
    for enabled, function in [("generate_walls", generate_wall), ("generate_trees", generate_trees), ("generate_lake_vegetation", generate_lake_vegetation), ("generate_berries", generate_berries), ("generate_streams", generate_streams), ("generate_ruins", generate_ruins), ("generate_district_center", generate_district_center), ("generate_slopes", generate_slopes), ("starting_beavers", generate_beavers), ]:
        if config[enabled]:
            print(f"> Generating {' '.join(enabled.split('_')[1:]).title()}")
            entities = function(map_array, water_map, entities, map_length, map_width, config)

    # Convert the 2d NumPy array into a .json map file
    save_map_to_file(map_array, water_map, entities, map_length, map_width, config)

if __name__ == "__main__":
    main(configuration)
