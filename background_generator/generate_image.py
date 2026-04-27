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
from vector_helper import VectorFieldGenerator


#################################
### Set the needed parameters ###
#################################
# Vector field dimensions
n_rows = 1080
n_cols = 1920

# Base vector seed
seed = 0

# Softmax normalizer
softmax_normalizer = 120

# Affine transformation values
m_11 = 1
m_12 = 0
m_21 = 1
m_22 = 1
b_1 = 0
b_2 = 0

# Gap sizes
gap_size_quiver = 50
gap_size_streamplot = 20

# Show and save flags
show_flag = False
save_flag = True


#########################################################################
### Create the code inside __main__ so that multiprocessing will work ###
#########################################################################
if __name__ == "__main__":
    # Create the vector field generator and generate the vector field using the needed settings
    vector_field_generator = VectorFieldGenerator(n_rows = n_rows, n_cols = n_cols)
    vector_field = vector_field_generator.generate(seed = seed, softmax_normalizer = softmax_normalizer)

    # Apply the affine transformation to the vector field
    vector_field.applyAffineTransformation(m_11 = m_11, m_12 = m_12, m_21 = m_21, m_22 = m_22, b_1 = b_1, b_2 = b_2)

    # Compute the curl and divergence of the vector field
    vector_field.computeDerivativeInfo()

    # Plot the needed images
    # Vector field
    vector_field.plotVectorField(gap_size = gap_size_quiver, plot_type = "quiver", show_flag = show_flag, save_flag = save_flag)
    vector_field.plotVectorField(gap_size = gap_size_streamplot, plot_type = "streamplot", show_flag = show_flag, save_flag = save_flag)
    quit()
    # Raw derivative-related values
    vector_field.renderDerivativeInfo(curl_flag = True, divergence_flag = False, jacobian_flag = False, show_flag = show_flag, save_flag = save_flag)
    vector_field.renderDerivativeInfo(curl_flag = False, divergence_flag = True, jacobian_flag = False, show_flag = show_flag, save_flag = save_flag)
    vector_field.renderDerivativeInfo(curl_flag = False, divergence_flag = False, jacobian_flag = True, show_flag = show_flag, save_flag = save_flag)
    # PCA combinations
    vector_field.renderDerivativeInfo(curl_flag = True, divergence_flag = True, jacobian_flag = False, show_flag = show_flag, save_flag = save_flag)
    vector_field.renderDerivativeInfo(curl_flag = True, divergence_flag = False, jacobian_flag = True, show_flag = show_flag, save_flag = save_flag)
    vector_field.renderDerivativeInfo(curl_flag = False, divergence_flag = True, jacobian_flag = True, show_flag = show_flag, save_flag = save_flag)
    vector_field.renderDerivativeInfo(curl_flag = True, divergence_flag = True, jacobian_flag = True, show_flag = show_flag, save_flag = save_flag)