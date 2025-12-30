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
from dimension_estimation import generateDimensionDatabase, plotCumulativeVariances, visualizePointwiseEstimate

# External modules
from numpy import random


#################################
### Set the needed parameters ###
#################################
# Random seed
seed = 0

# Number of points and parameters
n_points = 500
n_parameters = 10

# Softmax distance
softmax_distance = 1

# Percent variances to use
percent_variances = [50, 75, 90]

# Plot settings
used_engine = "plotly"
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
raw_data_array = random.rand(n_points, n_parameters)

# Generate the dimension database and get the corresponding db file path
db_path = generateDimensionDatabase(raw_data_array = raw_data_array, softmax_distance = softmax_distance)

# Plot the cumulative percent variances stored in the db file
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