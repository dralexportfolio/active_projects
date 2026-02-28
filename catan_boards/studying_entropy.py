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
from color_helper import ALL_PLOTLY_COLOR_SCALES_BY_TYPE, customSpectrum, RGB
from Polygon import HEXAGON_REGULAR_TALL
from sqlite3_helper import addTable, appendRow, getRowCount, readColumn, readEntry, replaceRow
from tkinter_helper import askSaveFilename
from type_helper import tolerantlyCompare

# External modules
from math import log2, sqrt
from numpy import random
import plotly.graph_objects as go
from tqdm import tqdm


######################################################
### Define parameters related to the entropy study ###
######################################################
# Flag for rejecting bad changes
reject_flag = False

# Number of simulations to run and number of swaps to run per simulation
N_SIMULATIONS = 10
N_STEPS_PER_SIMULATION = 1000

# Number of hexagons per side of board
N_HEXAGONS_PER_SIDE = 5

# Set the names of the possible tile types
ALL_TILE_TYPES = ["brick", "sheep", "stone", "wheat", "wood", "desert", "gold", "water"]

# Tile types and likelihoods
LIKELIHOOD_PER_TILE = {
	"brick": 0.1,
	"sheep": 0.1,
	"stone": 0.1,
	"wheat": 0.1,
	"wood": 0.1,
	"desert": 0.05,
	"gold": 0.05,
	"water": 0.4
}

