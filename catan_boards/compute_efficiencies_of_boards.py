##########################################
### Import needed general dependencies ###
##########################################
# Add paths for internal modules
# Import dependencies
from pathlib import Path
from sys import path
# Get the shared unit tests folder
unit_tests_folder = Path(__file__).parent.parent
# Get the shared parent folder
parent_folder = unit_tests_folder.parent
# Get the shared infrastructure folder
infrastructure_folder = parent_folder.joinpath("infrastructure")
# Add the needed paths
path.insert(0, str(infrastructure_folder.joinpath("board_games")))
path.insert(0, str(infrastructure_folder.joinpath("common_needs")))

# Internal modules
from catan_generator import ALL_TILE_TYPES, CatanGeneratorTiling
from tkinter_helper import askSaveFilename

# External modules
from math import log2
from numpy import nan, nanmean


#############################################
### Define pre-existing boards to analyze ###
#############################################
# Pre-set the number of boards to test
n_boards = 5

# Initialize the lists of game modes and tilings
all_game_modes = []
all_tile_per_polygons = []

# Define the 1st board
all_game_modes.append("Original: 3-4 Player")
all_tile_per_polygons.append(["stone", "wheat", "sheep",
							  "wheat", "brick", "stone", "wood",
							  "wood", "wheat", "brick", "wood", "sheep",
							  "brick", "sheep", "wood", "stone",
							  "desert", "wheat", "sheep"])

# Define the 2nd board
all_game_modes.append("Original: 3-4 Player")
all_tile_per_polygons.append(["wheat", "wood", "brick",
							  "stone", "wheat", "desert", "stone",
							  "wheat", "wood", "brick", "sheep", "sheep",
							  "sheep", "stone", "wood", "wheat",
							  "brick", "wheat", "sheep"])

# Define the 3rd board
all_game_modes.append("Original: 5-6 Player")
all_tile_per_polygons.append(["brick", "sheep", "stone",
							  "wood", "wheat", "wood", "wheat",
							  "wood", "stone", "sheep", "brick", "wood",
							  "desert", "sheep", "wheat", "stone", "sheep", "wheat",
							  "wood", "stone", "wood", "wheat", "sheep",
							  "brick", "wheat", "stone", "brick",
							  "brick", "sheep", "desert"])

# Define the 4th board
all_game_modes.append("Original: 5-6 Player")
all_tile_per_polygons.append(["wheat", "sheep", "wheat",
							  "wood", "brick", "stone", "wood",
							  "stone", "wheat", "wood", "desert", "sheep",
							  "wheat", "sheep", "stone", "wheat", "brick", "wood",
							  "desert", "brick", "wood", "stone", "sheep",
							  "sheep", "wood", "wheat", "brick",
							  "sheep", "brick", "stone"])

# Define the 5th board
all_game_modes.append("Seafarers: 3-4 Player")
all_tile_per_polygons.append(["wheat", "wood", "stone", "water", "wheat",
							  "stone", "sheep", "brick", "sheep", "water", "brick",
							  "brick", "wood", "desert", "wheat", "wood", "water", "water",
							  "wheat", "brick", "wheat", "sheep", "water", "gold",
							  "water", "sheep", "wood", "stone", "water", "wood", "water",
							  "water", "water", "water", "water", "brick", "stone",
							  "stone", "sheep", "water", "gold", "water"])

# Define the 6th board
all_game_modes.append("Seafarers: 3-4 Player")
all_tile_per_polygons.append(["water", "wood", "water", "stone", "wheat",
							  "sheep", "sheep", "stone", "water", "water", "water",
							  "brick", "brick", "wheat", "wood", "water", "gold", "sheep",
							  "water", "wood", "brick", "sheep", "water", "water",
							  "wheat", "desert", "stone", "wheat", "wood", "water", "brick",
							  "stone", "desert", "brick", "sheep", "water", "wheat",
							  "gold", "desert", "wood", "water", "stone"])

