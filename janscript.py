import string, math,sys
import numpy as np

def distance(R1, R2):
    dR = (R1 - R2)**2
    return np.sqrt(np.sum(dR))

if __name__ == "__main__":

    filename = sys.argv[1]

    file = open(filename,'r')

    atom = []
    coord = []
    N_atoms = []
    N_coord = []
    bonded_to_N = []
    NHbond = []

    title = " "

    sign = -1 #change to +1 to invert

    # Get number of atoms
    for i in range(3): line = file.readline()
    words = string.split(line)
    atoms = int(words[0])

    # skip 4 lines
    for i in range(4): line = file.readline()

    # Read atom lines
    for i in range(atoms):

        line = file.readline()
        line = line.split()

        atom_id = line[0]
        atom_type = line[1]
        atom_x = float(line[2])
        atom_y = float(line[3])
        atom_z = float(line[4])
        atom_hyp = line[5]

        atom.append(atom_type)
        coord.append(np.array([atom_x, atom_y, atom_z]))

        check_hyp = ['N.3', 'N.2', 'N.ar']

        if any(x in atom_hyp for x in check_hyp):
            N_atoms.append(i)
            N_coord.append([atom_x, atom_y, atom_z])


    # Iterate over found Nitrogens
    for i in range(len(N_atoms)):

        bonded_to_N.append([])

        for j in range(atoms):

            if j != N_atoms[i]:
                r = distance(coord[j], coord[N_atoms[i]])
                # r = dist(coord[j], N_coord[i]) # What is the reason for N_coord???

                # check if bonded
                if r < 1.8:
                    bonded_to_N[i].append(j)
                    NHbond.append(j) 

    for i in range(len(N_atoms)):

        c_ave = np.zeros(3)

        if len(bonded_to_N[i]) > 3: continue #skip quaternary Ns

        for j in range(len(bonded_to_N[i])):
            c_ave += coord[bonded_to_N[i][j]]

        c_ave /= len(bonded_to_N[i])

        r = distance(c_ave, coord[N_atoms[i]])

        c_ave = coord[N_atoms[i]] + sign*(c_ave - coord[N_atoms[i]])/r

        coord.append(c_ave)
        atom.append('H')
        atoms += 1

    print '{0:3d}'.format(atoms)
    print '{0:50s}'.format(title)

    for i in range(atoms):
        print atom[i], coord[i][0], coord[i][1], coord[i][2] 
