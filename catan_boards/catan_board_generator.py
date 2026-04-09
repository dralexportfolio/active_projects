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
from math import log2, sqrt
from typing import Any

# Internal modules
from Board import Board
from color_helper import RGB
from Polygon import HEXAGON_REGULAR_TALL
from privacy_helper import privacyDecorator
from tkinter_helper import createCanvas, createRectangle, createWindow
from type_helper import isListWithStringEntries, isNumeric, tolerantlyCompare

# External modules
from numpy import random
from PIL import Image



#####################################################
### Define important shared settings for the game ###
#####################################################
# Define the default bevel and sun information
CATAN_BEVEL_ATTITUDE = 25
CATAN_BEVEL_SIZE = 0.1
CATAN_SUN_ANGLE = 120
CATAN_SUN_ATTITUDE = 35

# Define the lists of keys shared between multiple dictionaries
ALL_GAME_MODES = ["Original: 5 Wide", "Original: 6 Wide", "Seafarers: 6 Wide", "Seafarers: 7 Wide", "Seafarers: 8 Wide", "Seafarers: 9 Wide", "Seafarers: 10 Wide"]
ALL_TILE_TYPES = ["brick", "sheep", "stone", "wheat", "wood", "desert", "gold", "water"]

# Define a dictionary of tile count per row for each game mode
ROW_COUNTS_PER_MODE = {
	"Original: 5 Wide": [3, 4, 5, 4, 3],				# 19 total
	"Original: 6 Wide": [3, 4, 5, 6, 5, 4, 3],			# 30 total
	"Seafarers: 6 Wide": [4, 5, 6, 5, 6, 5, 4],			# 35 total
	"Seafarers: 7 Wide": [5, 6, 7, 6, 7, 6, 5],			# 42 total
	"Seafarers: 8 Wide": [6, 7, 8, 7, 8, 7, 6],			# 49 total
	"Seafarers: 9 Wide": [7, 8, 9, 8, 9, 8, 7],			# 56 total
	"Seafarers: 10 Wide": [8, 9, 10, 9, 10, 9, 8]		# 63 total
}

# Define a dictionary of tile count per type for each game mode
TILE_COUNTS_PER_MODE = {
	"Original: 5 Wide": {			# 19 total, 18 with numbers
		"brick": 3,
		"sheep": 4,
		"stone": 3,
		"wheat": 4,
		"wood": 4,
		"desert": 1,
		"gold": 0,
		"water": 0
	},
	"Original: 6 Wide": {			# 30 total, 28 with numbers
		"brick": 5,
		"sheep": 6,
		"stone": 5,
		"wheat": 6,
		"wood": 6,
		"desert": 2,
		"gold": 0,
		"water": 0
	},
	"Seafarers: 6 Wide": {			# 35 total, 24 with numbers
		"brick": 4,
		"sheep": 5,
		"stone": 4,
		"wheat": 4,
		"wood": 5,
		"desert": 1,
		"gold": 2,
		"water": 10
	},
	"Seafarers: 7 Wide": {			# 42 total, 25 with numbers
		"brick": 4,
		"sheep": 5,
		"stone": 4,
		"wheat": 5,
		"wood": 5,
		"desert": 1,
		"gold": 2,
		"water": 16
	},
	"Seafarers: 8 Wide": {			# 49 total, 27 with numbers
		"brick": 5,
		"sheep": 5,
		"stone": 5,
		"wheat": 5,
		"wood": 5,
		"desert": 2,
		"gold": 2,
		"water": 20
	},
	"Seafarers: 9 Wide": {			# 56 total, 30 with numbers
		"brick": 5,
		"sheep": 6,
		"stone": 5,
		"wheat": 6,
		"wood": 6,
		"desert": 2,
		"gold": 2,
		"water": 24
	},
	"Seafarers: 10 Wide": {			# 63 total, 33 with numbers
		"brick": 6,
		"sheep": 6,
		"stone": 6,
		"wheat": 6,
		"wood": 6,
		"desert": 3,
		"gold": 3,
		"water": 27
	}
}

