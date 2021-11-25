##################################################################################################
# CONFIGURATION
# All numbers in the configuration must be integers, no floats.

configuration = {
    # NAME: map_length, CHANGES: The length of the map, must be multiple of 16
    "map_length": 128,
    # NAME: map_width, CHANGES: The width of the map, must be multiple of 16
    "map_width": 128,
    # NAME: map_name, CHANGES: The name of the map file
    "map_name": "output_map_6",
    # NAME: min_height, CHANGES: The minimum point on the map, probably want to keep this at 1, unless you want a deep map floor
    "min_height": 1,
    # NAME: max_height, CHANGES: The maximum point on the map, however this will get capped to 16 (max height) so be careful going above it to avoid flattened hills
    "max_height": 20,
    # NAME: water_level, CHANGES: The maximum level at which water will generate, default is 7
    "water_level": 7,
    # NAME: seed, CHANGES: The random values used to generate terrain, change this to get a different layout, 17 is a nice one to try out
    "seed": 17,
    # NAME: starting_berries, CHANGES: How many to berries to start with, only used when generate_district_center is set to `True`s
    "starting_berries": 130,
    # NAME: starting_beavers, CHANGES: How many beavers to start with, if no district center exists, they will spawn at (1, 1)
    "starting_beavers": 0,  # NOTE: If you want to edit the map in the editor, set this to 0, otherwise it'll crash
    # NAME: auto_unlock_staircases, CHANGES: Whether the player should have staircases pre-unlocked
    # and not have to unlock them through research, often important/required for hilly maps
    "auto_unlock_staircases": True,

    # Enable or disable certain terrain features, all are bools
    # NAME: generate_ponds, CHANGES: Whether to generate ponds
    "generate_ponds": True,
    # NAME: generate_tree, CHANGES: Whether to generate trees
    "generate_trees": True,
    # NAME: generate_lake_vegetation, CHANGES: Whether to generate Cattails and Spadderdock in lakes
    "generate_lake_vegetation": True,
    # NAME: generate_berries, CHANGES: Whether to generate berries on mountain tops
    "generate_berries": True,
    # NAME: generate_walls, CHANGES: Whether to stop water spilling out by raising the terrain around the edge
    "generate_walls": True,
    # NAME: generate_streams, CHANGES: Whether to spawn streams from mountains
    "generate_streams": True,
    # NAME: generate_ruins, CHANGES: Wether to spawn ruins on the map
    "generate_ruins": True,
    # NAME: generate_district_center, CHANGES: Whether or not to provide a district center, so the map is directly playable
    "generate_district_center": True,
    # NAME: generate_slopes: CHANGES: Whether to spawn random slops around the map
    "generate_slopes": True,

    # PERLIN SETTINGS, PROBABLY DON'T WANT TO CHANGE THESE UNLESS YOU KNOW WHAT YOU'RE DOING!!!
    "octaves": 1,  # int
    "persistence": 0.5,  # float
    "lacunarity": 2,  # float
    "frequency": 1,  # float
    "amplitude": 1,  # float

    # IF YOU HAVE THE `QuadrupleTerrainHeight by Ximsa` YOU CAN ENABLE THIS WHICH WILL ALLOW BIGGER MAPS
    "has_quad_terrain_mod": False,
}
configuration["terrain_height_limit"] = 64 if configuration["has_quad_terrain_mod"] else 16
##################################################################################################

MAX_MAP_LENGTH = 1024 if configuration["has_quad_terrain_mod"] else 256
MAX_MAP_WIDTH = 1024 if configuration["has_quad_terrain_mod"] else 256
MAX_MAP_HEIGHT = 64 if configuration["has_quad_terrain_mod"] else 16

def verify_inputs(config):
    # Assert types
    for variable in ("map_length", "map_width", "min_height", "max_height", "water_level", "seed", "starting_berries", "starting_beavers", "octaves"):
        assert isinstance(config[variable], int), f"error, {variable} must be an integer"
        assert config[variable] >= 0, "error, {variable} cannot be negative!"

    # Assert all booleans
    for generate_x in ("generate_ponds", "generate_trees", "generate_lake_vegetation", "generate_berries", "generate_walls", "generate_streams", "generate_ruins", "generate_district_center", "generate_slopes"):
        assert isinstance(config[generate_x], bool), f"error, {generate_x} must be `True` or `False`"

    # Assert values:
    assert 16 <= config["map_length"] <= MAX_MAP_LENGTH, "invalid map_length, must be between 16 and {MAX_MAP_LENGTH}"
    assert 16 <= config["map_width"] <= MAX_MAP_WIDTH, "invalid map_width, must be between 16 and {MAX_MAP_WIDTH}"
    assert config["map_length"]%16==0, "invalid map_length, must be a multiple of 16"
    assert config["map_width"] %16==0, "invalid map_width, must be a multiple of 16"
    
    assert config["max_height"] > 2, "max_height must be more than 2!"
    assert config["min_height"] < MAX_MAP_HEIGHT, "the mimimum height can't be this high! Try to make it low, e.g. 1-4"
    assert config["max_height"] <= MAX_MAP_HEIGHT+16, "the maximum height can't be this high! Try to make it lower, e.g. 4-20"
    assert config["min_height"] < config["max_height"], "min_height must be less than max_height!"
