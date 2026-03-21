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
from catan_generator import ALL_TILE_TYPES, CatanGeneratorTiling
from color_helper import ALL_PLOTLY_COLOR_SCALES_BY_TYPE, customSpectrum
from sqlite3_helper import addTable, appendRow, ConnectionManager, getRowCount, readColumn, readEntry
from tkinter_helper import askSaveFilename

# External modules
from numpy import quantile, zeros
import plotly.graph_objects as go
from tqdm import tqdm


######################################################
### Define parameters related to the entropy study ###
######################################################
# Define the initial random seed to use
initial_seed = 0

# Game mode to use
game_mode = "Seafarers: 5-6 Player"

# Swap settings
all_skew_powers = [0, 0.5, 1, 2, 4, float("inf")]
reject_flag = True

# Number of simulations to run and number of swaps to run per simulation
n_simulations_per_power = 100
n_steps_per_simulation = 2000


######################################################################
### Run the needed simulations and save the results to the db file ###
######################################################################
# Initialize the dictionary of expected MSE over time
expected_mse_over_time_by_power = {}

# Run the simulations for each skew power
for skew_power in all_skew_powers:
	# Initialize the array for this skew power
	expected_mse_over_time_by_power[skew_power] = zeros(n_steps_per_simulation, dtype = float)

	# Set the first seed to use
	if initial_seed is None:
		seed = None
	else:
		seed = initial_seed

	# Run the simulations for this skew power
	for sim_index in tqdm(range(n_simulations_per_power)):
		# Create the tiling to use for this simulation
		current_tiling = CatanGeneratorTiling(game_mode = game_mode, seed = seed)

		# Randomly swap tiles for the needed number of simulation steps
		for step_index in range(n_steps_per_simulation):
			# Execute a random swap and get the needed results
			swap_results = current_tiling.swapTiles(skew_power = skew_power, reject_flag = reject_flag)

			# Extract the pre-swap MSE from the swap results
			pre_mean_squared_error = swap_results["pre_mean_squared_error"]

			# Insert the current MSE contribution to the array
			expected_mse_over_time_by_power[skew_power][step_index] += pre_mean_squared_error / n_simulations_per_power

		# Iterate the random seed (if needed)
		if seed is not None:
			seed += 1

##########################################################
### Create a plot comparing the expected MSE over time ###
##########################################################
import matplotlib.pyplot as plt

plt.figure(figsize = (10, 8), layout = "constrained")
for skew_power in all_skew_powers:
	plt.plot(expected_mse_over_time_by_power[skew_power], label = "skew power = " + str(skew_power))
plt.title("Expected MSE Over Time As A Function Of Skew Power (Many Steps)")
plt.xlabel("step index")
plt.ylabel("expected MSE")
plt.yscale("log")
plt.grid()
plt.legend()

plt.figure(figsize = (10, 8), layout = "constrained")
for skew_power in all_skew_powers:
	plt.plot(expected_mse_over_time_by_power[skew_power][:100], label = "skew power = " + str(skew_power))
plt.title("Expected MSE Over Time As A Function Of Skew Power (Few Steps)")
plt.xlabel("step index")
plt.ylabel("expected MSE")
plt.yscale("log")
plt.grid()
plt.legend()

plt.show()