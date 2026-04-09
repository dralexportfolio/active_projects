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
from math import sqrt

# Internal modules
from catan_board_generator import ALL_TILE_TYPES, CatanGeneratorTiling
from color_helper import ALL_PLOTLY_COLOR_SCALES_BY_TYPE, customSpectrum
from sqlite3_helper import addTable, appendRow, ConnectionManager, getRowCount, readColumn, readEntry
from tkinter_helper import askSaveFilename

# External modules
from numpy import corrcoef, quantile
import plotly.graph_objects as go
from tqdm import tqdm


######################################################
### Define parameters related to the entropy study ###
######################################################
# Define the random seed to use
seed = 0

# Game mode to use
game_mode = "Seafarers: 8 Wide"

# Swap settings
skew_power = 0
reject_flag = True
normalize_type = "static"

# Number of simulations to run and number of swaps to run per simulation
n_simulations = 20
n_steps_per_simulation = 1000


#################################################################
### Set up the db file required for saving simulation results ###
#################################################################
# Get a path to which the data should be saved and make sure cancel wasn't clicked
db_path = askSaveFilename(allowed_extensions = ["db"])
assert db_path is not None, "Unable to create db file because cancel button was clicked"

# Create a connection manager to associate with the db file
connection_manager = ConnectionManager(db_path = db_path)

# Set the table name for the simulation results
table_name = "sim_results"

# Set the column names and types for this table
column_names = ["sim_index", "step_index", "tile_type_1", "tile_type_2", "pre_mean_squared_error", "post_mean_squared_error", "delta_mean_squared_error"]
column_types = ["BIGINT", "BIGINT", "TEXT", "TEXT", "FLOAT", "FLOAT", "FLOAT"]
for tile_type in ALL_TILE_TYPES:
	column_names.append(tile_type + "_pre_efficiency")
	column_types.append("FLOAT")
for tile_type in ALL_TILE_TYPES:
	column_names.append(tile_type + "_normalized_error")
	column_types.append("FLOAT")

# Create the needed table in the db file
addTable(connection_manager = connection_manager, table_name = table_name, column_names = column_names, column_types = column_types)


######################################################################
### Run the needed simulations and save the results to the db file ###
######################################################################
for sim_index in tqdm(range(n_simulations)):
	# Create the tiling to use for this simulation
	current_tiling = CatanGeneratorTiling(game_mode = game_mode, seed = seed)

	# Randomly swap tiles for the needed number of simulation steps
	for step_index in range(n_steps_per_simulation):
		# Execute a random swap and get the needed results
		swap_results = current_tiling.swapTiles(skew_power = skew_power, reject_flag = reject_flag, normalize_type = normalize_type)

		# Extract the needed values from the swap results
		tile_type_1 = swap_results["tile_type_1"]
		tile_type_2 = swap_results["tile_type_2"]
		pre_mean_squared_error = swap_results["pre_mean_squared_error"]
		post_mean_squared_error = swap_results["post_mean_squared_error"]
		pre_efficiency_by_tile = swap_results["pre_efficiency_by_tile"]
		normalized_error_by_tile = swap_results["normalized_error_by_tile"]

		# Compute the change in mean squared error
		delta_mean_squared_error = post_mean_squared_error - pre_mean_squared_error

		# Write the needed information to the db file (if needed)
		if reject_flag == False or delta_mean_squared_error < 0:
			# Get the row index for the new row
			row_index = getRowCount(connection_manager = connection_manager, table_name = table_name)

			# Create a list containing the new row information
			new_row = [sim_index, step_index, tile_type_1, tile_type_2, pre_mean_squared_error, post_mean_squared_error, delta_mean_squared_error]
			for tile_type in ALL_TILE_TYPES:
				new_row.append(pre_efficiency_by_tile[tile_type])
			for tile_type in ALL_TILE_TYPES:
				new_row.append(normalized_error_by_tile[tile_type])

			# Add the row to the db file
			appendRow(connection_manager = connection_manager, table_name = table_name, new_row = new_row)

	# Iterate the random seed (if needed)
	if seed is not None:
		seed += 1

# Commit changes to db file now that the simulations are done
connection_manager.commit()

##########################################################
### Read important shared information from the db file ###
##########################################################
# Get the total number of rows from the db file
n_rows = getRowCount(connection_manager = connection_manager, table_name = table_name)

# Read the change in MSE column from the db file
delta_mean_squared_error_column = readColumn(connection_manager = connection_manager, table_name = table_name, column_name = "delta_mean_squared_error")

# Read the tile type columns from the db file
tile_type_1_column = readColumn(connection_manager = connection_manager, table_name = table_name, column_name = "tile_type_1")
tile_type_2_column = readColumn(connection_manager = connection_manager, table_name = table_name, column_name = "tile_type_2")

# Read the normalized error columns for each tile type
normalized_error_column_by_tile = {}
for tile_type in ALL_TILE_TYPES:
	normalized_error_column_by_tile[tile_type] = readColumn(connection_manager = connection_manager, table_name = table_name, column_name = tile_type + "_normalized_error")

