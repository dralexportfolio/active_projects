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
from Board import Board
from color_helper import RGB
from Polygon import HEXAGON_REGULAR_TALL, Polygon
from tkinter_helper import createCanvas, createRectangle, createWindow
from type_helper import isNumeric

# External modules
from math import log2, sqrt
from numpy import random, zeros
from PIL import Image
from PrivateAttributesDecorator import private_attributes_dec


#####################################################
### Define important shared settings for the game ###
#####################################################
# Define the default bevel and sun information
BEVEL_ATTITUDE = 25
BEVEL_SIZE = 0.1
SUN_ANGLE = 120
SUN_ATTITUDE = 35

# Define the lists needed for parameter selection
ALL_GAME_MODES = ["Original: 3-4 Player", "Original: 5-6 Player", "Seafarers: 3-4 Player", "Seafarers: 5-6 Player"]

# Define a dictionary of number counts for each game mode
NUMBER_COUNTS_PER_MODE = {
	"Original: 3-4 Player": {		# 20 total
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
	"Original: 5-6 Player": {		# 28 total
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
	"Seafarers: 3-4 Player": {		# 28 total
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
	"Seafarers: 5-6 Player": {		# 32 total
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
	}
}

# Define a dictionary of tile count per row for each game mode
ROW_COUNTS_PER_MODE = {
	"Original: 3-4 Player": [3, 4, 5, 4, 3],
	"Original: 5-6 Player": [3, 4, 5, 6, 5, 4, 3],
	"Seafarers: 3-4 Player": [5, 6, 7, 6, 7, 6, 5],
	"Seafarers: 5-6 Player": [7, 8, 9, 8, 9, 8, 7]
}

# Define a dictionary of tile count per type for each game mode
TILE_COUNTS_PER_MODE = {
	"Original: 3-4 Player": {		# 19 total, 18 with numbers
		"brick": 3,
		"sheep": 4,
		"stone": 3,
		"wheat": 4,
		"wood": 4,
		"desert": 1,
		"gold": 0,
		"water": 0
	},
	"Original: 5-6 Player": {		# 30 total, 28 with numbers
		"brick": 5,
		"sheep": 6,
		"stone": 5,
		"wheat": 6,
		"wood": 6,
		"desert": 2,
		"gold": 0,
		"water": 0
	},
	"Seafarers: 3-4 Player": {		# 42 total, 25 with numbers
		"brick": 4,
		"sheep": 5,
		"stone": 4,
		"wheat": 5,
		"wood": 5,
		"desert": 1,
		"gold": 2,
		"water": 16
	},
	"Seafarers: 5-6 Player": {		# 56 total, 30 with numbers
		"brick": 5,
		"sheep": 6,
		"stone": 5,
		"wheat": 6,
		"wood": 6,
		"desert": 2,
		"gold": 2,
		"water": 24
	}
}

# Define the colors used for each tile
COLORS_PER_TILE = {
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

# Define a marginal Shannon entropy function for use with classes below
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
catan_generator_tiling_decorator = private_attributes_dec("_adjacency_matrix",		# class variables
														  "_board",
														  "_n_polygons",
														  "_tiles_per_index",
														  "_initializeTiling")		# private functions

# Define the class with private attributes
@catan_generator_tiling_decorator
class CatanGeneratorTiling:
	### Initialize the class ###
	def __init__(self, game_mode:str):
		# Verify the inputs
		assert game_mode in ALL_GAME_MODES, "CatanGeneratorTiling::__init__: Provided value for 'game_mode' must be contained in the list ALL_GAME_MODES"

		# Store the provided values
		self._game_mode = game_mode

		# Initialize a new tiling given the current game mode
		self._initializeTiling()

	### Define a function for randomly initializing the tiling information ###
	def _initializeTiling(self):
		# Set the number of polygons based onm the game mode
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

		# Create and store the Board object for the tiling
		self._board = Board(n_polygons = self._n_polygons,
			  				all_polygons = all_polygons,
			  				x_shift_per_polygon = x_shift_per_polygon,
			  				y_shift_per_polygon = y_shift_per_polygon)

		# Apply the selected bevel and sun information to the board
		self._board.preprocessBevelInfo(bevel_attitude = BEVEL_ATTITUDE, bevel_size = BEVEL_SIZE)
		self._board.preprocessAllSunInfo(sun_angle = SUN_ANGLE, sun_attitude = SUN_ATTITUDE)

		# Randomly assigning an initial tile selection to each polygon
		# Initialize the needed storage
		self._tiles_per_index = []
		# Create the list of currently selectable tiles given the current game mode
		possible_tiles = []
		for tile in TILE_COUNTS_PER_MODE[self._game_mode]:
			for _ in range(TILE_COUNTS_PER_MODE[self._game_mode][tile]):
				possible_tiles.append(tile)
		# Perform the tiling assignment to each polygon
		for polygon_index in range(self._n_polygons):
			# Select and tile and remove it from the list of possible tiles
			tile_index = random.randint(len(possible_tiles))
			selected_tile = possible_tiles.pop(tile_index)
			# Assign this tile to this polygon
			self._tiles_per_index.append(selected_tile)

		# Compute the adjacency matrix between the polygons on the board
		self._adjacency_matrix = zeros((self._n_polygons, self._n_polygons), dtype = int)

	### Define functions related to probability distributions for the current tiling ###

	### Define a function for rendering the tiling ###
	def render(self, dpi:int) -> Image.Image:
		# Return a PIL image render of the tiling for the Catan board
		# Assign the correct colors to each polygon
		for polygon_index in range(self._n_polygons):
			selected_tile = self._tiles_per_index[polygon_index]
			self._board.setTintShade(tint_shade = COLORS_PER_TILE[selected_tile], polygon_index = polygon_index)

		# Create the rendered image and return it
		return self._board.render(dpi = dpi)


############################################
### Define the board generator GUI class ###
############################################
# Create the decorator needed for making the attributes private
catan_generator_gui_decorator = private_attributes_dec("_used_canvas",					# class variables
												       "_used_window",
												       "_BACKGROUND_COLOR_DARK",		# class constants
												       "_BACKGROUND_COLOR_LIGHT",
												       "_FOREGROUND_COLOR_DARK",
												       "_FOREGROUND_COLOR_LIGHT")

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

#game_mode = "Original: 3-4 Player"
#game_mode = "Original: 5-6 Player"
#game_mode = "Seafarers: 3-4 Player"
game_mode = "Seafarers: 5-6 Player"

dpi = 600

CatanGeneratorTiling(game_mode = game_mode).render(dpi = dpi).show()
