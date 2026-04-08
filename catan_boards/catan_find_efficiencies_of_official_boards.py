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

# Built-in modules
from math import log2

# Internal modules
from catan_board_generator import ALL_GAME_MODES, ALL_TILE_TYPES, CatanGeneratorTiling
from tkinter_helper import askSaveFilename

# External modules
from numpy import isnan, nan, nanmean


#############################################
### Define pre-existing boards to analyze ###
#############################################
# Initialize the dictionary of tilings for each game mode
tilings_per_mode = {}
for game_mode in ALL_GAME_MODES:
	tilings_per_mode[game_mode] = []

# Define all the Original: 5 Wide tilings
# Set the game mode
game_mode = "Original: 5 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["stone", "wheat", "sheep",
							  		"wheat", "brick", "stone", "wood",
							  		"wood", "wheat", "brick", "wood", "sheep",
							  		"brick", "sheep", "wood", "stone",
							  		"desert", "wheat", "sheep"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["wheat", "wood", "brick",
							  		"stone", "wheat", "desert", "stone",
							  		"wheat", "wood", "brick", "sheep", "sheep",
							  		"sheep", "stone", "wood", "wheat",
							  		"brick", "wheat", "sheep"])

# Define all the Original: 6 Wide tilings
# Set the game mode
game_mode = "Original: 6 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["brick", "sheep", "stone",
							  		"wood", "wheat", "wood", "wheat",
							  		"wood", "stone", "sheep", "brick", "wood",
							  		"desert", "sheep", "wheat", "stone", "sheep", "wheat",
							  		"wood", "stone", "wood", "wheat", "sheep",
							  		"brick", "wheat", "stone", "brick",
							  		"brick", "sheep", "desert"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["wheat", "sheep", "wheat",
							  		"wood", "brick", "stone", "wood",
							  		"stone", "wheat", "wood", "desert", "sheep",
							  		"wheat", "sheep", "stone", "wheat", "brick", "wood",
							  		"desert", "brick", "wood", "stone", "sheep",
							  		"sheep", "wood", "wheat", "brick",
							  		"sheep", "brick", "stone"])

# Define all the Seafarers: 6 Wide tilings
# Set the game mode
game_mode = "Seafarers: 6 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["wheat", "wood", "water", "brick",
							  		"wheat", "stone", "brick", "water", "stone",
							  		"brick", "sheep", "sheep", "wood", "water", "water",
							  		"sheep", "stone", "wood", "water", "gold",
							  		"water", "wheat", "sheep", "water", "wheat", "water",
							  		"water", "water", "water", "sheep", "stone",
							  		"brick", "gold", "water", "water"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["sheep", "water", "water", "water",
							  		"wood", "sheep", "water", "stone", "wheat",
							  		"wheat", "stone", "wood", "water", "brick", "brick",
							  		"water", "water", "water", "water", "water",
							  		"sheep", "stone", "water", "wood", "brick", "water",
							  		"stone", "wood", "water", "wheat", "brick",
							  		"water", "water", "wheat", "sheep"])
# Define the 3rd board
tilings_per_mode[game_mode].append(["sheep", "wheat", "water", "wheat",
							  		"wheat", "stone", "brick", "water", "stone",
							  		"brick", "sheep", "water", "water", "wood", "sheep",
							  		"water", "water", "wood", "water", "water",
							  		"wheat", "wood", "water", "brick", "stone", "water",
							  		"brick", "water", "stone", "wheat", "sheep",
							  		"sheep", "water", "wood", "wood"])
# Define the 4th board
tilings_per_mode[game_mode].append(["sheep", "sheep", "water", "stone",
							  		"stone", "wheat", "wood", "water", "wheat",
							  		"wood", "brick", "wheat", "brick", "water", "water",
							  		"water", "stone", "wood", "water", "gold",
							  		"wheat", "desert", "brick", "sheep", "water", "water",
							  		"wood", "desert", "wood", "water", "sheep",
							  		"gold", "desert", "water", "stone"])

# Define all the Seafarers: 7 Wide tilings
# Set the game mode
game_mode = "Seafarers: 7 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["wheat", "wood", "stone", "water", "wheat",
							  		"stone", "sheep", "brick", "sheep", "water", "brick",
							  		"brick", "wood", "desert", "wheat", "wood", "water", "water",
							  		"wheat", "brick", "wheat", "sheep", "water", "gold",
							  		"water", "sheep", "wood", "stone", "water", "wood", "water",
							  		"water", "water", "water", "water", "brick", "stone",
							  		"stone", "sheep", "water", "gold", "water"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["water", "wood", "water", "stone", "wheat",
							  		"sheep", "sheep", "stone", "water", "water", "water",
							  		"brick", "brick", "wheat", "wood", "water", "gold", "sheep",
							  		"water", "wood", "brick", "sheep", "water", "water",
							  		"wheat", "desert", "stone", "wheat", "wood", "water", "brick",
							  		"stone", "desert", "brick", "sheep", "water", "wheat",
							  		"gold", "desert", "wood", "water", "stone"])
