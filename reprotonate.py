#!/usr/bin/env python

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

    title = " "

    sign = -1 #change to +1 to invert

    # Get number of atoms
    atoms = int(file.readline())
    file.readline()

    for i in range(atoms):

        line = file.readline()
        line = line.split()

        atom_type = line[0]
        atom_x = float(line[1])
        atom_y = float(line[2])
        atom_z = float(line[3])

        atom.append(atom_type)
        coord.append(np.array([atom_x, atom_y, atom_z]))


        if atom_type == "N":
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
                if r < 1.8 and atom[j] == "H":
                    bonded_to_N[i].append(j)
    
    MolNumber = 0
    
    # MOLECULE HAS 1 NITROGEN ATOM
    
    if len(bonded_to_N) == 1: 
    
        MolNumber += 1
        Namestring = filename[:-4] + str(MolNumber)
        Namestring = Namestring.replace("-", "_") + "+.xyz"

        f = open(Namestring,'w')
            
        f.write('{0:3d}'.format(atoms))
        f.write('{0:50s}'.format(title))
        f.write("\n")

        for i in range(atoms):
            Writestring = "\n" + str(atom[i]) + " " + str(coord[i][0]) + " " + str(coord[i][1]) + " " + str(coord[i][2])
            f.write(Writestring)
            
        f.close

    # MOLECULE HAS 2 NITROGEN ATOM

    if len(bonded_to_N) == 2:

        
        bonded0 = bonded_to_N[0] + bonded_to_N[1]              

        for x in range(len(bonded0)):
            
            MolNumber += 1
            Namestring = filename[:-4] + str(MolNumber)
	    Namestring = Namestring.replace("-", "_") + "+.xyz"
            

            f = open(Namestring,'w')
            
            f.write('{0:3d}'.format(atoms-1))
            f.write('{0:50s}'.format(title))
            f.write("\n")
    
            for i in range(atoms):
                if i == bonded0[x]:
                    continue
                else:
                    Writestring = "\n" + str(atom[i]) + " " + str(coord[i][0]) + " " + str(coord[i][1]) + " " + str(coord[i][2])
                    f.write(Writestring)
            f.close


    if len(bonded_to_N) == 0 or len(bonded_to_N) > 2:
        print "0 or more than 2 nitrogen atoms were present. Please complain @ Frej."
