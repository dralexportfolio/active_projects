##########################################
### Import needed general dependencies ###
##########################################
# DraleInfra objects
from DraleInfra.common_needs.privacy_helper import privacyDecorator
from DraleInfra.common_needs.type_helper import isListWithStringEntries

# Project dependencies
from Graph import Graph

# Scipy objects
from scipy.sparse import lil_matrix

# Additional dependencies
from itertools import combinations
from typing import Tuple


###########################################
### Define the simplicial complex class ###
###########################################
# Create the decorator needed for making the attributes private
simplicial_complex_decorator = privacyDecorator(["_n_vertices",						# class variables
												 "_simplex_integers",
												 "_vertex_labels",
												 "_computeRankNullity",				# private functions
												 "_computeSubsimplexIntegers",
												 "_integerToDimension",
												 "_integerToString"
												 "_stringToInteger",
												 "_verticesToString"])

# Define the class with private attributes
@simplicial_complex_decorator
class SimplicialComplex:
	### Initialize the class ###
	def __init__(self, n_vertices:int, vertex_labels:list = None):
		# Verify the inputs
		assert type(n_vertices) == int, "SimplicialComplex::__init__: Provided value for 'n_vertices' must be an int object"
		assert n_vertices > 0, "SimplicialComplex::__init__: Provided value for 'n_vertices' must be positive"
		if vertex_labels is not None:
			assert isListWithStringEntries(vertex_labels, allow_empty_flag = False) == True, "SimplicialComplex::__init__: If provided, value for 'vertex_labels' must be a list object with non-empty strings for entries"
			assert len(vertex_labels) == n_vertices, "SimplicialComplex::__init__: If provided, value for 'vertex_labels' must be a list of length 'n_vertices'"
			assert len(vertex_labels) == len(set(vertex_labels)), "SimplicialComplex::__init__: If provided, value for 'vertex_labels' must be a list of distinct entries"

		# Set the default vertex labels (if needed)
		if vertex_labels is None:
			vertex_labels = [str(index) for index in range(n_vertices)]

		# Initialize the needed internal storage
		self._n_vertices = n_vertices
		self._vertex_labels = vertex_labels
		self._simplex_integers = []

	### Define helpful magic methods ###
	def __str__(self) -> str:
		# Return a string representation of the simplicial complex
		# Initialize the string to return
		to_return = ""

		# Add binary representations of the simplex integers
		for simplex_integer in self._simplex_integers:
			to_return += self._integerToString(simplex_integer) + "\n"

		# Return the results
		return to_return

	### Define private functions for handling conversions ###
	def _integerToDimension(self, simplex_integer:int) -> int:
		# Compute the dimension associated with a given simplex integer
		# Verify the inputs
		assert simplex_integer > 0, "SimplicialComplex::_integerToDimension: Provided value for 'simplex_integer' must be positive"

		# Convert the integer to its associated string
		simplex_string = self._integerToString(simplex_integer)

		# Return the dimension based on the number of 1's in the string
		return simplex_string.count("1") - 1

	def _integerToString(self, simplex_integer:int) -> str:
		# Compute the string of 0's and 1's associated with an existing integer
		# Convert the integer to a string of 0's and 1's
		simplex_string = format(simplex_integer, "b")

		# Reverse the string and append 0's (if needed)
		simplex_string = simplex_string[::-1] + "0" * (self._n_vertices - len(simplex_string))

		# Return the result
		return simplex_string

	def _stringToInteger(self, simplex_string:str) -> int:
		# Convert the reversed string to an integer and return the result
		return int(simplex_string[::-1], 2)

	def _verticesToString(self, *vertices) -> str:
		# Compute the string of 0's and 1's associated with a new list of vertices
		# Initialize the string to be all 0's
		new_simplex_string = "0" * (1 + max(vertices))

		# Add in the needed 1's
		for vertex in vertices:
			new_simplex_string = new_simplex_string[:vertex] + "1" + new_simplex_string[vertex + 1:]

		# Return the result
		return new_simplex_string

	### Define functions for accessing internally stored information ###
	def getVertexCount(self) -> int:
		# Return the number of vertices used to represent the simplices in this complex
		return self._n_vertices

	def getDimension(self) -> int:
		# Return the dimension of the highest dimension simplex in the complex
		if len(self._simplex_integers) == 0:
			return 0
		else:
			return max([self._integerToDimension(simplex_integer) for simplex_integer in self._simplex_integers])

	### Define a function for adding a simplex to the complex ###
	def addSimplex(self, *vertices):
		# Verify the inputs
		for vertex in vertices:
			assert type(vertex) == int, "SimplicialComplex::addSimplex: Provided values for 'vertices' must be int objects"
			assert 0 <= vertex, "SimplicialComplex::addSimplex: Provided values for 'vertices' must be non-negative"
			assert vertex < self._n_vertices, "Graph::addSimplex: Provided values for 'vertices' must be less than the number of vertices (in this case " + str(self._n_vertices) + ")"
		assert len(vertices) > 0, "SimplicialComplex::addSimplex: Provided values for 'vertices' must exist (i.e. must provide at least 1 argument)"
		assert len(vertices) == len(set(vertices)), "SimplicialComplex::addSimplex: Provided values for 'vertices' must be distict integers"

		# Compute the string of 0's and 1's associated with this new simplex
		new_simplex_string = self._verticesToString(*vertices)

		# Convert the string to an integer (after reversing the string)
		new_simplex_integer = self._stringToInteger(new_simplex_string)

		# Determine if this simplex needs to be added to the complex, add it if so
		if new_simplex_integer not in self._simplex_integers:
			# Initialize a flag indicating if the simplex should be added
			add_simplex_flag = True

			# Loop over the currently added simplices and determine their relation to this new one
			simplex_index = 0
			while simplex_index < len(self._simplex_integers):
				# Take the bitwise and (i.e. intersection) of the selected simplex and the new one
				intersection_integer = self._simplex_integers[simplex_index] & new_simplex_integer

				# Handle the various cases
				if intersection_integer == new_simplex_integer:
					# New simplex is contained in the selected one, don't add the new one
					add_simplex_flag = False
					break
				elif intersection_integer == self._simplex_integers[simplex_index]:
					# Selected simplex is contained in the new one, remove the selected one
					self._simplex_integers.pop(simplex_index)
					simplex_index -= 1

				# Iterate to the next simplex
				simplex_index += 1

			# Add the result to storage (if needed)
			if add_simplex_flag == True:
				self._simplex_integers.append(new_simplex_integer)
				self._simplex_integers.sort(reverse = False)

	### Define a function for removing extra vertices from the representations of the simplices ###
	def removeExtraVertices(self) -> list:
		# Remove any vertices which are not part of simplices and update the stored integers accordingly, return the removed vertices
		# Take the bitwise or (i.e. union) of the stored simplex integers
		union_integer = 0
		for simplex_integer in self._simplex_integers:
			union_integer = union_integer | simplex_integer

		# Convert this union integer to its string form
		union_string = self._integerToString(union_integer)

		# Loop over the simplex integers and update them accordingly
		new_simplex_integers = []
		for simplex_integer in self._simplex_integers:
			# Convert the current integer to its string form
			simplex_string = self._integerToString(simplex_integer)

			# Take only the characters corresponding entries take a value of '1' in the union string
			new_simplex_string = "".join([simplex_string[index] for index in range(self._n_vertices) if union_string[index] == "1"])

			# Convert this new string back to an integer and store it
			new_simplex_integers.append(self._stringToInteger(new_simplex_string))

		# Compute the vertices which were removed from the representations, also compute the vertex labels to keep
		removed_vertices = [index for index in range(self._n_vertices) if union_string[index] == "0"]
		new_vertex_labels = [self._vertex_labels[index] for index in range(self._n_vertices) if union_string[index] == "1"]

		print(self._vertex_labels)
		print(new_vertex_labels)

		# Update the internal storage to match the changes
		self._n_vertices -= len(removed_vertices)
		self._vertex_labels = new_vertex_labels
		self._simplex_integers = new_simplex_integers

		# Return the results
		return removed_vertices

	### Define functions for computing the boundary matrices of the complex ###
	def _computeSubsimplexIntegers(self, subsimplex_dimension:int) -> list:
		# Compute the list of all simplex integers corresponding to sub-simplices of a given dimension
		# Initialize the needed list
		subsimplex_integers = []

		# Handle the various cases
		if subsimplex_dimension == -1:
			# Add the equivalent of the empty set
			subsimplex_integers.append(0)
		else:
			# Loop over the simplex integers
			for simplex_integer in self._simplex_integers:
				if self._integerToDimension(simplex_integer) >= subsimplex_dimension:
					# Convert the current integer to its string form
					simplex_string = self._integerToString(simplex_integer)

					# Find the indices of the 1's in this string
					indices_of_ones = [index for index in range(self._n_vertices) if simplex_string[index] == "1"]

					# Loop over the sub-simplices of the given dimension
					for vertices in combinations(indices_of_ones, subsimplex_dimension + 1):
						# Compute the string and integer corresponding to these vertices
						subsimplex_string = self._verticesToString(*vertices)
						subsimplex_integer = self._stringToInteger(subsimplex_string)

						# Add the integer to the list (if needed)
						if subsimplex_integer not in subsimplex_integers:
							subsimplex_integers.append(subsimplex_integer)

			# Sort the resulting list
			subsimplex_integers.sort()

		# Return the results
		return subsimplex_integers

	def boundaryMatrix(self, dimension:int) -> Tuple[lil_matrix, list, list]:
		# Return the lists of row and column labels as well as the boundary matrix itself
		# Note: dimension = 0 gives a non-zero matrix so this is technically for augmented homology, bettiNumber function corrects for this
		# Compute the dimension of this simplicial complex and only proceed if it is non-zero
		complex_dimension = self.getDimension()
		assert complex_dimension > 0, "SimplicialComplex::boundaryMatrix: Unable to proceed because there are no simplices in this complex"

		# Verify the inputs
		assert type(dimension) == int, "SimplicialComplex::boundaryMatrix: Provided value for 'dimension' must be an int object"
		assert dimension >= 0, "SimplicialComplex::boundaryMatrix: Provided value for 'dimension' must be non-negative"
		assert dimension <= complex_dimension, "SimplicialComplex::boundaryMatrix: Provided value for 'dimension' must be <= to dimension of the complex (in this case " + str(complex_dimension) + ")"

		# Compute the subsimplex integers to use as labels for the rows and columns of the matrices
		row_subsimplex_integers = self._computeSubsimplexIntegers(dimension - 1)
		col_subsimplex_integers = self._computeSubsimplexIntegers(dimension)

		# Extract the numbers of rows and columns
		n_rows = len(row_subsimplex_integers)
		n_cols = len(col_subsimplex_integers)

		# Create an empty matrix to store the boundary matrix values
		boundary_matrix = lil_matrix((n_rows, n_cols), dtype = int)

		# Construct the boundary matrix accordingly
		for row_index in range(n_rows):
			for col_index in range(n_cols):
				if row_subsimplex_integers[row_index] & col_subsimplex_integers[col_index] == row_subsimplex_integers[row_index]:
					boundary_matrix[row_index, col_index] = 1

		# Compute the corresponding labels to use for the rows and columns
		# Row labels
		row_labels = []
		for subsimplex_integer in row_subsimplex_integers:
			# Compute the corresponding subsimplex string
			subsimplex_string = self._integerToString(subsimplex_integer)
			# Create the row label and store it
			row_label = ",".join([self._vertex_labels[index] for index in range(self._n_vertices) if subsimplex_string[index] == "1"])
			row_label = "null" if len(row_label) == 0 else row_label
			row_labels.append(row_label)
		# Column labels
		col_labels = []
		for subsimplex_integer in col_subsimplex_integers:
			# Compute the corresponding subsimplex string
			subsimplex_string = self._integerToString(subsimplex_integer)
			# Create the column label and store it
			col_label = ",".join([self._vertex_labels[index] for index in range(self._n_vertices) if subsimplex_string[index] == "1"])
			col_label = "null" if len(col_label) == 0 else col_label
			col_labels.append(col_label)

		# Return the results
		return (boundary_matrix, row_labels, col_labels)

	### Define functions for computing the Betti numbers of the complex ###
	def _computeRankNullity(self, binary_matrix:lil_matrix) -> Tuple[int, int]:
		# Put the binary matrix in row echelon form to compute its rank and nullity
		# Get the numbers of rows and columns
		n_rows = binary_matrix.shape[0]
		n_cols = binary_matrix.shape[1]

		# Intialize the needed storage
		search_index = 0
		matrix_rank = 0
		matrix_nullity = 0

		# Perform Gaussian elimination to put in REF
		while search_index < n_cols:
			# Search for a 1 in the current column
			pivot_found_flag = False
			for row_index in range(matrix_rank, n_rows):
				if binary_matrix[row_index, search_index] == 1:
					pivot_found_flag = True
					break

			# Handle the various cases
			if pivot_found_flag == True:
				# Switch the rows at indices row_index and matrix_rank (if needed)
				if row_index != matrix_rank:
					binary_matrix[[row_index, matrix_rank], :] = binary_matrix[[matrix_rank, row_index], :]

				# Cancel out any 1's in this column below the newly found pivot
				for row_index in range(matrix_rank + 1, n_rows):
					if binary_matrix[row_index, search_index] == 1:
						for col_index in range(n_cols):
							binary_matrix[row_index, col_index] = (binary_matrix[row_index, col_index] + binary_matrix[matrix_rank, col_index]) % 2

				# Add 1 to the rank because a pivot was found
				matrix_rank += 1
			else:
				# Add 1 to the nullity because no pivot was found
				matrix_nullity += 1

			# Move to the next column
			search_index += 1

		# Return the results
		return (matrix_rank, matrix_nullity)

	def bettiNumber(self, dimension:int) -> int:
		# Return the Betti number of the given dimension
		# Compute the dimension of this simplicial complex and only proceed if it is non-zero
		complex_dimension = self.getDimension()
		assert complex_dimension > 0, "SimplicialComplex::bettiNumber: Unable to proceed because there are no simplices in this complex"

		# Verify the inputs
		assert type(dimension) == int, "SimplicialComplex::bettiNumber: Provided value for 'dimension' must be an int object"
		assert dimension >= 0, "SimplicialComplex::bettiNumber: Provided value for 'dimension' must be non-negative"
		assert dimension <= complex_dimension, "SimplicialComplex::bettiNumber: Provided value for 'dimension' must be <= to dimension of the complex (in this case " + str(complex_dimension) + ")"

		# Handle the various cases
		if dimension < complex_dimension:
			# Compute the two needed boundary matrices
			low_boundary_matrix = self.boundaryMatrix(dimension)[0]
			high_boundary_matrix = self.boundaryMatrix(dimension + 1)[0]

			# Compute the needed rank and nullity
			low_nullity = self._computeRankNullity(low_boundary_matrix)[1]
			high_rank = self._computeRankNullity(high_boundary_matrix)[0]

			# Add 1 to the nullity if dimension is 0 (to go from augmented homology to unaugmented)
			if dimension == 0:
				low_nullity += 1

			# Return the result using rank and nullity
			return low_nullity - high_rank
		else:
			# Compute the top-dimension boundary matrix
			top_boundary_matrix = self.boundaryMatrix(dimension)[0]

			# Return the result using nullity
			return self._computeRankNullity(top_boundary_matrix)[1]

	### Define a function for computing the 1-skeleton of the complex ###
	def oneSkeleton(self) -> Graph:
		# Return a Graph object representing the 1-skeleton of the complex
		# Initialize the graph
		one_skeleton = Graph(self._n_vertices, self._vertex_labels)

		# Loop over the simplex integers
		for simplex_integer in self._simplex_integers:
			if self._integerToDimension(simplex_integer) >= 1:
				# Convert the current integer to its string form
				simplex_string = self._integerToString(simplex_integer)

				# Find the indices of the 1's in this string
				indices_of_ones = [index for index in range(self._n_vertices) if simplex_string[index] == "1"]

				# Loop over the sub-simplices of the given dimension
				for vertices in combinations(indices_of_ones, 2):
					one_skeleton.addEdge(vertices[0], vertices[1])

		# Return the result
		return one_skeleton