# Define the 3rd board
tilings_per_mode[game_mode].append(["sheep", "wood", "stone", "wheat", "brick",
							  		"brick", "wheat", "water", "water", "sheep", "stone",
							  		"water", "water", "water", "gold", "water", "water", "stone",
							  		"water", "desert", "water", "water", "desert", "water",
							  		"wheat", "water", "water", "gold", "water", "water", "water",
							  		"wheat", "wood", "water", "water", "wood", "stone",
							  		"wood", "sheep", "brick", "sheep", "wheat"])

# Define all the Seafarers: 8 Wide tilings
# Set the game mode
game_mode = "Seafarers: 8 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["desert", "brick", "water", "brick", "desert", "gold",
							  		"water", "water", "water", "water", "water", "water", "water",
							  		"wood", "wheat", "stone", "sheep", "brick", "wheat", "water", "wood",
							  		"sheep", "brick", "sheep", "wheat", "wood", "sheep", "water",
							  		"wheat", "wood", "stone", "brick", "wood", "stone", "water", "sheep",
							  		"water", "water", "water", "water", "water", "water", "water",
							  		"gold", "stone", "water", "desert", "stone", "wheat"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["gold", "stone", "water", "water", "wheat", "brick",
							  		"brick", "water", "water", "sheep", "water", "stone", "wood",
							  		"wheat", "water", "water", "desert", "water", "sheep", "wood", "sheep",
							  		"water", "stone", "water", "water", "wheat", "brick", "sheep",
							  		"wheat", "water", "water", "desert", "water", "wood", "sheep", "wood",
							  		"brick", "water", "water", "sheep", "water", "stone", "wood",
							  		"gold", "stone", "water", "water", "wheat", "brick"])
# Define the 3rd board
tilings_per_mode[game_mode].append(["stone", "water", "sheep", "sheep", "water", "wheat",
							  		"water", "wood", "water", "wood", "wheat", "water", "wood",
							  		"brick", "sheep", "water", "water", "brick", "water", "water", "gold",
							  		"stone", "wheat", "stone", "sheep", "brick", "desert", "water",
							  		"stone", "wheat", "brick", "wheat", "sheep", "wood", "desert", "water",
							  		"water", "water", "water", "wood", "water", "desert", "water",
							  		"gold", "brick", "water", "stone", "water", "water"])



# Define all the Seafarers: 9 Wide tilings
# Set the game mode
game_mode = "Seafarers: 9 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["sheep", "stone", "water", "sheep", "water", "brick", "wheat",
							  		"wood", "wheat", "water", "wheat", "stone", "water", "brick", "sheep",
							  		"water", "brick", "water", "water", "sheep", "wood", "water", "wood", "wheat",
							  		"water", "water", "water", "water", "water", "water", "water", "water",
							  		"brick", "wheat", "water", "sheep", "wood", "water", "water", "wood", "water",
							  		"wood", "stone", "water", "stone", "brick", "water", "wheat", "brick",
							  		"sheep", "stone", "water", "wood", "water", "stone", "sheep"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["sheep", "wood", "stone", "wood", "wood", "wheat", "brick",
							  		"brick", "wheat", "water", "water", "water", "water", "sheep", "stone",
							  		"stone", "water", "water", "desert", "water", "desert", "water", "water", "stone",
							  		"water", "gold", "water", "water", "water", "water", "gold", "water",
							  		"wheat", "water", "water", "desert", "water", "desert", "water", "water", "sheep",
							  		"wheat", "wood", "water", "water", "water", "water", "wood", "stone",
							  		"wood", "sheep", "brick", "wheat", "brick", "sheep", "wheat"])

# Define all the Seafarers: 10 Wide tilings
# Set the game mode
game_mode = "Seafarers: 10 Wide"
# Define the 1st board
tilings_per_mode[game_mode].append(["sheep", "water", "sheep", "wheat", "water", "gold", "water", "wheat",
							  		"brick", "stone", "water", "water", "water", "water", "water", "sheep", "wood",
							  		"sheep", "wheat", "brick", "stone", "brick", "stone", "wheat", "water", "water", "stone",
							  		"stone", "wood", "wheat", "brick", "sheep", "wood", "brick", "water", "water",
							  		"water", "water", "water", "wheat", "wood", "sheep", "wood", "water", "water", "gold",
							  		"wood", "sheep", "desert", "desert", "desert", "desert", "desert", "water", "water",
							  		"gold", "stone", "brick", "water", "wood", "wheat", "stone", "brick"])
