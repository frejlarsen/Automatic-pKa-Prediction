# es_init.py

import subprocess
import re
import time

headersgas = '/home/faln/bachelor/headers/opt_gas_pm6'

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
    varstrucinp = varstruc[:-4] + '.inp'
    subprocess.call([babel, '-ixyz', varstruc, '-ogamin', varstrucinp, '-xf', headersgas])

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/icharg=0/icharg=1/', varstrucinp])


    subprocess.call(['bash', 'ihrep_script', varstrucinp])


    subprocess.call(['/home/faln/bin/submit_gamess', varstrucinp])

# wait

queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
waiting_time = -1
while len(queuecheck) > 85:
    queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
    waiting_time += 1
    print "Waiting for server.. ", waiting_time 
    time.sleep(1)

# es_solsub.py


headersspe = '/home/faln/bachelor/headers/spe_smd_pm6'


for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstruclog = varstruc[:-4] + '.log'
    varstrucsolinp = varstruc[:-4] + '_sol.inp'

    varspefile = subprocess.check_output(['/home/faln/bin/get_gamess_out', varstruclog, 'gamin', headersspe])
    tempfile = open(varstrucsolinp, "w+")
    tempfile.write(varspefile)
    tempfile.close()

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/icharg=0/icharg=1/', varstrucsolinp])

    subprocess.call(['bash', 'ihrep_script', varstrucsolinp])

    subprocess.call(['/home/faln/bin/submit_gamess', varstrucsolinp])
                                                      

# wait

queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
waiting_time = -2
while len(queuecheck) > 85:
    queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
    waiting_time += 2
    print "Waiting for server(2).. ", waiting_time 
    time.sleep(2)

# es_calc.py

strucfile = open("structure_list.txt", "r+")
structures = strucfile.read().split('\n')
structures = structures[:-1]
strucfile.close()

finalfile = open('energies.csv', "a")

iastruc = structures[-1]
strucbase = iastruc[:-8]

subprocess.call(['mkdir', strucbase])

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstruclog = varstruc[:-4] + '.log'
    varstrucinp = varstruc[:-4] + '.inp'
    varstrucsollog = varstruc[:-4] + '_sol.log'
    varstrucsolinp = varstruc[:-4] + '_sol.inp'
    varstrucheslog = varstruc[:-4] + '_hes.log'
    varstruchesinp = varstruc[:-4] + '_hes.log'


    energies_sol = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'FREE ENERGY OF SOLVATION', varstrucsollog]))
    energies_hof = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'HEAT OF', varstruclog]))
    

    finalfile.write("%s, %s, %s \n" % (varstruc, energies_hof[-1], energies_sol[0]))



finalfile.close()

rmstrucbase = iastruc[:-7] + "*"
subprocess.call(['mv *.log %s' % strucbase], shell = True)
subprocess.call(['mv *.inp %s' % strucbase], shell = True)
subprocess.call(['rm %s' % rmstrucbase], shell = True)
subprocess.call(['rm structure_list.txt'], shell = True)