# Define a dictionary of number counts for each game mode
NUMBER_COUNTS_PER_MODE = {
	"Original: 5 Wide": {			# 20 total
		2: 1,
		3: 2,
		4: 2,
		5: 2,
		6: 2,
		8: 2,
		9: 2,
		10: 2,
		11: 2,
		12: 1
	},
	"Original: 6 Wide": {			# 28 total
		2: 2,
		3: 3,
		4: 3,
		5: 3,
		6: 3,
		8: 3,
		9: 3,
		10: 3,
		11: 3,
		12: 2
	},
	"Seafarers: 6 Wide": {			# 26 total
		2: 2,
		3: 2,
		4: 3,
		5: 3,
		6: 3,
		8: 3,
		9: 3,
		10: 3,
		11: 2,
		12: 2
	},
	"Seafarers: 7 Wide": {			# 28 total
		2: 2,
		3: 3,
		4: 3,
		5: 3,
		6: 3,
		8: 3,
		9: 3,
		10: 3,
		11: 3,
		12: 2
	},
	"Seafarers: 8 Wide": {			# 28 total
		2: 2,
		3: 3,
		4: 3,
		5: 3,
		6: 3,
		8: 3,
		9: 3,
		10: 3,
		11: 3,
		12: 2
	},
	"Seafarers: 9 Wide": {			# 32 total
		2: 2,
		3: 3,
		4: 4,
		5: 4,
		6: 3,
		8: 3,
		9: 4,
		10: 4,
		11: 3,
		12: 2
	},
	"Seafarers: 10 Wide": {			# 34 total
		2: 2,
		3: 3,
		4: 4,
		5: 4,
		6: 4,
		8: 4,
		9: 4,
		10: 4,
		11: 3,
		12: 2
	}
}

# Define the target efficiency values for each game mode and tile type
# Initialize the dictionary
TARGET_EFFICIENCY_PER_TUPLE = {}
# Add information for brick
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "brick")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "brick")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "brick")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "brick")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "brick")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "brick")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "brick")] = 0.85
# Add information for sheep
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "sheep")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "sheep")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "sheep")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "sheep")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "sheep")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "sheep")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "sheep")] = 0.85
# Add information for stone
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "stone")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "stone")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "stone")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "stone")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "stone")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "stone")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "stone")] = 0.8
# Add information for wheat
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "wheat")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "wheat")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "wheat")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "wheat")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "wheat")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "wheat")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "wheat")] = 0.85
# Add information for wood
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "wood")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "wood")] = 0.9
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "wood")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "wood")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "wood")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "wood")] = 0.85
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "wood")] = 0.85
# Add information for desert
TARGET_EFFICIENCY_PER_TUPLE[("Original: 5 Wide", "desert")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Original: 6 Wide", "desert")] = 0.8
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "desert")] = 0.5
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "desert")] = 0.5
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "desert")] = 0.5
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "desert")] = 0.5
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "desert")] = 0.5
# Add information for gold
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "gold")] = 0.4
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "gold")] = 0.4
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "gold")] = 0.4
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "gold")] = 0.3
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "gold")] = 0.3
# Add information for water
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 6 Wide", "water")] = 0.4
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 7 Wide", "water")] = 0.6
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 8 Wide", "water")] = 0.6
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 9 Wide", "water")] = 0.6
TARGET_EFFICIENCY_PER_TUPLE[("Seafarers: 10 Wide", "water")] = 0.6

# Define the colors used for each tile
COLOR_PER_TILE = {
	"brick": RGB((180, 60, 30)),
	"sheep": RGB((20, 200, 50)),
	"stone": RGB((127, 127, 127)),
	"wheat": RGB((250, 230, 20)),
	"wood": RGB((10, 80, 10)),
	"desert": RGB((230, 210, 150)),
	"gold": RGB((160, 140, 50)),
	"water": RGB((80, 210, 240))
}

# Define any additional object colors
CIRCLE_COLOR = RGB((210, 170, 110))
LOW_PROB_NUMBER_COLOR = RGB((0, 0, 0))
HIGH_PROB_NUMBER_COLOR = RGB((200, 0, 0))

# Define a marginal Shannon entropy function
def computeMarginalEntropy(prob_value:Any) -> float:
	# Compute the marginal Shannon entropy associated with a probability value
	# Verify the inputs
	assert isNumeric(prob_value, include_numpy_flag = True) == True, "computeMarginalEntropy: Provided value for 'prob_value' must be numeric"
	assert 0 <= prob_value and prob_value <= 1, "computeMarginalEntropy: Provided value for 'prob_value' must be >= 0 and <= 1"

	# Compute the needed value and return it
	if prob_value in [0, 1]:
		return 0
	else:
		return prob_value * log2(1 / prob_value)


