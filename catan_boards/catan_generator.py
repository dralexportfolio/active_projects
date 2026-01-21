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


#####################################################
### Define important shared settings for the game ###
#####################################################
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
	"wheat": RGB((230, 200, 20)),
	"wood": RGB((10, 80, 10)),
	"desert": RGB((230, 210, 150)),
	"gold": RGB((160, 140, 50)),
	"water": RGB((80, 210, 240))
}