# Define the entropy weights by tile type
ENTROPY_WEIGHT_BY_TILE = {
	"brick": 1,
	"sheep": 1,
	"stone": 1,
	"wheat": 1,
	"wood": 1,
	"desert": 1,
	"gold": 1,
	"water": 1
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

# Define the default bevel and sun information
BEVEL_ATTITUDE = 25
BEVEL_SIZE = 0.1
SUN_ANGLE = 120
SUN_ATTITUDE = 35

# Board rendering information
debug_flag = False
dpi = 600


###############################################################################
### Perform the setup required for creating the overall layout of the board ###
###############################################################################
# Set the number of hexagons in each row of the board
row_counts = []
for index in range(N_HEXAGONS_PER_SIDE):
	row_counts.append(N_HEXAGONS_PER_SIDE + index)
for index in range(N_HEXAGONS_PER_SIDE - 1):
	row_counts.append(2 * N_HEXAGONS_PER_SIDE - index - 2)

# Set the number of polygons based on the row counts
n_polygons = sum(row_counts)

# Create a list of all polygons objects to be passed to the Board object
all_polygons = [HEXAGON_REGULAR_TALL for _ in range(n_polygons)]

# Create the lists of x-value and y-value shifts associated with each polygon
x_shift_per_polygon = []
y_shift_per_polygon = []
for row_index in range(len(row_counts)):
	y_shift = 3 / 2 * row_index
	for col_index in range(row_counts[row_index]):
		x_shift = sqrt(3) * (col_index - row_counts[row_index] / 2)
		x_shift_per_polygon.append(x_shift)
		y_shift_per_polygon.append(y_shift)

# Create and store the Board object for the tiling
board = Board(n_polygons = n_polygons,
			  all_polygons = all_polygons,
			  x_shift_per_polygon = x_shift_per_polygon,
			  y_shift_per_polygon = y_shift_per_polygon)

# Apply the selected bevel and sun information to the board
board.preprocessBevelInfo(bevel_attitude = BEVEL_ATTITUDE, bevel_size = BEVEL_SIZE)
board.preprocessAllSunInfo(sun_angle = SUN_ANGLE, sun_attitude = SUN_ATTITUDE)

# Display the board for debugging (if needed)
if debug_flag == True:
	board.render(dpi = dpi).show()

# Determine the indices adjacent to each polygon on the board
# Initialize the needed storage
neighbor_indices_per_polygon = {}
for polygon_index in range(n_polygons):
	neighbor_indices_per_polygon[polygon_index] = []
# Compute the theoretically correct distance for adjacent polygons
theoretical_distance = sqrt(3)
# Mark which polygons are adjacent to which other polygons
for polygon_index_1 in range(n_polygons - 1):
	# Get the x-shift and y-shift for the 1st polygon
	x_shift_1 = x_shift_per_polygon[polygon_index_1]
	y_shift_1 = y_shift_per_polygon[polygon_index_1]
	# Loop over the needed other polygons
	for polygon_index_2 in range(polygon_index_1 + 1, n_polygons):
		# Get the x-shift and y-shift for the 2nd polygon
		x_shift_2 = x_shift_per_polygon[polygon_index_2]
		y_shift_2 = y_shift_per_polygon[polygon_index_2]
		# Compute the actual distances between the centers of these polygons
		actual_distance = sqrt((x_shift_1 - x_shift_2)**2 + (y_shift_1 - y_shift_2)**2)
		# Mark that the polygons are adjacent if the distance is correct (within a margin of error)
		if tolerantlyCompare(actual_distance, "==", theoretical_distance, threshold = 10**-3):
			neighbor_indices_per_polygon[polygon_index_1].append(polygon_index_2)
			neighbor_indices_per_polygon[polygon_index_2].append(polygon_index_1)


#################################################################
### Set up the db file required for saving simulation results ###
#################################################################
# Get a path to which the data should be saved and make sure cancel wasn't clicked
db_path = askSaveFilename(allowed_extensions = ["db"])
assert db_path is not None, "Unable to create db file because cancel button was clicked"

# Set the table name for the simulation results
table_name = "sim_results"

# Set the column names and types for this table
column_names = ["sim_index", "step_index", "tile_type_1", "tile_type_2", "pre_total_weighted_entropy", "post_total_weighted_entropy", "delta_total_weighted_entropy"]
column_types = ["BIGINT", "BIGINT", "TEXT", "TEXT", "FLOAT", "FLOAT", "FLOAT"]
for tile_type in ALL_TILE_TYPES:
	column_names.append(tile_type + "_pre_efficiency")
	column_types.append("FLOAT")

# Create the needed table in the db file
addTable(db_path = db_path, table_name = table_name, column_names = column_names, column_types = column_types)


######################################################################
### Run the needed simulations and save the results to the db file ###
######################################################################
# Define function for computing the entropy information of a given tiling
def computeEntropyInfo(needed_tile_types:list, tile_per_polygon:list) -> dict:
	# Verify the inputs
	# Needed tile types
	assert type(needed_tile_types) == list, "computeEntropyInfo: Provided value for 'computeEntropyInfo' must be a list object"
	assert len(needed_tile_types) == len(set(needed_tile_types)), "computeEntropyInfo: Provided value for 'computeEntropyInfo' must be a list of distinct entries"
	assert len(needed_tile_types) >= 2, "computeEntropyInfo: Provided value for 'computeEntropyInfo' must be a list with at least two entries"
	for value in needed_tile_types:
		assert value in ALL_TILE_TYPES, "computeEntropyInfo: Provided value for 'computeEntropyInfo' must be a list with entries that are valid tile types"
	# Tile types for each polygon
	assert type(tile_per_polygon) == list, "computeEntropyInfo: Provided value for 'tile_per_polygon' must be a list object"
	assert len(tile_per_polygon) == n_polygons, "computeEntropyInfo: Provided value for 'tile_per_polygon' must be a list of length equal to the number of polygons"
	assert set(tile_per_polygon) == set(needed_tile_types), "computeEntropyInfo: Provided value for 'tile_per_polygon' must have exactly the entries contained in 'needed_tile_types'"

	# Initialize the needed storage dictionaries
	# Initialize the main dictionaries
	count_results = {}
	probability_results = {}
	entropy_by_tile = {}
	efficiency_by_tile = {}
	# Loop over the needed tile types and add more information
	for tile_type_1 in needed_tile_types:
		# Add in the storage at this level
		count_results[tile_type_1] = {}
		probability_results[tile_type_1] = {}
		entropy_by_tile[tile_type_1] = 0
		efficiency_by_tile[tile_type_1] = 0
		# Loop over secondary tile types for the counts and probabilities
		for tile_type_2 in needed_tile_types:
			count_results[tile_type_1][tile_type_2] = 0
			probability_results[tile_type_1][tile_type_2] = 0

	# Count the number of neighbors of each tile type belonging to each type of tile
	for polygon_index_1 in range(n_polygons):
		tile_type_1 = tile_per_polygon[polygon_index_1]
		for polygon_index_2 in neighbor_indices_per_polygon[polygon_index_1]:
			tile_type_2 = tile_per_polygon[polygon_index_2]
			count_results[tile_type_1][tile_type_2] += 1

	# Convert the neighbor counts to probabilities of neighbor types
	for tile_type_1 in needed_tile_types:
		n_neighbors = sum(list(count_results[tile_type_1].values()))
		for tile_type_2 in needed_tile_types:
			probability_results[tile_type_1][tile_type_2] = count_results[tile_type_1][tile_type_2] / n_neighbors

	# Compute the Shannon entropy of each tile type's distribution
	for tile_type_1 in needed_tile_types:
		for tile_type_2 in needed_tile_types:
			prob_value = probability_results[tile_type_1][tile_type_2]
			if prob_value not in [0, 1]:
				entropy_by_tile[tile_type_1] += prob_value * log2(1 / prob_value)

	# Compute the efficiency (i.e. normalized entropy) of each tile type's distribution
	for tile_type in needed_tile_types:
		efficiency_by_tile[tile_type] = entropy_by_tile[tile_type] / log2(len(needed_tile_types))

	# Compute the total weighted entropy using the needed values
	total_weighted_entropy = 0
	for tile_type in needed_tile_types:
		total_weighted_entropy += ENTROPY_WEIGHT_BY_TILE[tile_type] * entropy_by_tile[tile_type]

	# Construct the dictionary of results
	all_entropy_results = {
		"count_results": count_results,
		"probability_results": probability_results,
		"entropy_by_tile":  entropy_by_tile,
		"efficiency_by_tile": efficiency_by_tile,
		"total_weighted_entropy": total_weighted_entropy
	}

	# Return the results
	return all_entropy_results

# Execute the simulation and write the needed information to the db file
for sim_index in tqdm(range(N_SIMULATIONS)):
	# Create a random initial tiling of the board using the probabilities
	tile_per_polygon = []
	for _ in range(n_polygons):
		selected_tile_type = random.choice(a = list(LIKELIHOOD_PER_TILE.keys()), p = list(LIKELIHOOD_PER_TILE.values()))
		tile_per_polygon.append(selected_tile_type)

	# Get the tile types which actually appear in this particular tiling
	needed_tile_types = [tile_type for tile_type in ALL_TILE_TYPES if tile_type in tile_per_polygon]

	# Randomly swap tiles for the needed number of simulation steps
	for step_index in range(N_STEPS_PER_SIMULATION):
		# Compute all relevant pre-swap entropy information
		pre_all_entropy_results = computeEntropyInfo(needed_tile_types = needed_tile_types, tile_per_polygon = tile_per_polygon)

		# Randomly select two tile types to be swapped
		tile_type_1 = None
		tile_type_2 = None
		while tile_type_1 == tile_type_2:
			tile_type_1 = random.choice(a = needed_tile_types)
			tile_type_2 = random.choice(a = needed_tile_types)

		# Get the indices of polygons associated with these tile types
		possible_indices_1 = [polygon_index for polygon_index in range(n_polygons) if tile_per_polygon[polygon_index] == tile_type_1]
		possible_indices_2 = [polygon_index for polygon_index in range(n_polygons) if tile_per_polygon[polygon_index] == tile_type_2]

		# Randomly select the indices to switch
		polygon_index_1 = random.choice(a = possible_indices_1)
		polygon_index_2 = random.choice(a = possible_indices_2)

		# Perform the needed tile swap for these polygons
		tile_per_polygon[polygon_index_1] = tile_type_2
		tile_per_polygon[polygon_index_2] = tile_type_1

		# Compute all relevant post-swap entropy information
		post_all_entropy_results = computeEntropyInfo(needed_tile_types = needed_tile_types, tile_per_polygon = tile_per_polygon)

		# Undo the changes in the case of a bad swap(if needed)
		if reject_flag == True and post_all_entropy_results["total_weighted_entropy"] < pre_all_entropy_results["total_weighted_entropy"]:
			tile_per_polygon[polygon_index_1] = tile_type_1
			tile_per_polygon[polygon_index_2] = tile_type_2
			post_all_entropy_results = pre_all_entropy_results

		# Write the needed information to the db file
		# Get the row index for the new row
		row_index = getRowCount(db_path = db_path, table_name = table_name)
		# Create a list containing the new row information
		new_row = [sim_index, step_index, tile_type_1, tile_type_2, pre_all_entropy_results["total_weighted_entropy"], post_all_entropy_results["total_weighted_entropy"],
				   post_all_entropy_results["total_weighted_entropy"] - pre_all_entropy_results["total_weighted_entropy"]]
		for tile_type in ALL_TILE_TYPES:
			if tile_type in needed_tile_types:
				new_row.append(pre_all_entropy_results["efficiency_by_tile"][tile_type])
			else:
				new_row.append(0)
		# Add the new row to the db file
		appendRow(db_path = db_path, table_name = table_name)
		replaceRow(db_path = db_path, table_name = table_name, row_index = row_index, new_row = new_row)


#########################################################
### Analyze the simulations and create relevant plots ###
#########################################################
# Initialize the needed storage
all_delta_values = []
all_efficiency_1_values = []
all_efficiency_2_values = []
all_color_values = []

# Compute the maximum magnitude delta value in the db file
delta_column = readColumn(db_path = db_path, table_name = table_name, column_name = "delta_total_weighted_entropy")
max_abs_delta = max(abs(max(delta_column)), abs(min(delta_column)))

# Get the total number of rows from the db file
n_rows = getRowCount(db_path = db_path, table_name = table_name)

# Read the needed information from the table
for row_index in range(n_rows):
	# Get the change in total weighted entropy associated with this swap
	delta_total_weighted_entropy = readEntry(db_path = db_path, table_name = table_name, column_name = "delta_total_weighted_entropy", row_index = row_index)

	# Proceed with the analysis (if needed)
	if reject_flag == False or delta_total_weighted_entropy > 0:
		# Get the two tile types involved with this swap
		tile_type_1 = readEntry(db_path = db_path, table_name = table_name, column_name = "tile_type_1", row_index = row_index)
		tile_type_2 = readEntry(db_path = db_path, table_name = table_name, column_name = "tile_type_2", row_index = row_index)

		# Get the associated efficient values for these tile types
		efficiency_1 = readEntry(db_path = db_path, table_name = table_name, column_name = tile_type_1 + "_pre_efficiency", row_index = row_index)
		efficiency_2 = readEntry(db_path = db_path, table_name = table_name, column_name = tile_type_2 + "_pre_efficiency", row_index = row_index)

		# Append to the needed lists
		all_delta_values.append(delta_total_weighted_entropy)
		all_efficiency_1_values.append(efficiency_1)
		all_efficiency_2_values.append(efficiency_2)

# Set the color scale and color bound values as needed
if reject_flag == False:
	rgb_spectrum = ALL_PLOTLY_COLOR_SCALES_BY_TYPE["diverging"]["Portland"]
	color_function = lambda index: customSpectrum(parameter = 1 - index / 100, rgb_spectrum = rgb_spectrum)
	color_scale = [[index / 100, color_function(index).asStringTuple()] for index in range(101)]
	c_min = -max_abs_delta
	c_max = max_abs_delta
else:
	rgb_spectrum = ALL_PLOTLY_COLOR_SCALES_BY_TYPE["sequential"]["Blues"]
	color_function = lambda index: customSpectrum(parameter = index / 100, rgb_spectrum = rgb_spectrum)
	color_scale = [[index / 100, color_function(index).asStringTuple()] for index in range(101)]
	c_min = 0
	c_max = max_abs_delta

# Create a scatter plot showing how efficiency values affect delta values
# Create the figure
fig = go.Figure()
# Add the needed traces
fig.add_trace(go.Scatter(x = all_efficiency_1_values,
						 y = all_efficiency_2_values,
						 showlegend = False,
						 customdata = all_delta_values,
						 hovertemplate = ("<b>Pre-Swap Efficiency 1:</b> %{x}<br>"
										  "<b>Pre-Swap Efficiency 2:</b> %{y}<br>"
										  "<b>Delta Total Weighted Entropy:</b> %{customdata}<br>"
										  "<extra></extra>"),
						 mode = "markers",
						 marker = {"color": all_delta_values,
								   "colorscale": color_scale,
								   "showscale": True,
								   "cmin": c_min,
								   "cmax": c_max}))
# Format the figure
fig.update_layout(title = "Deltas In Total Weighted Entropy As Functions Of Efficiency Values")
fig.update_xaxes(title = "pre-swap efficiency 1")
fig.update_yaxes(title = "pre-swap efficiency 2")
# Show the figure
fig.show()