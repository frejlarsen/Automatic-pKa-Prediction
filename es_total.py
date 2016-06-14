# es_init.py

import sys
import subprocess
import re
import time

start_time = time.time()

headersgas = '/home/faln/bachelor/headers/opt_gas_pm6-d3h+'

babel = '/opt/openbabel/openbabel-master/bin/babel'

def wait(output):
    queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
    waiting_time = -3
    while len(queuecheck) > 85:
        queuecheck = subprocess.check_output(["squeue -u faln"], shell = True)
        waiting_time += 3
        print "Waiting for server..%s " % output, waiting_time
        time.sleep(3)
    return


varfile = sys.argv[1]
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

    #subprocess.call(['sed -i s/opttol=5.0e-4/opttol=1.0e-4/ %s' % varstrucinp], shell = True)
    
    #subprocess.call(['bash', 'ihrep_script', varstrucinp])


    subprocess.call(['/home/faln/bin/submit_gamess', varstrucinp])

# wait

wait("1")

# es_solsub.py


headersspe = '/home/faln/bachelor/headers/spe_smd_pm6-d3h+'

strucfile = open("structure_list.txt", "r+")
structures = strucfile.read().split('\n')
structures = structures[:-1]
strucfile.close()

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstruclog = varstruc[:-4] + '.log'
    varstrucsolinp = varstruc[:-4] + '_sol.inp'

    varspefile = subprocess.check_output(['/home/faln/bin/get_gamess_out', varstruclog, 'gamin', headersspe])
    tempfile = open(varstrucsolinp, "w+")
    tempfile.write(varspefile)
    tempfile.close()
    

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/icharg=0/icharg=1/', varstrucsolinp])

    #subprocess.call(['bash', 'ihrep_script', varstrucsolinp])

    subprocess.call(['/home/faln/bin/submit_gamess', varstrucsolinp])
                                                      

# es_hessub.py


headershes = '/home/faln/bachelor/headers/hes_gas_pm6-d3h+'

strucfile = open("structure_list.txt", "r+")
structures = strucfile.read().split('\n')
structures = structures[:-1]
strucfile.close()

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstruclog = varstruc[:-4] + '.log'
    varstruchesinp = varstruc[:-4] + '_hes.inp'

    varspefile = subprocess.check_output(['/home/faln/bin/get_gamess_out', varstruclog, 'gamin', headershes])
    tempfile = open(varstruchesinp, "w+")
    tempfile.write(varspefile)
    tempfile.close()

    if '+' in varstruc:
        subprocess.call(['sed', '-i', 's/icharg=0/icharg=1/', varstruchesinp])

    #subprocess.call(['bash', 'ihrep_script', varstruchesinp])

    subprocess.call(['/home/faln/bin/submit_gamess', varstruchesinp])

# wait

wait("2")

# es_calc.py

strucfile = open("structure_list.txt", "r+")
structures = strucfile.read().split('\n')
structures = structures[:-1]
strucfile.close()

finalfile = open('energies.csv', "a")

iastruc = structures[-1]
strucbase = " ".join(re.findall("[a-zA-Z]+", iastruc[:-8]))

subprocess.call(['mkdir', strucbase])