###############################################
### Define the board generator tiling class ###
###############################################
# Create the decorator needed for making the attributes private
catan_generator_tiling_decorator = privacyDecorator(["_adjacency_matrix",					# class variables
													 "_board",
													 "_maximum_entropy",
													 "_n_polygons",
													 "_needed_tile_types",
													 "_neighbor_counts_per_tile",
													 "_neighbor_indices_per_polygon",
													 "_tiles_per_index",
													 "_initializeBoard",					# private functions
													 "_initializeStorageFromTiling",
													 "_initializeTiling"])

# Define the class with private attributes
@catan_generator_tiling_decorator
class CatanGeneratorTiling:
	### Initialize the class ###
	def __init__(self, game_mode:str, seed:int = None):
		# Verify the inputs
		assert game_mode in ALL_GAME_MODES, "CatanGeneratorTiling::__init__: Provided value for 'game_mode' must be contained in the list ALL_GAME_MODES"
		if seed is not None:
			assert type(seed) == int, "CatanGeneratorTiling::__init__: If provided, value for 'seed' must be an int object"
			assert 0 <= seed and seed < 2**32, "CatanGeneratorTiling::__init__: If provided, value for 'seed' must be >= 0 and < 2^32"

		# Store the provided values
		self._game_mode = game_mode

		# Initialize a new tiling given the current game mode
		self._initializeBoard()
		self._initializeRandomTiling(seed = seed)

	### Define internal functions for initializing freshly created tilings ###
	def _initializeBoard(self):
		# Initialize information related to the polygon layout and stored Board object
		# Set the number of polygons based on the game mode
		self._n_polygons = sum(ROW_COUNTS_PER_MODE[self._game_mode])

		# Create a list of all polygons objects to be passed to the Board object
		all_polygons = [HEXAGON_REGULAR_TALL for _ in range(self._n_polygons)]

		# Create the lists of x-value and y-value shifts associated with each polygon
		x_shift_per_polygon = []
		y_shift_per_polygon = []
		for row_index in range(len(ROW_COUNTS_PER_MODE[self._game_mode])):
			y_shift = 3 / 2 * row_index
			for col_index in range(ROW_COUNTS_PER_MODE[self._game_mode][row_index]):
				x_shift = sqrt(3) * (col_index - ROW_COUNTS_PER_MODE[self._game_mode][row_index] / 2)
				x_shift_per_polygon.append(x_shift)
				y_shift_per_polygon.append(y_shift)

		# Determine the indices adjacent to each polygon on the board
		# Initialize the needed storage
		self._neighbor_indices_per_polygon = {}
		for polygon_index in range(self._n_polygons):
			self._neighbor_indices_per_polygon[polygon_index] = []
		# Compute the theoretically correct distance for adjacent polygons
		theoretical_distance = sqrt(3)
		# Mark which polygons are adjacent to which other polygons
		for polygon_index_1 in range(self._n_polygons - 1):
			# Get the x-shift and y-shift for the 1st polygon
			x_shift_1 = x_shift_per_polygon[polygon_index_1]
			y_shift_1 = y_shift_per_polygon[polygon_index_1]
			# Loop over the needed other polygons
			for polygon_index_2 in range(polygon_index_1 + 1, self._n_polygons):
				# Get the x-shift and y-shift for the 2nd polygon
				x_shift_2 = x_shift_per_polygon[polygon_index_2]
				y_shift_2 = y_shift_per_polygon[polygon_index_2]
				# Compute the actual distances between the centers of these polygons
				actual_distance = sqrt((x_shift_1 - x_shift_2)**2 + (y_shift_1 - y_shift_2)**2)
				# Mark that the polygons are adjacent if the distance is correct (within a margin of error)
				if tolerantlyCompare(actual_distance, "==", theoretical_distance, threshold = 10**-3):
					self._neighbor_indices_per_polygon[polygon_index_1].append(polygon_index_2)
					self._neighbor_indices_per_polygon[polygon_index_2].append(polygon_index_1)

		# Create and store the Board object for the tiling
		self._board = Board(n_polygons = self._n_polygons,
			  				all_polygons = all_polygons,
			  				x_shift_per_polygon = x_shift_per_polygon,
			  				y_shift_per_polygon = y_shift_per_polygon)

	def _initializeRandomTiling(self, seed:int):
		# Perform all steps necessary for obtaining an initial tiling
		# Set the random seed (if needed)
		if seed is not None:
			random.seed(seed = seed)

		# Randomly assigning an initial tile selection to each polygon
		# Initialize the needed storage
		self._tile_per_polygon = []
		# Create the list of currently selectable tiles given the current game mode
		possible_tiles = []
		for tile_type in TILE_COUNTS_PER_MODE[self._game_mode]:
			for _ in range(TILE_COUNTS_PER_MODE[self._game_mode][tile_type]):
				possible_tiles.append(tile_type)
		# Perform the tiling assignment to each polygon
		for polygon_index in range(self._n_polygons):
			# Select and tile and remove it from the list of possible tiles
			tile_index = random.randint(len(possible_tiles))
			selected_tile_type = possible_tiles.pop(tile_index)
			# Assign this tile to this polygon
			self._tile_per_polygon.append(selected_tile_type)

		# Initialize the other storage variables given this new random tiling
		self._initializeStorageFromTiling()

	def _initializeStorageFromTiling(self):
		# Compute the tiling related storage variables which might be shared by providing a specific tiling or randomly generating one
		# Get the tile types which actually appear in this particular tiling, also compute the resulting maximum entropy
		self._needed_tile_types = [tile_type for tile_type in ALL_TILE_TYPES if tile_type in self._tile_per_polygon]
		self._maximum_entropy = log2(len(self._needed_tile_types))

		# Count the number of neighbors of each tile type belonging to each type of tile
		# Initialize the dictionary
		self._neighbor_counts_per_tile = {}
		for tile_type_1 in self._needed_tile_types:
			self._neighbor_counts_per_tile[tile_type_1] = {}
			for tile_type_2 in self._needed_tile_types:
				self._neighbor_counts_per_tile[tile_type_1][tile_type_2] = 0
		# Compute the neighbor counts
		for polygon_index_1 in range(self._n_polygons):
			tile_type_1 = self._tile_per_polygon[polygon_index_1]
			for polygon_index_2 in self._neighbor_indices_per_polygon[polygon_index_1]:
				tile_type_2 = self._tile_per_polygon[polygon_index_2]
				self._neighbor_counts_per_tile[tile_type_1][tile_type_2] += 1

	### Define an external function for overwriting the tiling with specific values ###
	def overwriteTiling(self, tile_per_polygon:list):
		# Overwrite the randomly generated tiling (i.e. the primary use case) with a specified one (i.e. the secondary use case)
		# Verify the inputs
		assert isListWithStringEntries(tile_per_polygon, allow_empty_flag = False) == True, "CatanGeneratorTiling::overwriteTiling: Provided value for 'tile_per_polygon' must be a list object containing non-empty str objects as entries"
		assert len(tile_per_polygon) == self._n_polygons, "CatanGeneratorTiling::overwriteTiling: Provided value for 'tile_per_polygon' must be a list of length equal to the stored number of polygons (in this case " + str(self._n_polygons) + ")"
		for value in tile_per_polygon:
			assert value in ALL_TILE_TYPES, "CatanGeneratorTiling::overwriteTiling: Provided value for 'tile_per_polygon' must be a list of valid tile types"

		# Update the tile for each polygon
		self._tile_per_polygon = tile_per_polygon

		# Initialize the other storage variables given this new specified tiling
		self._initializeStorageFromTiling()

	### Define external functions for preprocessing bevel and sun information for all polygons ###
	def preprocessAllBevelInfo(self, bevel_attitude:Any, bevel_size:Any):
		# Preprocess all information related to the bevel for all polygons on the stored board (leaving error checking to the Board object)
		self._board.preprocessAllBevelInfo(bevel_attitude = bevel_attitude, bevel_size = bevel_size)

	def preprocessAllSunInfo(self, sun_angle:Any, sun_attitude:Any):
		# Preprocess all information related to the sun for all polygons on the stored board (leaving error checking to the Board object)
		self._board.preprocessAllSunInfo(sun_angle = sun_angle, sun_attitude = sun_attitude)

	### Define an external function for closing figures to save on memory ###
	def closeFigures(self):
		# Close the figures associated with all polygons on the stored board
		self._board.closeFigures()

	### Define an external function for computing the Shannon entropy of neighbor distributions for each tile type ###
	def computeEntropyPerTileType(self) -> dict:
		# Compute the Shannon entropy of the probability distributions over possible neighbors for each tile type
		# Initialize all the storage dictionaries needed for this function
		# Create the main dictionaries
		neighbor_probs_per_tile = {}
		entropy_by_tile = {}
		# Loop over the needed tile types and add more information
		for tile_type_1 in self._needed_tile_types:
			# Add in the storage at this level
			neighbor_probs_per_tile[tile_type_1] = {}
			entropy_by_tile[tile_type_1] = 0
			# Loop over secondary tile types for the probabilities
			for tile_type_2 in self._needed_tile_types:
				neighbor_probs_per_tile[tile_type_1][tile_type_2] = 0

		# Convert the neighbor counts to probabilities of neighbor types
		for tile_type_1 in self._needed_tile_types:
			n_neighbors = sum(list(self._neighbor_counts_per_tile[tile_type_1].values()))
			for tile_type_2 in self._needed_tile_types:
				neighbor_probs_per_tile[tile_type_1][tile_type_2] = self._neighbor_counts_per_tile[tile_type_1][tile_type_2] / n_neighbors

		# Compute the Shannon entropy of each tile type's distribution
		for tile_type_1 in self._needed_tile_types:
			for tile_type_2 in self._needed_tile_types:
				entropy_by_tile[tile_type_1] += computeMarginalEntropy(neighbor_probs_per_tile[tile_type_1][tile_type_2])

		# Return the results
		return entropy_by_tile

	### Define functions for swapping two tiles in an attempt to improve the MSE between actual and target efficiency values ###
	def swapTiles(self, skew_power:Any = 1, reject_flag:bool = False, normalize_type:str = "static") -> dict:
		# Swap two tiles in an attempt to improve relevant entropy values, return a dictionary of relevant results
		# Verify the inputs
		assert isNumeric(skew_power, include_numpy_flag = True) == True, "CatanGeneratorTiling::swapTiles: Provided value for 'skew_power' must be numeric"
		assert 0 <= skew_power, "CatanGeneratorTiling::swapTiles: Provided value for 'skew_power' must be non-negative"
		assert type(reject_flag) == bool, "CatanGeneratorTiling::swapTiles: Provided value for 'reject_flag' must be a bool object"
		assert normalize_type in ["static", "dynamic"], "CatanGeneratorTiling::swapTiles: Provided value for 'normalize_type' must be 'static' or 'dynamic"

		# Initialize the dictionary of relevant results
		# Add in the provided inputs
		swap_results = {}
		swap_results["skew_power"] = skew_power
		swap_results["reject_flag"] = reject_flag
		swap_results["normalize_type"] = normalize_type
		# Add keys related to entropy values
		swap_results["pre_entropy_by_tile"] = None
		swap_results["post_entropy_by_tile"] = None
		# Add keys related to efficiency values
		swap_results["pre_efficiency_by_tile"] = None
		swap_results["post_efficiency_by_tile"] = None
		# Add keys related to error values
		swap_results["normalized_error_by_tile"] = None
		swap_results["pre_mean_squared_error"] = None
		swap_results["post_mean_squared_error"] = None
		# Add keys related to probabilities
		swap_results["probability_1_by_tile"] = None
		swap_results["probability_2_by_tile"] = None
		# Add keys related to selected indices
		swap_results["tile_type_1"] = None
		swap_results["tile_type_2"] = None
		swap_results["polygon_index_1"] = None
		swap_results["polygon_index_2"] = None
		# Add keys related to whether the swap was accepted
		swap_results["swap_accepted_flag"] = None

		# Compute the pre-swap entropy and efficiency (i.e. normalized entropy) values and add to the results dictionary
		# Get the needed entropy values for each distribution
		pre_entropy_by_tile = self.computeEntropyPerTileType()
		# Convert to the efficiency values
		pre_efficiency_by_tile = {}
		for tile_type in self._needed_tile_types:
			pre_efficiency_by_tile[tile_type] = pre_entropy_by_tile[tile_type] / self._maximum_entropy
		# Add these results to the dictionary
		swap_results["pre_entropy_by_tile"] = pre_entropy_by_tile
		swap_results["pre_efficiency_by_tile"] = pre_efficiency_by_tile

		# Compute the differences between actual and target efficiencies as the raw error values
		raw_error_by_tile = {}
		for tile_type in self._needed_tile_types:
			raw_error_by_tile[tile_type] = pre_efficiency_by_tile[tile_type] - TARGET_EFFICIENCY_PER_TUPLE[(self._game_mode, tile_type)]

		# Normalize these errors to be between 0 and 1 (i.e. 1 is for the most above, -1 is for the most below, 0.5 is exactly correct)
		# Fetch the largest magnitude raw error (needed for dynamic normalize type)
		max_abs_raw_error = max([abs(raw_error_by_tile[tile_type]) for tile_type in self._needed_tile_types])
		# Compute the normalized errors using the needed method
		normalized_error_by_tile = {}
		for tile_type in self._needed_tile_types:
			if normalize_type == "static":
				normalized_error_by_tile[tile_type] = 0.5 + raw_error_by_tile[tile_type] / 2
			else:
				normalized_error_by_tile[tile_type] = 0.5 + raw_error_by_tile[tile_type] / (2 * max_abs_raw_error)
		# Add these results to the dictionary
		swap_results["normalized_error_by_tile"] = normalized_error_by_tile

		# Compute the probability values for the 1st and 2nd tile type distributions using the provided skew power and add to the results dictionary
		# General idea: Tile type 1 should be a tile above its target efficiency, tile type 2 should be a tile below its target efficiency
		# Initialize the needed dictionaries
		pseudo_probability_1_by_tile = {}
		pseudo_probability_2_by_tile = {}
		probability_1_by_tile = {}
		probability_2_by_tile = {}
		# Compute the minimum and maximum normalized errors (needed for infinite skew powers)
		min_normalized_error = min(list(normalized_error_by_tile.values()))
		max_normalized_error = max(list(normalized_error_by_tile.values()))
		# Loop over the tile types to get the pseudo-probabilities
		for tile_type in self._needed_tile_types:
			# When efficiency is higher than needed, make likely for tile type 1 and unlikely for tile type 2 (and vice versa)
			if skew_power < float("inf"):
				# For finite skew power, simply raise normalized error and 1 - normalized error to that power
				pseudo_probability_1_by_tile[tile_type] = normalized_error_by_tile[tile_type]**skew_power
				pseudo_probability_2_by_tile[tile_type] = (1 - normalized_error_by_tile[tile_type])**skew_power
			else:
				# In the limit, probability 1 will only be non-zero if the normalized error is the maximum value
				if normalized_error_by_tile[tile_type] == max_normalized_error:
					pseudo_probability_1_by_tile[tile_type] = 1
				else:
					pseudo_probability_1_by_tile[tile_type] = 0
				# In the limit, probability 2 will only be non-zero if the normalized error is the minimum value
				if normalized_error_by_tile[tile_type] == min_normalized_error:
					pseudo_probability_2_by_tile[tile_type] = 1
				else:
					pseudo_probability_2_by_tile[tile_type] = 0
		# Convert the pseudo-probabilities to probabilities by normalizing
		normalizer_1 = sum(list(pseudo_probability_1_by_tile.values()))
		normalizer_2 = sum(list(pseudo_probability_2_by_tile.values()))
		for tile_type in self._needed_tile_types:
			probability_1_by_tile[tile_type] = pseudo_probability_1_by_tile[tile_type] / normalizer_1
			probability_2_by_tile[tile_type] = pseudo_probability_2_by_tile[tile_type] / normalizer_2
		# Add these results to the dictionary
		swap_results["probability_1_by_tile"] = probability_1_by_tile
		swap_results["probability_2_by_tile"] = probability_2_by_tile

		# Randomly select the tile types to use in the swap and add to the results dictionary
		# Select the tile types and make sure they are distinct
		while True:
			tile_type_1 = str(random.choice(a = list(probability_1_by_tile.keys()), p = list(probability_1_by_tile.values())))
			tile_type_2 = str(random.choice(a = list(probability_2_by_tile.keys()), p = list(probability_2_by_tile.values())))
			if tile_type_1 != tile_type_2:
				break
		# Add these results to the dictionary
		swap_results["tile_type_1"] = tile_type_1
		swap_results["tile_type_2"] = tile_type_2

		# Get the indices of polygons associated with these tile types
		possible_indices_1 = [polygon_index for polygon_index in range(self._n_polygons) if self._tile_per_polygon[polygon_index] == tile_type_1]
		possible_indices_2 = [polygon_index for polygon_index in range(self._n_polygons) if self._tile_per_polygon[polygon_index] == tile_type_2]

		# Randomly select the indices to switch and add to the results dictionary
		# Select the polygon indices
		polygon_index_1 = int(random.choice(a = possible_indices_1))
		polygon_index_2 = int(random.choice(a = possible_indices_2))
		# Add these results to the dictionary
		swap_results["polygon_index_1"] = polygon_index_1
		swap_results["polygon_index_2"] = polygon_index_2

		# Perform the needed tile swap for these polygons by updating internal storage accordingly
		self._updateStorageDueToSwap(polygon_index_1 = polygon_index_1, polygon_index_2 = polygon_index_2)

		# Compute the post-swap entropy and efficiency (i.e. normalized entropy) values and add to the results dictionary
		# Get the needed entropy values for each distribution
		post_entropy_by_tile = self.computeEntropyPerTileType()
		# Convert to the efficiency values
		post_efficiency_by_tile = {}
		for tile_type in self._needed_tile_types:
			post_efficiency_by_tile[tile_type] = post_entropy_by_tile[tile_type] / self._maximum_entropy
		# Add these results to the dictionary
		swap_results["post_entropy_by_tile"] = post_entropy_by_tile
		swap_results["post_efficiency_by_tile"] = post_efficiency_by_tile

		# Compute the mean squared error for efficiency values relative to the target values and add to the results dictionary
		# Get the needed MSE values
		pre_mean_squared_error = 0
		post_mean_squared_error = 0
		denominator = len(self._needed_tile_types)
		for tile_type in self._needed_tile_types:
			pre_mean_squared_error += (TARGET_EFFICIENCY_PER_TUPLE[(self._game_mode, tile_type)] - pre_efficiency_by_tile[tile_type])**2 / denominator
			post_mean_squared_error += (TARGET_EFFICIENCY_PER_TUPLE[(self._game_mode, tile_type)] - post_efficiency_by_tile[tile_type])**2 / denominator
		# Add these results to the dictionary
		swap_results["pre_mean_squared_error"] = pre_mean_squared_error
		swap_results["post_mean_squared_error"] = post_mean_squared_error

		# Reject the change if it raised the mean squared error of efficiency (if needed)
		if reject_flag == True and post_mean_squared_error > pre_mean_squared_error:
			# Undo the changes and mark that the swap was rejected
			self._updateStorageDueToSwap(polygon_index_1 = polygon_index_1, polygon_index_2 = polygon_index_2)
			swap_results["swap_accepted_flag"] = False
		else:
			# Leave the changes and mark that the swap was accepted
			swap_results["swap_accepted_flag"] = True

		# Return the results
		return swap_results

	def _updateStorageDueToSwap(self, polygon_index_1:int, polygon_index_2:int):
		# Update the polygon tile type list and neighbor counts dictionary to reflect a swap occurring (note: input verification not done for efficiency)
		# Get the current tile types associated with these polygons
		tile_type_1 = self._tile_per_polygon[polygon_index_1]
		tile_type_2 = self._tile_per_polygon[polygon_index_2]

		# Lower the neighbor counts for type 1 before changing the 1st polygon
		for neighbor_polygon_index in self._neighbor_indices_per_polygon[polygon_index_1]:
			# Get the tile type for the neighbor
			neighbor_tile_type = self._tile_per_polygon[neighbor_polygon_index]

			# Unlink the neighbor type from type 1
			self._neighbor_counts_per_tile[neighbor_tile_type][tile_type_1] -= 1
			self._neighbor_counts_per_tile[tile_type_1][neighbor_tile_type] -= 1

		# Lower the neighbor counts for type 2 before changing the 2nd polygon
		for neighbor_polygon_index in self._neighbor_indices_per_polygon[polygon_index_2]:
			# Get the tile type for the neighbor
			neighbor_tile_type = self._tile_per_polygon[neighbor_polygon_index]

			# Unlink the neighbor type from type 2
			self._neighbor_counts_per_tile[neighbor_tile_type][tile_type_2] -= 1
			self._neighbor_counts_per_tile[tile_type_2][neighbor_tile_type] -= 1

		# Swap the types for the selected polygons
		self._tile_per_polygon[polygon_index_1] = tile_type_2
		self._tile_per_polygon[polygon_index_2] = tile_type_1

		# Raise the neighbor counts for type 2 after changing the 1st polygon
		for neighbor_polygon_index in self._neighbor_indices_per_polygon[polygon_index_1]:
			# Get the tile type for the neighbor
			neighbor_tile_type = self._tile_per_polygon[neighbor_polygon_index]

			# Link the neighbor type to type 2
			self._neighbor_counts_per_tile[neighbor_tile_type][tile_type_2] += 1
			self._neighbor_counts_per_tile[tile_type_2][neighbor_tile_type] += 1

		# Raise the neighbor counts for type 1 after changing the 2nd polygon
		for neighbor_polygon_index in self._neighbor_indices_per_polygon[polygon_index_2]:
			# Get the tile type for the neighbor
			neighbor_tile_type = self._tile_per_polygon[neighbor_polygon_index]

			# Link the neighbor type to type 1
			self._neighbor_counts_per_tile[neighbor_tile_type][tile_type_1] += 1
			self._neighbor_counts_per_tile[tile_type_1][neighbor_tile_type] += 1

	### Define an external function for rendering the tiling ###
	def render(self, dpi:int) -> Image.Image:
		# Return a PIL image render of the tiling for the Catan board
		# Assign the correct colors to each polygon
		for polygon_index in range(self._n_polygons):
			selected_tile_type = self._tile_per_polygon[polygon_index]
			self._board.setTintShade(tint_shade = COLOR_PER_TILE[selected_tile_type], polygon_index = polygon_index)

		# Create the rendered image and return it
		return self._board.render(dpi = dpi)


