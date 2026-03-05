##########################################
### Import needed general dependencies ###
##########################################
# Add paths for internal modules
# Import dependencies
from pathlib import Path
from sys import path
# Get the shared active projects folder
active_projects_folder = Path(__file__).parent.parent
# Get the shared parent folder
parent_folder = active_projects_folder.parent
# Get the shared infrastructure folder
infrastructure_folder = parent_folder.joinpath("infrastructure")
# Add the needed paths
path.insert(0, str(infrastructure_folder.joinpath("common_needs")))
path.insert(0, str(infrastructure_folder.joinpath("dimensional_analysis")))

# Internal modules
from persistent_dimension import estimatePointwiseDimension, generateDimensionDatabase, plotDimensionEstimateOfSet
from sqlite3_helper import getColumnNames, getColumnTypes, getExistingTables, getRowCount, readRow
from tkinter_helper import askOpenFilename

# External modules
from numpy import array
from tqdm import tqdm


#################################################
### Load the efficiency database and parse it ###
#################################################
# Set the names of the possible tile types
all_tile_types = ["brick", "sheep", "stone", "wheat", "wood", "desert", "gold", "water"]

# Set the theoretical contents of the db file
table_name = "sim_results"
column_names = ["sim_index", "step_index", "tile_type_1", "tile_type_2", "pre_mean_squared_error", "post_mean_squared_error", "delta_mean_squared_error"]
column_types = ["BIGINT", "BIGINT", "TEXT", "TEXT", "FLOAT", "FLOAT", "FLOAT"]
for tile_type in all_tile_types:
	column_names.append(tile_type + "_pre_efficiency")
	column_types.append("FLOAT")

# Get a path from which the data should be loaded and make sure cancel wasn't clicked
db_path_efficiency = askOpenFilename(allowed_extensions = ["db"])
assert db_path_efficiency is not None, "Unable to read db file because cancel button was clicked"

# Verify that the db file has the needed information
# Make sure that only the needed table is present
actual_table_names = getExistingTables(db_path = db_path_efficiency)
assert len(actual_table_names) == 1, "Selected db file must have exactly 1 table in it"
assert actual_table_names[0] == table_name, "Selected db file must have only '" + table_name + "' as a table name"
# Make sure the column names match
actual_column_names = getColumnNames(db_path = db_path_efficiency, table_name = table_name)
assert len(actual_column_names) == len(column_names), "Table '" + table_name +  "' in selected db file must have exactly " + str(len(column_names)) + " column names"
for column_index in range(len(column_names)):
	assert actual_column_names[column_index] == column_names[column_index], "Table '" + table_name +  "' in selected db file must have the exactly the needed column names"
# Make sure the column types match
actual_column_types = getColumnTypes(db_path = db_path_efficiency, table_name = table_name)
assert len(actual_column_types) == len(column_types), "Table '" + table_name +  "' in selected db file must have exactly " + str(len(column_types)) + " column types"
for column_index in range(len(column_types)):
	assert actual_column_types[column_index] == column_types[column_index], "Table '" + table_name +  "' in selected db file must have the exactly the needed column types"

# Get the number of rows in the efficiency db file
n_rows = getRowCount(db_path = db_path_efficiency, table_name = table_name)

# Initialize the raw data as a list of lists as well as a hash table for the rows
raw_data_lists = []
added_row_hashes = []

# Iterate through the db file and store the needed efficiency values
for row_index in tqdm(range(n_rows)):
	# Read the needed row from the db file
	read_row = readRow(db_path = db_path_efficiency, table_name = table_name, row_index = row_index)

	# Extract the needed efficiency values from the read row
	new_row = read_row[7:]

	# Get the hash associated with this row
	row_hash = hash(tuple(new_row))

	# Add to the needed lists (if needed)
	if row_hash not in added_row_hashes:
		raw_data_lists.append(new_row)
		added_row_hashes.append(row_hash)

# Convert the raw data lists to a numpy array
raw_data_array = array(raw_data_lists, dtype = float)


######################################################################
### Perform the needed dimensional analysis on the efficiency data ###
######################################################################
# Set the needed softmax distance settings
all_softmax_distances = [0.4, 0.8, 1.6]
min_softmax_distance = 0.1
max_softmax_distance = 2.5
n_distances = 20

# Set the needed percent variance settings
all_percent_variances = [60, 75, 90]
min_percent_variance = 50
max_percent_variance = 90

# General plot settings
round_flag = False
show_flag = False
save_flag = True

# Generate the dimensional analysis db file
db_path_dimensional = generateDimensionDatabase(raw_data_array = raw_data_array,
												min_softmax_distance = min_softmax_distance,
												max_softmax_distance = max_softmax_distance,
												n_distances = n_distances)

# Generate the needed figures
for softmax_distance in all_softmax_distances:
	for percent_variance in all_percent_variances:
		# Create a scatter plot of the dimension estimate of each point given a fixed softmax distance and percent variance
		plotDimensionEstimateOfSet(db_path = db_path_dimensional,
								   softmax_distance = softmax_distance,
								   percent_variance = percent_variance,
								   plot_type = "scatter3D",
								   used_engine = "matplotlib",
								   round_flag = round_flag,
								   show_flag = show_flag,
								   save_flag = save_flag)

		# Create a distribution of the dimension estimates by percentile given a fixed softmax distance and percent variance
		plotDimensionEstimateOfSet(db_path = db_path_dimensional,
								   softmax_distance = softmax_distance,
								   percent_variance = percent_variance,
								   plot_type = "distribution",
								   used_engine = "matplotlib",
								   round_flag = round_flag,
								   show_flag = show_flag,
								   save_flag = save_flag)