# Define the 2nd board
tilings_per_mode[game_mode].append(["desert", "desert", "water", "stone", "brick", "water", "wheat", "gold",
							  		"water", "water", "water", "water", "water", "water", "water", "water", "water",
							  		"wood", "stone", "wheat", "brick", "wood", "stone", "sheep", "wheat", "wood", "stone",
							  		"wood", "sheep", "wood", "wheat", "sheep", "brick", "wheat", "sheep", "brick",
							  		"wheat", "brick", "stone", "sheep", "brick", "wood", "wheat", "brick", "wood", "stone",
							  		"water", "water", "water", "water", "water", "water", "water", "water", "water",
							  		"desert", "desert", "water", "gold", "gold", "water", "sheep", "sheep"])
# Define the 3rd board
tilings_per_mode[game_mode].append(["gold", "water", "stone", "water", "water", "wood", "wheat", "wood",
							  		"water", "water", "water", "water", "desert", "water", "wheat", "stone", "brick",
							  		"gold", "desert", "stone", "water", "water", "water", "sheep", "sheep", "brick", "sheep",
							  		"water", "water", "water", "desert", "water", "wheat", "wheat", "stone", "sheep",
							  		"gold", "desert", "stone", "water", "water", "water", "wood", "wood", "sheep", "wood",
							  		"water", "water", "water", "water", "desert", "water", "stone", "brick", "wood",
							  		"gold", "water", "stone", "water", "water", "sheep", "wheat", "brick"])
# Define the 4th board
tilings_per_mode[game_mode].append(["water", "stone", "wood", "water", "sheep", "sheep", "water", "gold",
							  		"gold", "water", "wood", "stone", "water", "stone", "wheat", "water", "wood",
							  		"water", "water", "brick", "sheep", "water", "brick", "wood", "stone", "water", "water",
							  		"water", "wheat", "stone", "wood", "stone", "wheat", "sheep", "brick", "desert",
							  		"water", "brick", "sheep", "wheat", "brick", "wheat", "sheep", "wood", "desert", "water",
							  		"water", "water", "brick", "water", "wood", "water", "water", "desert", "desert",
							  		"gold", "water", "sheep", "water", "wheat", "water", "water", "water"])


#########################################################################
### Loop over the provided boards and compute their efficiency values ###
#########################################################################
# Create a generator for each game mode
generator_per_mode = {}
for game_mode in ALL_GAME_MODES:
	generator_per_mode[game_mode] = CatanGeneratorTiling(game_mode = game_mode)

# Initialize a dictionary of the efficiency values for each game mode and tile type
all_efficiencies_per_tuple = {}
for game_mode in ALL_GAME_MODES:
	for tile_type in ALL_TILE_TYPES:
		all_efficiencies_per_tuple[(game_mode, tile_type)] = []

# Loop over the games modes and tilings within to compute the efficiency values
for game_mode in ALL_GAME_MODES:
	# Get the current maximum entropy
	if "Original" in game_mode:
		maximum_entropy = log2(6)
	else:
		maximum_entropy = log2(8)

	# Loop over the tilings for this game mode
	for tiling_index in range(len(tilings_per_mode[game_mode])):
		# Overwrite the tiling of the needed object
		generator_per_mode[game_mode].overwriteTiling(tilings_per_mode[game_mode][tiling_index])

		# Compute the needed entropy values and store the associated efficiencies
		entropy_by_tile = generator_per_mode[game_mode].computeEntropyPerTileType()
		for tile_type in ALL_TILE_TYPES:
			if tile_type in entropy_by_tile:
				# Tile present in this mode, compute efficiency
				all_efficiencies_per_tuple[(game_mode, tile_type)].append(entropy_by_tile[tile_type] / maximum_entropy)
			else:
				# Tile not present in this mode, ignore for now
				all_efficiencies_per_tuple[(game_mode, tile_type)].append(nan)

# Set the subsection label for the average value
average_label = "Average Over All Modes"

# Compute the maximum length of subsection label
max_length = max([len(average_label)] + [len(tile_type) for tile_type in ALL_TILE_TYPES])

# Print the efficiencies of each tile type ranging over the game modes
for tile_type in ALL_TILE_TYPES:
	# Print the section header
	print("EFFICIENCY SUMMARY FOR '" + tile_type + "':")

	# Initialize a list to keep track of all values for this tile type
	all_efficiencies_for_tile_type = []

	# Loop over the game modes
	for game_mode in ALL_GAME_MODES:
		# Get the currently needed efficiencies and add them to the full list
		current_efficiencies = all_efficiencies_per_tuple[(game_mode, tile_type)]
		all_efficiencies_for_tile_type += current_efficiencies

		# Search for any non-nan values in the current values
		found_non_nan = False
		for value in current_efficiencies:
			if not isnan(value):
				found_non_nan = True
				break

		# Print the line for this game mode
		if found_non_nan == True:
			print("    " + game_mode + " " + "-" * (max_length - len(game_mode) + 3) + "> " + str(nanmean(current_efficiencies)))
		else:
			print("    " + game_mode + " " + "-" * (max_length - len(game_mode) + 3) + "> nan")

	# Print the overall mean value
	print("    " + average_label + " " + "-" * (max_length - len(average_label) + 3) + "> " + str(nanmean(all_efficiencies_for_tile_type)))