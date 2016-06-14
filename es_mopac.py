# es_init.py

import subprocess
import re
import time

headersmop = '/home/faln/bachelor/headers/opt_gas_pm6-mopac'
headerscos = '/home/faln/bachelor/headers/spe_cosmo_pm6'

babel = '/opt/openbabel/openbabel-master/bin/babel'

varfile = raw_input("Which file would you like to process? ")
if varfile[-4:] != '.xyz': # check for correct file input
    print "That doesn't look like a .xyz file, please try again."
    quit()


subprocess.call(['/home/faln/bin/splitxyz.sh', varfile])

strucfile = open("structure_list.txt", "r+")
structures = strucfile.read().split('\n')
structures = structures[:-1]
strucfile.close()

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstrucmop = varstruc[:-4] + '.mop'
    subprocess.call(['babel', '-ixyz', varstruc, '-omop', varstrucmop, '-xf', headersmop])

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/CHARGE=0/CHARGE=1/', varstrucmop])

    subprocess.call(['/home/faln/bin/submit_mopac', varstrucmop])


# wait

queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
waiting_time = 0
while len(queuecheck) > 85:
    queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
    waiting_time += 3
    print "Waiting for server.. ", waiting_time 
    time.sleep(3)


# es_cos.py

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstrucout = varstruc[:-4] + '.out'
    varstruccos = varstruc[:-4] + '_cos.mop'
    
    subprocess.call(['%s -imopout %s -omop %s -xf %s' % (babel, varstrucout, varstruccos, headerscos)], shell = True)

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/CHARGE=0/CHARGE=1/', varstruccos])

    subprocess.call(['/home/faln/bin/submit_mopac', varstruccos])


# wait

queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
waiting_time = 0
while len(queuecheck) > 85:
    queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
    waiting_time += 3
    print "Waiting for server(2).. ", waiting_time 
    time.sleep(3)


# es_calc.py


finalfile = open('energies.csv', "a")

iastruc = structures[-1]
strucbase = iastruc[:-8]

subprocess.call(['mkdir', strucbase])

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstrucout = varstruc[:-4] + '.out'
    varstruccusout = varstruc[:-4] + '_cos.out'


    energies_mop = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'FINAL HEAT OF FORMATION', varstrucout]))
    energies_cos = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'FINAL HEAT OF FORMATION', varstruccusout]))
    energies_diff = float(energies_mop[0]) - float(energies_cos[0])

    finalfile.write("%s, %s, %s, %s \n" % (varstruc, energies_cos[0],energies_mop[0], energies_diff))


finalfile.close()

rmstrucbase = iastruc[:-7] + "*"
subprocess.call(['mv *.out %s' % strucbase], shell = True)
subprocess.call(['rm %s' % rmstrucbase], shell = True)
subprocess.call(['rm structure_list.txt'], shell = True)

