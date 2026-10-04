##########################################
### Import needed general dependencies ###
##########################################
# DraleInfra objects
from DraleInfra.common_needs.privacy_helper import privacyDecorator
from DraleInfra.common_needs.type_helper import isListWithStringEntries

# Numpy objects
from numpy import inf, matmul, ndarray, zeros
from numpy import max as np_max

# Matplotlib objects
import matplotlib.pyplot as plt

# Additonal dependencies
from copy import deepcopy
from math import cos, pi, sin, sqrt, tanh


#############################################################
### Set the various parameters needed for the graph class ###
#############################################################
# Set the various sizes to use
FIG_SIZE = (10, 8)
TEXT_SIZE = 14

# Set the various colors to use
EDGE_COLOR = "orange"
VERTEX_COLOR = "black"
TEXT_COLOR = "indigo"

# Set the step size and default angles
STEP_SIZE = 5
DEFAULT_ELEV = 30
DEFAULT_AZIM = -60


##############################
### Define the graph class ###
##############################
# Create the decorator needed for making the attributes private
graph_decorator = privacyDecorator(["_edge_tuples",						# class variables
									"_n_vertices",
									"_vertex_labels",
									"_computeEmbeddedDistances"])		# private functions
class Graph:
	### Initialize the class ###
	def __init__(self, n_vertices:int, vertex_labels:list = None):
		# Verify the inputs
		assert type(n_vertices) == int, "Graph::__init__: Provided value for 'n_vertices' must be an int object"
		assert n_vertices > 0, "Graph::__init__: Provided value for 'n_vertices' must be positive"
		if vertex_labels is not None:
			assert isListWithStringEntries(vertex_labels, allow_empty_flag = False) == True, "Graph::__init__: If provided, value for 'vertex_labels' must be a list object with non-empty strings for entries"
			assert len(vertex_labels) == n_vertices, "Graph::__init__: If provided, value for 'vertex_labels' must be a list of length 'n_vertices'"
			assert len(vertex_labels) == len(set(vertex_labels)), "Graph::__init__: If provided, value for 'vertex_labels' must be a list of distinct entries"

		# Set the default vertex labels (if needed)
		if vertex_labels is None:
			vertex_labels = [str(index) for index in range(n_vertices)]

		# Initialize the needed internal storage
		self._n_vertices = n_vertices
		self._vertex_labels = vertex_labels
		self._edge_tuples = []

	### Define a function for adding an edge to the graph ###
	def addEdge(self, vertex_0:int, vertex_1:int):
		# Add the given vertex pair to the list of stored edges
		# Verify the inputs
		assert type(vertex_0) == int, "Graph::addEdge: Provided value for 'vertex_0' must be an int object"
		assert type(vertex_1) == int, "Graph::addEdge: Provided value for 'vertex_1' must be an int object"
		assert 0 <= vertex_0, "Graph::addEdge: Provided value for 'vertex_0' must be non-negative"
		assert vertex_0 < vertex_1, "Graph::addEdge: Provided value for 'vertex_0' must be less than provided value for 'vertex_1'"
		assert vertex_1 < self._n_vertices, "Graph::addEdge: Provided value for 'vertex_1' must be less than the number of vertices (in this case " + str(self._n_vertices) + ")"

		# Set the edge tuple to add to the list
		edge_tuple = (vertex_0, vertex_1)

		# Add the tuple to the list (if needed)
		if edge_tuple not in self._edge_tuples:
			self._edge_tuples.append(edge_tuple)

	### Define a function computing the adjacency matrix of the graph ###
	def adjacencyMatrix(self) -> ndarray:
		# Return a binary matrix representing the edges of the graph
		# Initialize the distance matrix
		adjacency_matrix = zeros((self._n_vertices, self._n_vertices), dtype = int)

		# Loop over the edges and add the needed 1's to the matrix
		for edge_tuple in self._edge_tuples:
			adjacency_matrix[edge_tuple[0], edge_tuple[1]] = 1
			adjacency_matrix[edge_tuple[1], edge_tuple[0]] = 1

		# Return the result
		return adjacency_matrix

	### Define functions for computing clusters and path distances ###
	def computePathDistances(self) -> ndarray:
		# Compute the pairwise distances between the vertices as paths in the graph
		# Compute the adjacency matrix of the graph
		adjacency_matrix = self.adjacencyMatrix()

		# Initialize the needed matrices
		power_matrix = deepcopy(adjacency_matrix)
		path_distances = deepcopy(adjacency_matrix).astype(float)

		# Set the current power of the power matrix
		current_power = 1

		# Loop until the needed distances are computed
		while True:
			# Compute the new power matrix and iterate to the next power
			power_matrix = matmul(power_matrix, adjacency_matrix)
			current_power += 1

			# Set a flag indicating that an update has yet to occur
			updated_flag = False

			# Compute updates to the distance matrix
			for row_index in range(self._n_vertices - 1):
				for col_index in range(row_index + 1, self._n_vertices):
					if power_matrix[row_index, col_index] > 0 and path_distances[row_index, col_index] == 0:
						# Set the distance for this pair
						path_distances[row_index, col_index] = current_power
						path_distances[col_index, row_index] = current_power

						# Mark that an update occured
						updated_flag = True

			# End the loop if no update occured
			if updated_flag == False:
				break

		# Set any non-diagonal entries to infinity (since not connected)
		for row_index in range(self._n_vertices - 1):
			for col_index in range(row_index + 1, self._n_vertices):
				if path_distances[row_index, col_index] == 0:
					path_distances[row_index, col_index] = inf
					path_distances[col_index, row_index] = inf

		# Return the result
		return path_distances

	def computeClusters(self) -> list:
		# Return a list of lists where each sub-list is the vertices in that clusters
		# Compute the path distances between the vertices
		path_distances = self.computePathDistances()

		# Initialize the needed storage
		cluster_per_vertex = {}
		all_clusters = []

		# Loop over the vertices and compute the clusters
		for index_0 in range(self._n_vertices):
			if index_0 not in cluster_per_vertex:
				# Vertex not in a cluster yet, create new cluster
				all_clusters.append([])

				# Add all vertices connected to this one to the cluster
				for index_1 in range(self._n_vertices):
					if path_distances[index_0, index_1] < inf:
						cluster_per_vertex[index_1] = len(all_clusters) - 1
						all_clusters[-1].append(index_1)

		# Return the results
		return all_clusters

	### Define functions for creating a plot of the nodes and edges ###
	def _computeEmbeddedDistances(self, x_coordinates:list, y_coordinates:list, z_coordinates:list) -> ndarray:
		# Compute the pairwise distances between the vertices as embedded in 3D space
		# Initialize the matrix
		embedded_distances = zeros((self._n_vertices, self._n_vertices), dtype = float)

		# Loop over the pairs of vertices and add the distances
		for index_0 in range(self._n_vertices - 1):
			for index_1 in range(index_0 + 1, self._n_vertices):
				# Compute the current distance
				current_distance = sqrt((x_coordinates[index_1] - x_coordinates[index_0])**2
										+ (y_coordinates[index_1] - y_coordinates[index_0])**2
										+ (z_coordinates[index_1] - z_coordinates[index_0])**2)

				# Store in the matrix
				embedded_distances[index_0, index_1] = current_distance
				embedded_distances[index_1, index_0] = current_distance

		# Return the result
		return embedded_distances

	def plot(self, title_prefix:str = "", n_iter:int = 1000, max_update_size:float = 0.01):
		# Create a plot of the nodes and edges for this graph
		# Verify the inputs
		assert type(title_prefix) == str, "Graph::plot: Provided value for 'title_prefix' must be a str object"
		assert type(n_iter) == int, "Graph::plot: Provided value for 'n_iter' must be an int object"
		assert n_iter > 0, "Graph::plot: Provided value for 'n_iter' must be positive"
		assert type(max_update_size) == float, "Graph::plot: Provided value for 'max_update_size' must be a float object"
		assert 0 < max_update_size and max_update_size < 0.1, "Graph::plot: Provided value for 'max_update_size' must be > 0 and < 0.1"

		# Compute the path distances between the vertices
		path_distances = self.computePathDistances()

		# Determine the vertex coordinates for the plot
		if self._n_vertices == 1:
			# Just one vertex, just use the origin for the coordinates
			best_x_coordinates = [0]
			best_y_coordinates = [0]
			best_z_coordinates = [0]
		else:
			# Use the Fibonacci Sphere method to distribute the vertices evenly
			# Z-coordinates
			z_coordinates = [1 - (2 * index) / (self._n_vertices - 1) for index in range(self._n_vertices)]
			# Radius and theta values
			r_values = [sqrt(1 - z_coordinates[index]**2) for index in range(self._n_vertices)]
			t_values = [(4 * pi * index) / (1 + sqrt(5)) for index in range(self._n_vertices)]
			# X and Y-coordinates
			x_coordinates = [r_values[index] * cos(t_values[index]) for index in range(self._n_vertices)]
			y_coordinates = [r_values[index] * sin(t_values[index]) for index in range(self._n_vertices)]

			# Compute the embedded distances between the vertices
			embedded_distances = self._computeEmbeddedDistances(x_coordinates, y_coordinates, z_coordinates)

			# Initialize the best squared error and coordinates
			best_squared_error = inf
			best_x_coordinates = None
			best_y_coordinates = None
			best_z_coordinates = None

			# Iteratively make small adjustments to the distances
			for _ in range(n_iter):
				# Create copies of the coordinates so adjustments can be made
				new_x_coordinates = deepcopy(x_coordinates)
				new_y_coordinates = deepcopy(y_coordinates)
				new_z_coordinates = deepcopy(z_coordinates)

				# Loop over the vertex pairs and make small adjustments
				for index_0 in range(self._n_vertices - 1):
					for index_1 in range(index_0 + 1, self._n_vertices):
						if path_distances[index_0, index_1] < inf:
							# Compute the vector connecting these two points
							delta_x = x_coordinates[index_1] - x_coordinates[index_0]
							delta_y = y_coordinates[index_1] - y_coordinates[index_0]
							delta_z = z_coordinates[index_1] - z_coordinates[index_0]

							# Compute the length (i.e. norm) of this vector
							delta_norm = sqrt(delta_x**2 + delta_y**2 + delta_z**2)

							# Compute the signed update size based on the difference between embedded and path distances
							update_size = max_update_size * tanh(embedded_distances[index_0, index_1] - path_distances[index_0, index_1])

							# If the embedded distance is too large (resp. small) then move the points closer (resp. further)
							# Point 0
							new_x_coordinates[index_0] += update_size * delta_x / delta_norm
							new_y_coordinates[index_0] += update_size * delta_y / delta_norm
							new_z_coordinates[index_0] += update_size * delta_z / delta_norm
							# Point 1
							new_x_coordinates[index_1] -= update_size * delta_x / delta_norm
							new_y_coordinates[index_1] -= update_size * delta_y / delta_norm
							new_z_coordinates[index_1] -= update_size * delta_z / delta_norm

				# Update the coordinates now that adjustments have been made
				x_coordinates = new_x_coordinates
				y_coordinates = new_y_coordinates
				z_coordinates = new_z_coordinates

				# Update the embedded distances based on the new coordinates
				embedded_distances = self._computeEmbeddedDistances(x_coordinates, y_coordinates, z_coordinates)

				# Compute the squared error between the patha and embedded distances
				squared_error = 0
				for index_0 in range(self._n_vertices - 1):
					for index_1 in range(index_0 + 1, self._n_vertices):
						if path_distances[index_0, index_1] < inf:
							squared_error += (path_distances[index_0, index_1] - embedded_distances[index_0, index_1])**2

				# Update the best squared error and coordinates (if needed)
				if squared_error < best_squared_error:
					best_squared_error = squared_error
					best_x_coordinates = deepcopy(x_coordinates)
					best_y_coordinates = deepcopy(y_coordinates)
					best_z_coordinates = deepcopy(z_coordinates)

		# Compute the various clusters in the graph as well as the number of clusters
		all_clusters = self.computeClusters()
		n_clusters = len(all_clusters)

		# Create 3D plots of the embedded versions of each cluster in the graph
		for cluster_index in range(n_clusters):
			# Get the current cluster as well as its size
			current_cluster = all_clusters[cluster_index]
			cluster_size = len(current_cluster)

			# Get the coordinates needed for this cluster
			cluster_x_coordinates = [best_x_coordinates[index] for index in current_cluster]
			cluster_y_coordinates = [best_y_coordinates[index] for index in current_cluster]
			cluster_z_coordinates = [best_z_coordinates[index] for index in current_cluster]

			# Create the figure and axes
			fig = plt.figure(figsize = FIG_SIZE)
			ax = fig.add_subplot(projection = "3d")

			# Add the edges to the plot
			for index_0 in range(cluster_size - 1):
				for index_1 in range(index_0 + 1, cluster_size):
					if path_distances[current_cluster[index_0], current_cluster[index_1]] == 1:
						ax.plot([cluster_x_coordinates[index_0], cluster_x_coordinates[index_1]],
								[cluster_y_coordinates[index_0], cluster_y_coordinates[index_1]],
								[cluster_z_coordinates[index_0], cluster_z_coordinates[index_1]],
								color = EDGE_COLOR,
								zorder = 0)

			# Add the vertices to the plot
			ax.scatter(cluster_x_coordinates,
					   cluster_y_coordinates,
					   cluster_z_coordinates,
					   color = VERTEX_COLOR,
					   zorder = 10)

			# Add the labels to the plot
			for index in range(cluster_size):
				vertex_label = self._vertex_labels[current_cluster[index]]
				ax.text(cluster_x_coordinates[index],
						cluster_y_coordinates[index],
						cluster_z_coordinates[index],
						vertex_label,
						color = TEXT_COLOR,
						size = TEXT_SIZE,
						fontweight = "bold",
						zorder = 20)

			# Set the plot title to use
			plot_title = ""
			if len(title_prefix) > 0:
				plot_title += title_prefix + " - "
			plot_title += "Cluster " + str(cluster_index)

			# Format the figure
			plt.title(plot_title)
			ax.set_xlabel("x-axis")
			ax.set_ylabel("y-axis")
			ax.set_zlabel("z-axis")
			plt.tight_layout()

			# Define an internal function to be able to control the plot using arrow keys
			def _onKey(event):
				# Get the current angles of the 3D plot
				current_elev = ax.elev if ax.elev is not None else DEFAULT_ELEV
				current_azim = ax.azim if ax.azim is not None else DEFAULT_AZIM

				# Set the new angles accordingly
				if event.key == "up":
					new_elev = current_elev + STEP_SIZE
					new_azim = current_azim
				elif event.key == "down":
					new_elev = current_elev - STEP_SIZE
					new_azim = current_azim
				elif event.key == "right":
					new_elev = current_elev
					new_azim = current_azim + STEP_SIZE
				elif event.key == "left":
					new_elev = current_elev
					new_azim = current_azim - STEP_SIZE
				else:
					new_elev = current_elev
					new_azim = current_azim

				# Update the angles to the new values
				ax.view_init(elev = new_elev, azim = new_azim)
				fig.canvas.draw_idle()

			# Bind the on-key function to the figure
			fig.canvas.mpl_connect('key_press_event', _onKey)

			# Show the figures
			plt.show()