##################################################################
### Define the functions for boundary and coboundary complexes ###
##################################################################
def computeBoundaryComplexes(simplicial_complex:SimplicialComplex) -> list:
	# Compute the boundary complexes of each rank for the given complex
	# Verify the inputs
	assert type(simplicial_complex) == SimplicialComplex, "computeBoundaryComplexes: Provided value for 'simplicial_complex' must be a SimplicialComplex object"

	# Initialize the list of boundary complexes
	boundary_complexes = []

	# Compute the boundary matrices of complex and use their row to construct new complexes
	for dimension in range(simplicial_complex.getDimension() + 1):
		# Get the boundary matrix as well as its row and column counts
		boundary_matrix, row_labels, col_labels = simplicial_complex.boundaryMatrix(dimension)
		n_rows = boundary_matrix.shape[0]
		n_cols = boundary_matrix.shape[1]

		# Create a new boundary complex using the rows
		boundary_complex = SimplicialComplex(n_cols, col_labels)
		for row_index in range(n_rows):
			vertices = [col_index for col_index in range(n_cols) if boundary_matrix[row_index, col_index] == 1]
			if len(vertices) > 0:
				boundary_complex.addSimplex(*vertices)

		# Add the complex to the list
		boundary_complexes.append(boundary_complex)

	# Return the results
	return boundary_complexes

def computeCoboundaryComplexes(simplicial_complex:SimplicialComplex) -> list:
	# Compute the coboundary complexes of each rank for the given complex
	# Verify the inputs
	assert type(simplicial_complex) == SimplicialComplex, "computeCoboundaryComplexes: Provided value for 'simplicial_complex' must be a SimplicialComplex object"

	# Initialize the list of coboundary complexes
	coboundary_complexes = []

	# Compute the boundary matrices of complex and use their row to construct new complexes
	for dimension in range(simplicial_complex.getDimension() + 1):
		# Get the boundary matrix as well as its row and column counts
		boundary_matrix, row_labels, col_labels = simplicial_complex.boundaryMatrix(dimension)
		n_rows = boundary_matrix.shape[0]
		n_cols = boundary_matrix.shape[1]

		# Create a new coboundary complex using the columns
		coboundary_complex = SimplicialComplex(n_rows, row_labels)
		for col_index in range(n_cols):
			vertices = [row_index for row_index in range(n_rows) if boundary_matrix[row_index, col_index] == 1]
			if len(vertices) > 0:
				coboundary_complex.addSimplex(*vertices)

		# Add the complex to the list
		coboundary_complexes.append(coboundary_complex)

	# Return the results
	return coboundary_complexes
