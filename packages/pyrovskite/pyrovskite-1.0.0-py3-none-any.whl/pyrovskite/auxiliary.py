import numpy as np

def _get_periodic_X_images(perov):
    if perov.octahedra is None:
        perov.identify_octahedra()

    # There are 26 possible periodic images of a given atom, so for each
    # of the 6 X-anions in an octahedra, we want to have an 27x3 nparray
    # containing their coordinates. One for the base image, and 8 for the others.

    # This allows us to look at X from one octahedra, and tell if it is present in another octahedra by simply
    # looping through all possible combinations of the periodic images
    
    NN_combinations = np.array([[0, 0, 0], [0, 0, 1], [0, 0, -1], [0, 1, 0], [0, 1, 1], [0, 1, -1], [0, -1, 0], [0, -1, 1], [0, -1, -1], [1, 0, 0], [1, 0, 1], [1, 0, -1], [1, 1, 0], [1, 1, 1], [1, 1, -1], [1, -1, 0], [1, -1, 1], [1, -1, -1], [-1, 0, 0], [-1, 0, 1], [-1, 0, -1], [-1, 1, 0], [-1, 1, 1], [-1, 1, -1], [-1, -1, 0], [-1, -1, 1], [-1, -1, -1]], dtype='float64')

    cell_shifts = np.zeros_like(NN_combinations)
    for idx, image in enumerate(NN_combinations):
        cell_shifts[idx] = (perov.atoms.cell@image.T).T
    #print(cell_shifts)


    # N_octahedra, 7 (Bcation,6Xcations), 3(cartesian coords)
    octa_shape = perov.octahedra.shape

    # N_octa, 6Xcations, 27 images, 3 cartesian coords
    X_images = np.zeros((octa_shape[0], 6, 27, 3))

    for octa in range(octa_shape[0]):
        for X_anion in range(6):
            for shift_idx, shift in enumerate(cell_shifts):
                #print(shift)
                #print(perov.octahedra[octa, X_anion+1])
                #print(shift + perov.octahedra[octa,X_anion+1])
                X_images[octa, X_anion, shift_idx] = shift + perov.octahedra[octa,X_anion+1]
    return(X_images)

def _find_shared_X_atoms(perov):
    if perov.octahedra is None:
        perov.identify_octahedra()

    n_octahedra = perov.octahedra.shape[0]
    octa_adjacency = np.zeros((n_octahedra, n_octahedra))

    # N_octa, 6Xcations, 27 images, 3 cartesian coords
    X_images = _get_periodic_X_images(perov)

    for oct_i in range(perov.octahedra.shape[0]):
        for oct_j in range(perov.octahedra.shape[0]):
            if oct_j < oct_i:
                for X_anion_i in range(6):
                    curr_X = perov.octahedra[oct_i,X_anion_i] # +1 because 0'th element is always B-cation
                    for X_anion_j in range(6):
                        #print(X_images[oct_j, X_anion_j].shape)
                        #print((X_images[oct_j, X_anion_j] - curr_X).shape)
                        norms = np.linalg.norm(X_images[oct_j, X_anion_j] - curr_X, axis = 1)
                        print(norms)







    