# Close the connection manager
connection_manager.close()


#########################################################
### Analyze the simulations and create relevant plots ###
#########################################################
# Initialize the needed storage
delta_values_by_quantile = {0: [], 1: [], 2: [], 3: []}
normalized_error_1_values_by_quantile = {0: [], 1: [], 2: [], 3: []}
normalized_error_2_values_by_quantile = {0: [], 1: [], 2: [], 3: []}
distances_from_equal = []

# Get the quantile information from the delta column
quantile_values = quantile(a = delta_mean_squared_error_column, q = [0, 0.25, 0.5, 0.75, 1])

# Compute the maximum magnitude delta MSE value from the db file
max_abs_delta = max(abs(max(delta_mean_squared_error_column)), abs(min(delta_mean_squared_error_column)))

# Read the needed information from the table
for row_index in tqdm(range(n_rows)):
	# Get the change in mean squared error associated with this swap
	delta_mean_squared_error = delta_mean_squared_error_column[row_index]

	# Determine to which quantile the relevant data should be added
	if quantile_values[0] <= delta_mean_squared_error and delta_mean_squared_error < quantile_values[1]:
		quantile_index = 0
	elif quantile_values[1] <= delta_mean_squared_error and delta_mean_squared_error <= quantile_values[2]:
		quantile_index = 1
	elif quantile_values[2] <= delta_mean_squared_error and delta_mean_squared_error <= quantile_values[3]:
		quantile_index = 2
	else:
		quantile_index = 3

	# Get the two tile types involved with this swap
	tile_type_1 = tile_type_1_column[row_index]
	tile_type_2 = tile_type_2_column[row_index]

	# Get the associated normalized error values for these tile types
	normalized_error_1 = normalized_error_column_by_tile[tile_type_1][row_index]
	normalized_error_2 = normalized_error_column_by_tile[tile_type_2][row_index]

	# Append to the needed lists
	delta_values_by_quantile[quantile_index].append(delta_mean_squared_error)
	normalized_error_1_values_by_quantile[quantile_index].append(normalized_error_1)
	normalized_error_2_values_by_quantile[quantile_index].append(normalized_error_2)
	distances_from_equal.append(abs(normalized_error_1 - normalized_error_2) / sqrt(2))

# Print the correlation coefficient between these two columns
# Note: hypothesis is that LARGER DISTANCE should result in MORE NEGATIVE delta in MSE
print("Correlation Coefficient Between Diagonal Distance And Decrease In MSE ---> " + str(-float(corrcoef(distances_from_equal, delta_mean_squared_error_column)[0, 1])))

# Set the color scale and color bound values as needed
if reject_flag == False:
	rgb_spectrum = ALL_PLOTLY_COLOR_SCALES_BY_TYPE["diverging"]["Portland"]
	color_function = lambda index: customSpectrum(parameter = index / 100, rgb_spectrum = rgb_spectrum)
	color_scale = [[index / 100, color_function(index).asStringTuple()] for index in range(101)]
	c_min = -max_abs_delta
	c_max = max_abs_delta
else:
	rgb_spectrum = ALL_PLOTLY_COLOR_SCALES_BY_TYPE["sequential"]["YlGnBu"]
	color_function = lambda index: customSpectrum(parameter = 1 - index / 100, rgb_spectrum = rgb_spectrum)
	color_scale = [[index / 100, color_function(index).asStringTuple()] for index in range(101)]
	c_min = -max_abs_delta
	c_max = 0

# Set the title suffixes for each quantile
suffixes_by_quantile = ["75th To 100th Percentile",
						"50th To 75th Percentile",
						"25th To 50th Percentile",
						"0th To 25th Percentile"]

# Create scatter plots showing how efficiency values affect delta values
for quantile_index in range(4):
	# Create the figure
	fig = go.Figure()

	# Add the needed traces
	fig.add_trace(go.Scatter(x = normalized_error_1_values_by_quantile[quantile_index],
							 y = normalized_error_2_values_by_quantile[quantile_index],
							 showlegend = False,
							 customdata = delta_values_by_quantile[quantile_index],
							 hovertemplate = ("<b>Normalized Error 1:</b> %{x}<br>"
											  "<b>Normalized Error 2:</b> %{y}<br>"
											  "<b>Delta Mean Squared Error:</b> %{customdata}<br>"
											  "<extra></extra>"),
							 mode = "markers",
							 marker = {"color": delta_values_by_quantile[quantile_index],
									   "colorscale": color_scale,
									   "showscale": True,
									   "cmin": c_min,
									   "cmax": c_max}))

	# Format the figure
	fig.update_layout(title = "Change In Mean Squared Error As Function Of Normalized Error Values (" + suffixes_by_quantile[quantile_index] + ")",
					  xaxis = {"range": [-0.05, 1.05]}, yaxis = {"range": [-0.05, 1.05]})
	fig.update_xaxes(title = "normalized error 1")
	fig.update_yaxes(title = "normalized error 2")
	
	# Show the figure
	fig.show()