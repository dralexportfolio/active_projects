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
from dimension_estimation import plotCumulativeVariances, plotMarginalVariances, visualizePointwiseEstimate
from persistent_dimension import estimatePointwiseDimension, generateDimensionDatabase, plotDimensionEstimateOfPoint

# External modules
from math import sqrt
from numpy import random


#################################
### Set the needed parameters ###
#################################
# Random seed
seed = 0

# Geometric settings
circle_radius = 1
noise_level = 0.05

# Number of points and parameters
n_points = 500
n_parameters = 5

# Softmax distance
softmax_distance = 0.8

# Percent variances to use
percent_variances = [50, 75, 90]

# Plot settings
used_engine = "matplotlib"
mean_only_flag = False
use_3d_flag = False

# Show and save flags
show_flag = True
save_flag = False


##############################
### Run the requested demo ###
##############################
# Set the random seed (if needed)
if seed is not None:
    random.seed(seed = seed)

# Generate the raw random data
raw_data_array = (2 * random.rand(n_points, n_parameters) - 1) * noise_level
for row_index in range(n_points):
    # Generate the raw x-value and y-value
    raw_x_value = random.randn()
    raw_y_value = random.randn()

    # Normalize to get the correct final values
    x_value = circle_radius * raw_x_value / sqrt(raw_x_value**2 + raw_y_value**2)
    y_value = circle_radius * raw_y_value / sqrt(raw_x_value**2 + raw_y_value**2)

    # Store the computed values
    raw_data_array[row_index, 0] += x_value
    raw_data_array[row_index, 1] += y_value

db_path = generateDimensionDatabase(raw_data_array = raw_data_array, min_softmax_distance = 0.2 * softmax_distance, max_softmax_distance = 2 * softmax_distance, n_distances = 10)
print(estimatePointwiseDimension(db_path = db_path, softmax_distance = 0.95 * softmax_distance, percent_variance = 75))
print(estimatePointwiseDimension(db_path = db_path, softmax_distance = 1.00 * softmax_distance, percent_variance = 75))
print(estimatePointwiseDimension(db_path = db_path, softmax_distance = 1.05 * softmax_distance, percent_variance = 75))
plotDimensionEstimateOfPoint(db_path = db_path, row_index = 0, min_softmax_distance = softmax_distance, max_softmax_distance = softmax_distance, min_percent_variance = 0, max_percent_variance = 100)
plotDimensionEstimateOfPoint(db_path = db_path, row_index = 0, min_softmax_distance = 0.2 * softmax_distance, max_softmax_distance = 2 * softmax_distance, min_percent_variance = 75, max_percent_variance = 75)
plotDimensionEstimateOfPoint(db_path = db_path, row_index = 0, min_softmax_distance = 0.2 * softmax_distance, max_softmax_distance = 2 * softmax_distance, min_percent_variance = 50, max_percent_variance = 90)
quit()

# Generate the dimension database and get the corresponding db file path
db_path = generateDimensionDatabase(raw_data_array = raw_data_array, softmax_distance = softmax_distance)

# Plot the marginal and cumulative percent variances stored in the db file
plotMarginalVariances(db_path = db_path,
                      used_engine = used_engine,
                      mean_only_flag = mean_only_flag,
                      show_flag = show_flag,
                      save_flag = save_flag)
plotCumulativeVariances(db_path = db_path,
                        used_engine = used_engine,
                        mean_only_flag = mean_only_flag,
                        show_flag = show_flag,
                        save_flag = save_flag)

# Visualize the dimension estimates at the needed percent variance levels
for percent_variance in percent_variances:
    visualizePointwiseEstimate(db_path = db_path,
                               percent_variance = percent_variance,
                               used_engine = used_engine,
                               use_3d_flag = use_3d_flag,
                               show_flag = show_flag,
                               save_flag = save_flag)