for varstruc in structures: # iterating over each structure made by splitxyz.sh
    varstruclog = varstruc[:-4] + '.log'
    varstrucinp = varstruc[:-4] + '.inp'
    varstrucsollog = varstruc[:-4] + '_sol.log'
    varstrucsolinp = varstruc[:-4] + '_sol.inp'
    varstrucheslog = varstruc[:-4] + '_hes.log'
    varstruchesinp = varstruc[:-4] + '_hes.log'

    # REDO IF IMAGINARY FREQ..................................................................... 

    hasimag = " "
    grepvar = "grep IMAG " + varstrucheslog + ";exit 0"
    imaginary = subprocess.check_output(grepvar, stderr=subprocess.STDOUT, shell = True) 
    if len(imaginary) > 0:
	print varstrucheslog, " has an imaginary frequency!"
	subprocess.call('rm %s' % varstrucsolinp, shell = True)
	subprocess.call('rm %s' % varstruchesinp, shell = True)
	subprocess.call('rm %s' % varstrucsollog, shell = True)
        subprocess.call('rm %s' % varstrucheslog, shell = True)
        subprocess.call('sed -i s/opttol=5.0e-4/opttol=1.0e-4/ %s' % varstrucinp, shell = True)
        subprocess.call(['/home/faln/bin/submit_gamess', varstrucinp])
        wait("imag")
        
        varspefile = subprocess.check_output('/home/faln/bin/get_gamess_out %s gamin %s' % (varstruclog, headersspe), shell = True)
        tempfile = open(varstrucsolinp, "w+")
        tempfile.write(varspefile)
        tempfile.close()
        
        time.sleep(1)
        if '+' in varstruc:
            subprocess.call('sed -i s/icharg=0/icharg=1/ %s' % varstrucsolinp, shell = True)
        
        #subprocess.call('bash ihrep_script %s' % varstrucsolinp, shell = True)
        subprocess.call('/home/faln/bin/submit_gamess %s' % varstrucsolinp, shell = True)
        
        varspefile = subprocess.check_output('/home/faln/bin/get_gamess_out %s gamin %s' % (varstruclog, headershes), shell = True)
        tempfile = open(varstruchesinp, "w+")
        tempfile.write(varspefile)
        tempfile.close()
        
        time.sleep(1)
        if '+' in varstruc:
            subprocess.call('sed -i s/icharg=0/icharg=1/ %s' % varstruchesinp, shell = True)
        subprocess.call('/home/faln/bin/submit_gamess %s' % varstruchesinp, shell = True)
        wait("imag2")

        imaginary = subprocess.check_output(grepvar, stderr=subprocess.STDOUT, shell = True)
        if len(imaginary) > 0:
            print "Trying with a lower opttol (5.0e-5)."
    	    subprocess.call('rm %s' % varstrucsolinp, shell = True)
	    subprocess.call('rm %s' % varstruchesinp, shell = True)
	    subprocess.call('rm %s' % varstrucsollog, shell = True)
	    subprocess.call('rm %s' % varstrucheslog, shell = True)
	        
	    subprocess.call('sed -i s/opttol=1.0e-4/opttol=5.0e-5/ %s' % varstrucinp, shell = True)
            subprocess.call(['/home/faln/bin/submit_gamess', varstrucinp])
            wait("imag3")

            varspefile = subprocess.check_output('/home/faln/bin/get_gamess_out %s gamin %s' % (varstruclog, headersspe), shell = True)
            tempfile = open(varstrucsolinp, "w+")
            tempfile.write(varspefile)
            tempfile.close()

            if '+' in varstruc:
                subprocess.call('sed -i s/icharg=0/icharg=1/ %s' % varstrucsolinp, shell = True)

            #subprocess.call('bash ihrep_script %s' % varstrucsolinp, shell = True)
            subprocess.call('/home/faln/bin/submit_gamess %s' % varstrucsolinp, shell = True)

            varspefile = subprocess.check_output('/home/faln/bin/get_gamess_out %s gamin %s' % (varstruclog, headershes), shell = True)
            tempfile = open(varstruchesinp, "w+")
            tempfile.write(varspefile)
            tempfile.close()

            if '+' in varstruc:
                subprocess.call('sed -i s/icharg=0/icharg=1/ %s' % varstruchesinp, shell = True)
            subprocess.call('/home/faln/bin/submit_gamess %s' % varstruchesinp, shell = True)
            wait("imag4")

            imaginary = subprocess.check_output(grepvar, stderr=subprocess.STDOUT, shell = True)
	    if len(imaginary) > 0:
                print varstrucheslog, " still contains an imaginary frequency."
                hasimag = "X"


    # REDO IF IMAGINARY FREQ........................................................................

    energies_sol = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'FREE ENERGY OF SOLVATION', varstrucsollog]))
    energies_hes = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'HEAT OF', varstruclog]))
    energies_rroh = re.compile(r"[+-]?\d+(?:\.\d+)?").findall(subprocess.check_output(['grep', 'TOTAL', varstrucheslog]))

    finalfile.write("%s, %s, %s, %s, %s \n" % (varstruc, energies_hes[-1], energies_rroh[-9], energies_sol[0], hasimag))


finalfile.close()

rmstrucbase = iastruc[:-7] + "*"

subprocess.call(['mv *.log %s' % strucbase], shell = True)
subprocess.call(['mv *.inp %s' % strucbase], shell = True)
subprocess.call(['rm %s' % rmstrucbase], shell = True)
subprocess.call(['rm structure_list.txt'], shell = True)


print "Done. Elapsed time: ", time.time() - start_time, " seconds."
