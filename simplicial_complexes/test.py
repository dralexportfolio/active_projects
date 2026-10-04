##########################################
### Import needed general dependencies ###
##########################################
# Project dependencies
from SimplicialComplex import *


#################################################################
### Perform a series of tests on the simplicial complex class ###
#################################################################
# Create the empty complex
simplicial_complex = SimplicialComplex(12)

# Add some initial simplicies
simplicial_complex.addSimplex(0, 1)
simplicial_complex.addSimplex(0, 7, 9)
simplicial_complex.addSimplex(1, 3, 4, 7)
simplicial_complex.addSimplex(2, 11)
simplicial_complex.addSimplex(1, 3, 6)
print("INITIAL SIMPLICES ADDED:")
print(simplicial_complex)

# Add a super-simplex and observe the merging of existing simplices
simplicial_complex.addSimplex(1, 3, 4, 6, 7)
print("SUPER-SIMPLEX ADDED:")
print(simplicial_complex)

# Remove the vertices which are not part of any simplicies
simplicial_complex.removeExtraVertices()
print("EXTRA VERTICES REMOVED:")
print(simplicial_complex)

# Compute and display the various boundary simplices
print("BOUNDARY MATRICES OF VARIOUS DIMENSIONS:")
for dimension in range(simplicial_complex.getDimension() + 1):
	print("--------------- Dimension " + str(dimension) + " ---------------")
	print(simplicial_complex.boundaryMatrix(dimension)[0].toarray())
print(" ")

# Compute and display the Betti numbers of the complex
print("ALL BETTI NUMBERS OF THE COMPLEX:")
print([simplicial_complex.bettiNumber(dimension) for dimension in range(simplicial_complex.getDimension() + 1)])
print(" ")

# Compute the 1-skeleton of the complex
one_skeleton = simplicial_complex.oneSkeleton()

# Display the adjacency matrix of the 1-skeleton
print("ADJACENCY MATRIX OF THE 1-SKELETON:")
print(one_skeleton.adjacencyMatrix())
print(" ")

# Create a plot of the 1-skeleton graph
one_skeleton.plot(title_prefix = "Simplicial Complex")

# Compute and plot the the boundary complexes
boundary_complexes = computeBoundaryComplexes(simplicial_complex)
for dimension in range(simplicial_complex.getDimension() + 1):
	boundary_complexes[dimension].oneSkeleton().plot(title_prefix = "Boundary Complex " + str(dimension))

# Compute and plot the the coboundary complexes
coboundary_complexes = computeCoboundaryComplexes(simplicial_complex)
for dimension in range(simplicial_complex.getDimension() + 1):
	coboundary_complexes[dimension].oneSkeleton().plot(title_prefix = "Coboundary Complex " + str(dimension))