# Define the 7th board
all_game_modes.append("Seafarers: 3-4 Player")
all_tile_per_polygons.append(["sheep", "wood", "stone", "wheat", "brick",
							  "brick", "wheat", "water", "water", "sheep", "stone",
							  "water", "water", "water", "gold", "water", "water", "stone",
							  "water", "desert", "water", "water", "desert", "water",
							  "wheat", "water", "water", "gold", "water", "water", "water",
							  "wheat", "wood", "water", "water", "wood", "stone",
							  "wood", "sheep", "brick", "sheep", "wheat"])

# Define the 8th board
all_game_modes.append("Seafarers: 5-6 Player")
all_tile_per_polygons.append(["sheep", "stone", "water", "sheep", "water", "brick", "wheat",
							  "wood", "wheat", "water", "wheat", "stone", "water", "brick", "sheep",
							  "water", "brick", "water", "water", "sheep", "wood", "water", "wood", "wheat",
							  "water", "water", "water", "water", "water", "water", "water", "water",
							  "brick", "wheat", "water", "sheep", "wood", "water", "water", "wood", "water",
							  "wood", "stone", "water", "stone", "brick", "water", "wheat", "brick",
							  "sheep", "stone", "water", "wood", "water", "stone", "sheep"])

# Define the 9th board
all_game_modes.append("Seafarers: 5-6 Player")
all_tile_per_polygons.append(["sheep", "wood", "stone", "wood", "wood", "wheat", "brick",
							  "brick", "wheat", "water", "water", "water", "water", "sheep", "stone",
							  "stone", "water", "water", "desert", "water", "desert", "water", "water", "stone",
							  "water", "gold", "water", "water", "water", "water", "gold", "water",
							  "wheat", "water", "water", "desert", "water", "desert", "water", "water", "sheep",
							  "wheat", "wood", "water", "water", "water", "water", "wood", "stone",
							  "wood", "sheep", "brick", "wheat", "brick", "sheep", "wheat"])


#########################################################################
### Loop over the provided boards and compute their efficiency values ###
#########################################################################
# Create a board for each game mode
tiling_per_mode = {}
tiling_per_mode["Original: 3-4 Player"] = CatanGeneratorTiling(game_mode = "Original: 3-4 Player")
tiling_per_mode["Original: 5-6 Player"] = CatanGeneratorTiling(game_mode = "Original: 5-6 Player")
tiling_per_mode["Seafarers: 3-4 Player"] = CatanGeneratorTiling(game_mode = "Seafarers: 3-4 Player")
tiling_per_mode["Seafarers: 5-6 Player"] = CatanGeneratorTiling(game_mode = "Seafarers: 5-6 Player")

# Initialize a dictionary of the efficiency values for each tile type
all_efficiencies_per_tile = {}
for tile_type in ALL_TILE_TYPES:
	all_efficiencies_per_tile[tile_type] = []

# Loop over the boards and compute the efficiency values
for board_index in range(n_boards):
	# Get the current maximum entropy
	if "Original" in all_game_modes[board_index]:
		maximum_entropy = log2(6)
	else:
		maximum_entropy = log2(8)

	# Overwrite the tiling of the needed object
	tiling_per_mode[all_game_modes[board_index]].overwriteTiling(all_tile_per_polygons[board_index])

	# Compute the needed entropy values and store the associated efficiencies
	entropy_by_tile = tiling_per_mode[all_game_modes[board_index]].computeEntropyPerTileType()
	for tile_type in ALL_TILE_TYPES:
		if tile_type in entropy_by_tile:
			# Tile present in this mode, compute efficiency
			all_efficiencies_per_tile[tile_type].append(entropy_by_tile[tile_type] / maximum_entropy)
		else:
			# Tile not present in this mode, ignore for now
			all_efficiencies_per_tile[tile_type].append(nan)

# Compute the maximum string length for the tile types
max_length = max([len(tile_type) for tile_type in ALL_TILE_TYPES])

# Print the expected efficiency values for each tile type
print("EXPECTED EFFICIENCY PER TILE TYPE:")
for tile_type in ALL_TILE_TYPES:
	print("    " + tile_type + " " + "-" * (max_length - len(tile_type) + 3) + "> " + str(round(nanmean(all_efficiencies_per_tile[tile_type]), 2)))