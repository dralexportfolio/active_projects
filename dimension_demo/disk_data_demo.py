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
path.insert(0, str(infrastructure_folder.joinpath("dimensional_analysis")))

# Internal modules
from persistent_dimension import estimatePointwiseDimension, generateDimensionDatabase, plotDimensionEstimateOfPoint, plotDimensionEstimateOfSet

# External modules
from math import cos, pi, sin, sqrt
from numpy import random


#################################
### Set the needed parameters ###
#################################
# Random seed
seed = 0

# Geometric settings
disk_radius = 1
noise_level = 0.05

# Number of points and parameters
n_points = 500
n_parameters = 5

# Softmax distance settings
softmax_distance = 0.8
min_softmax_distance = 0.1
max_softmax_distance = 2.5
n_distances = 20

# Percent variance settings
percent_variance = 75
min_percent_variance = 50
max_percent_variance = 90

# General plot settings
used_engine_2d = "matplotlib"
used_engine_3d = "plotly"
round_flag = False
show_flag = True
save_flag = False

# Single point plot settings
row_index_to_plot = 0
n_samples = 200

# All points plot settings
use_3d_flag = False


##############################
### Run the requested demo ###
##############################
# Set the random seed (if needed)
if seed is not None:
    random.seed(seed = seed)

# Generate the raw random data
raw_data_array = (2 * random.rand(n_points, n_parameters) - 1) * noise_level
for row_index in range(n_points):
    # Generate the radius and angle values
    radius_value = disk_radius * random.rand()**0.5
    angle_value = 2 * pi * random.rand()

    # Convert to x-value and y-value
    x_value = radius_value * cos(angle_value)
    y_value = radius_value * sin(angle_value)

    # Store the computed values
    raw_data_array[row_index, 0] += x_value
    raw_data_array[row_index, 1] += y_value

# Generate the dimension database and get the corresponding db file path
db_path = generateDimensionDatabase(raw_data_array = raw_data_array,
									min_softmax_distance = min_softmax_distance,
									max_softmax_distance = max_softmax_distance,
									n_distances = n_distances)

# Create a plot of the dimension estimate of the given point ranging over only percent variance
plotDimensionEstimateOfPoint(db_path = db_path,
							 row_index = row_index_to_plot,
							 min_softmax_distance = softmax_distance,
							 max_softmax_distance = softmax_distance,
							 min_percent_variance = min_percent_variance,
							 max_percent_variance = max_percent_variance,
							 n_samples = n_samples,
							 used_engine = used_engine_2d,
							 round_flag = round_flag,
							 show_flag = show_flag,
							 save_flag = save_flag)

# Create a plot of the dimension estimate of the given point ranging over only softmax distance
plotDimensionEstimateOfPoint(db_path = db_path,
							 row_index = row_index_to_plot,
							 min_softmax_distance = min_softmax_distance,
							 max_softmax_distance = max_softmax_distance,
							 min_percent_variance = percent_variance,
							 max_percent_variance = percent_variance,
							 n_samples = n_samples,
							 used_engine = used_engine_2d,
							 round_flag = round_flag,
							 show_flag = show_flag,
							 save_flag = save_flag)

# Create a plot of the dimension estimate of the given point ranging over both softmax distance and percent variance
plotDimensionEstimateOfPoint(db_path = db_path,
							 row_index = row_index_to_plot,
							 min_softmax_distance = min_softmax_distance,
							 max_softmax_distance = max_softmax_distance,
							 min_percent_variance = min_percent_variance,
							 max_percent_variance = max_percent_variance,
							 n_samples = n_samples,
							 used_engine = used_engine_3d,
							 round_flag = round_flag,
							 show_flag = show_flag,
							 save_flag = save_flag)

# Create a scatter plot of the dimension estimate of each point given a fixed softmax distance and percent variance
plotDimensionEstimateOfSet(db_path = db_path,
						   softmax_distance = softmax_distance,
						   percent_variance = percent_variance,
						   used_engine = used_engine_3d if use_3d_flag == True else used_engine_2d,
						   use_3d_flag = use_3d_flag,
						   show_flag = show_flag,
						   save_flag = save_flag)