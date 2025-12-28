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

# Internal modules
from vector_helper import VectorField2D


#################################
### Set the needed parameters ###
#################################
# Vector field dimensions
n_rows = 1080
n_cols = 1920

# Base vector seed
seed = 0

# Softmax normalizer
softmax_normalizer = 320

# Show and save flags
show_flag = False
save_flag = True

# PCA image flags
unclipped_flag = True
keep_positive_flag = True
keep_negative_flag = True


#########################################################################
### Create the code inside __main__ so that multiprocessing will work ###
#########################################################################
if __name__ == "__main__":
    # Create the vector field object
    vector_field = VectorField2D(n_rows = n_rows, n_cols = n_cols)

    # Compute all vectors for the vector field
    vector_field.generateBaseVectors(seed = seed)
    vector_field.computeRemainingVectors(softmax_normalizer = softmax_normalizer)

    # Compute the curl and divergence of the vector field
    vector_field.computeAllCurlDivergence()

    # Plot the needed images
    vector_field.plotCurl(show_flag = show_flag, save_flag = save_flag)
    vector_field.plotDivergence(show_flag = show_flag, save_flag = save_flag)
    vector_field.plotPCA(unclipped_flag = unclipped_flag, keep_positive_flag = keep_positive_flag,
	                     keep_negative_flag = keep_negative_flag, show_flag = show_flag, save_flag = save_flag)