############################################
### Define the board generator GUI class ###
############################################
# Create the decorator needed for making the attributes private
catan_generator_gui_decorator = privacyDecorator(["_used_canvas",					# class variables
												  "_used_window",
												  "_BACKGROUND_COLOR_DARK",			# class constants
												  "_BACKGROUND_COLOR_LIGHT",
												  "_FOREGROUND_COLOR_DARK",
												  "_FOREGROUND_COLOR_LIGHT"])

# Define the class with private attributes
@catan_generator_gui_decorator
class CatanGeneratorGUI:
	### Define class constants ###
	_BACKGROUND_COLOR_DARK = RGB("#cccccc")
	_BACKGROUND_COLOR_LIGHT = RGB("#eeeeee")
	_FOREGROUND_COLOR_DARK = RGB("#000000")
	_FOREGROUND_COLOR_LIGHT = RGB("#ffffff")

	### Initialize the class ###
	def __init__(self):
		# Create the frame and canvas for this class
		self._used_window = createWindow(width_parameter = 0.9,
										 height_parameter = 0.85,
										 title = "Settlers Of Catan - Board Generator")
		self._used_canvas = createCanvas(used_window = self._used_window,
										 fill_color = self._BACKGROUND_COLOR_DARK)

		# Create the needed section rectangles
		createRectangle(used_canvas = self._used_canvas,
						tl_x_parameter = 0.00,
						tl_y_parameter = 0.00,
						br_x_parameter = 0.24,
						br_y_parameter = 0.22,
						fill_color = self._BACKGROUND_COLOR_LIGHT)
		createRectangle(used_canvas = self._used_canvas,
						tl_x_parameter = 0.00,
						tl_y_parameter = 0.22,
						br_x_parameter = 0.24,
						br_y_parameter = 0.48,
						fill_color = self._BACKGROUND_COLOR_LIGHT)
		createRectangle(used_canvas = self._used_canvas,
						tl_x_parameter = 0.00,
						tl_y_parameter = 0.48,
						br_x_parameter = 0.24,
						br_y_parameter = 0.74,
						fill_color = self._BACKGROUND_COLOR_LIGHT)
		createRectangle(used_canvas = self._used_canvas,
						tl_x_parameter = 0.00,
						tl_y_parameter = 0.74,
						br_x_parameter = 0.24,
						br_y_parameter = 1.00,
						fill_color = self._BACKGROUND_COLOR_LIGHT)

if __name__ == "__main__":
	#game_mode = "Original: 5 Wide"
	#game_mode = "Original: 6 Wide"
	#game_mode = "Seafarers: 6 Wide"
	#game_mode = "Seafarers: 7 Wide"
	#game_mode = "Seafarers: 8 Wide"
	#game_mode = "Seafarers: 9 Wide"
	game_mode = "Seafarers: 10 Wide"

	from tqdm import tqdm

	seed = 24
	dpi = 300

	tiling = CatanGeneratorTiling(game_mode = game_mode, seed = seed)
	tiling.preprocessAllBevelInfo(bevel_attitude = CATAN_BEVEL_ATTITUDE, bevel_size = CATAN_BEVEL_SIZE)
	tiling.preprocessAllSunInfo(sun_angle = CATAN_SUN_ANGLE, sun_attitude = CATAN_SUN_ATTITUDE)
	tiling.render(dpi = dpi).save("pre.png")

	for index in tqdm(range(8000)):
		tiling.swapTiles(skew_power = 0.5, reject_flag = True)

	#tiling.render(dpi = dpi).show()
	tiling.render(dpi = dpi).save("post.png")