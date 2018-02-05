#! /usr/bin/env python
import commands,sys,os,subprocess,stat,math,pwd
import datetime
import time 
from os import listdir
from os.path import isfile, join
from optparse import OptionParser
import argparse
import random

eos='/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
#MGrelease="2_5_2"
MGrelease="2_5_3"
#MGrelease="2_4_3"

def replace(name,med,hdm,dm,gdm,gq,proc,rand,directory):
    #Avoid restrict cards
    if gq == 1:
        gq=9.999999e-1
    if gdm == 1:
        gdm=9.999999e-1
    #if dm==1:
    #    dm=9.999999e-1
    #theta=0.01

    if proc == 700 or proc == 701:
        print "!!!!!!!!!!!!!!!!",gdm,gq,med,hdm,dm,theta
    if proc == 702:
        print "!!!!!!!!!!!!!!!!",med,dm

    parameterfiles = [ f for f in listdir(directory) if isfile(join(directory,f)) ]    
    for f in parameterfiles:
        with open('%s/%s_tmp' % (directory,f),"wt") as fout: 
            with open(directory+'/'+f        ,"rt") as fin: 
                for line in fin:

                    if proc == 700 or proc == 701: #BBbarDM/Dijet
                        tmpline = line.replace('X_gQ_X'   , str(gq))
                        tmpline = tmpline.replace('X_gX_X'   , str(gdm))
                        tmpline = tmpline.replace('X_tH_X'   , str(theta))
                        tmpline = tmpline.replace('X_MZP_X'  , str(med))
                        tmpline = tmpline.replace('X_MHS_X'  , str(hdm))
                        tmpline = tmpline.replace('X_MX_X'   , str(dm))
                        tmpline = tmpline.replace('MED'     ,str(med))
                        tmpline = tmpline.replace('XHS'     ,str(hdm))
                        tmpline = tmpline.replace('XMASS'   ,str(dm))
                        tmpline = tmpline.replace('PROC'    ,str(proc))
                    elif proc == 702: #pseudoscalar dark photon model
                        tmpline = line.replace('X_MZP_X'  , str(med))
                        tmpline = tmpline.replace('X_MPS_X'   , str(dm))
                        tmpline = tmpline.replace('MED'     ,str(med))
                        tmpline = tmpline.replace('XMASS'   ,str(dm))
                        tmpline = tmpline.replace('PROC'    ,str(proc))
                    elif proc == 703:
                        tmpline = line.replace('X_MZDINPUT_X'  , str(med))
                        tmpline = tmpline.replace('X_DMCHI_X'  , str(hdm))
                        tmpline = tmpline.replace('X_MCHI_X'   , str(dm))
                        tmpline = tmpline.replace('MED'     ,str(med))
                        tmpline = tmpline.replace('XHS'     ,str(hdm))
                        tmpline = tmpline.replace('XMASS'   ,str(dm))
                        tmpline = tmpline.replace('PROC'    ,str(proc))
                fout.write(tmpline)
        os.system('mv %s/%s_tmp %s/%s'%(directory,f,directory,f))

def fileExists(user,filename):
   sc=None
   #print '%s ls eos/cms/store/user/%s/gridpack/%s | wc -l' %(eos,user,filename)
   exists = commands.getoutput('%s ls eos/cms/store/user/%s/gridpack/%s | wc -l' %(eos,user,filename)  )
   if len(exists.splitlines()) > 1: 
      exists = exists.splitlines()[1]
   else:
      exists = exists.splitlines()[0]
   #print exists
   return int(exists) == 1

def loadRestrict(iFile):
    #print iFile
    inputfile =  open(iFile)
    pairs=[]
    for line in inputfile:
        if line.find("#") > -1:
            continue
        tmpline=line.replace("\n","").replace(" ","").replace("\t","")
        lX = tmpline.split(":")[0]
        lY = tmpline.split(":")[1].split(",")
        for pY in lY:
            pairs.append([int(pY),int(lX)])
    return pairs

def checkRestrict(iRestrict,iMMED,iMDM):
    for pair in iRestrict:
        if iMMED == pair[0] and iMDM == pair[1]:
            return True
    return False

aparser = argparse.ArgumentParser(description='Process benchmarks.')
aparser.add_argument('-carddir','--carddir'   ,action='store',dest='carddir',default='Cards/Axial_MonoTop_NLO_Mphi_Mchi_gSM-0p25_gDM-1p0_13TeV-madgraph'   ,help='carddir')
aparser.add_argument('-q'      ,'--queue'      ,action='store',dest='queue'  ,default='2nw'                   ,help='queue')

#Dijet 
aparser.add_argument('-dm'      ,'--dmrange'   ,dest='dmrange' ,nargs='+',type=int,default=[10],help='dark matter mass range')
aparser.add_argument('-hdm'      ,'--hdmrange'   ,dest='hdmrange' ,nargs='+',type=int,default=[50,150],help='dark higgs mass range')
aparser.add_argument('-med'     ,'--medrange'  ,dest='medrange',nargs='+',type=int,default=[50,100,300,500,1000,1500,2000,2500,3000],help='zprime mass range')

#BBbar
#aparser.add_argument('-dm'      ,'--dmrange'   ,dest='dmrange' ,nargs='+',type=int,default=[50,100,150,200,250,300,400],help='dark matter mass range')
#aparser.add_argument('-hdm'      ,'--hdmrange'   ,dest='hdmrange' ,nargs='+',type=int,default=[50],help='dark higgs mass range') #50,70,90
#aparser.add_argument('-med'     ,'--medrange'  ,dest='medrange',nargs='+',type=int,default=[500,1000,1500,2000,2500],help='zprime mass range')

aparser.add_argument('-proc'    ,'--proc'      ,dest='procrange',nargs='+',type=int,     default=[700],help='proc')
aparser.add_argument('-gq'      ,'--gq'        ,dest='gq',nargs='+',type=float,      default=[0.25],help='gq')
aparser.add_argument('-gdm'     ,'--gdm'       ,dest='gdm',nargs='+',type=float,     default=[0.1],help='gdm')
aparser.add_argument('-resubmit','--resubmit'  ,type=bool      ,dest='resubmit',default=False,help='resubmit')
aparser.add_argument('-install' ,'--install'   ,type=bool      ,dest='install' ,default=True ,help='install MG')
aparser.add_argument('-runcms'  ,'--runcms'    ,action='store' ,dest='runcms'  ,default='runcmsgrid_LO.sh',help='runcms')
aparser.add_argument('-release' ,'--release'    ,action='store' ,dest='release'  ,default='2_5_1',help='MG version')

args1 = aparser.parse_args()
MGrelease=args1.release

#print args1.carddir,args1.queue,args1.dmrange,args1.medrange,args1.install

user=pwd.getpwuid( os.getuid() ).pw_name
basedir=os.getcwd()
os.system('rm %s/%s/*~' % (basedir,args1.carddir))

##Get the base files
parameterdir   = [ f for f in listdir(basedir+'/'+args1.carddir) if not isfile(join(basedir+'/'+args1.carddir,f)) ]
parameterfiles = [ f for f in listdir(basedir+'/'+args1.carddir) if     isfile(join(basedir+'/'+args1.carddir,f)) ]
#print parameterfiles,' -',basedir+'/'+args1.carddir,parameterdir,parameterfiles

mgcf = [f for f in parameterfiles if f.find('madconfig') > -1]
proc = [f for f in parameterfiles if f.find('proc')      > -1]
cust = [f for f in parameterfiles if f.find('custom')    > -1]
spin = [f for f in parameterfiles if f.find('madspin')   > -1]
rwgt = [f for f in parameterfiles if f.find('reweight')  > -1]
rtct = [f for f in parameterfiles if f.find('mass')      > -1]

procnamebase = commands.getoutput('cat %s | grep output | awk \'{print $2}\' ' % (basedir+'/'+args1.carddir+'/'+proc[0]))

##Start with the basics download Madgraph and add the options we care  :
if not args1.resubmit and args1.install:
    #os.system('rm -rf /tmp/%s/CMSSW_7_1_25_patch5' % user)
    os.system('rm -rf /tmp/%s/CMSSW_7_1_20' % user)
    #os.system('rm -rf /tmp/%s/CMSSW_9_0_0_pre2' % user)
    os.system('rm -rf /tmp/%s/MG5_aMC_v%s'  % (user,MGrelease))
    #os.system('cp  patches/install.sh .')
    os.system('./install.sh %s' % args1.release)
    os.system(('mv MG5_aMC_v'+MGrelease+' %s_MG5_aMC_v'+MGrelease) % procnamebase)

os.chdir (('%s_MG5_aMC_v'+MGrelease) % procnamebase)

#print "MG config :",mgcf[0],"ProcName : ",procnamebase
if not args1.resubmit and args1.install:
    os.system("cp "+basedir+"/"+args1.carddir+"/%s ." % mgcf[0])
    #os.system("cp /afs/cern.ch/work/b/bmaier/public/xMadGraph243/lhe_parser.py ./madgraph/various/")
    os.system("cp /afs/cern.ch/user/p/pharris/pharris/public/amcatnlo_run_interface.py ./madgraph/interface/amcatnlo_run_interface.py")
    os.system("./bin/mg5_aMC %s" % mgcf[0])

##Now build the directories iterating over options
random.seed(1)
for f in parameterdir:
    if f.find('model') == -1:
        continue
    os.system('echo cp -r %s/%s/%s models/%s' % (basedir,args1.carddir,f,f))
    os.system('cp -r %s/%s/%s models/%s' % (basedir,args1.carddir,f,f))
    os.chdir('models/%s' % (f))
    os.system('python write_param_card.py')
    #os.system('cp param_card.dat restrict_test.dat')
    os.chdir(('%s/%s_MG5_aMC_v'+MGrelease) % (basedir,procnamebase))

restrict = loadRestrict(basedir+"/"+args1.carddir+"/"+rtct[0])

if 'BBbar' in procnamebase: #CORRECT
    print "BBbar"
    medranges = args1.medrange
    dmranges = args1.dmrange
elif 'DiJets' in procnamebase:
    print "DiJets"
    medranges = args1.medrange
    dmranges = args1.hdmrange
else:
    medranges = args1.medrange
    dmranges = args1.dmrange

    print "medranges = ", args1.medrange
    print "dmranges = ", args1.dmrange
    print "Proc = ", args1.procrange
    #print "NONE matches, faulty"
    #exit 

#Loop
#BBabr --> Z' is the med to chi chi
#Dijet --> hs is the med to chi chi, but since chi is fixed, we play the game of Z' is med and hs is decay product
for med    in medranges:
    for dm in dmranges:

        #Special case for dark higgs
        if args1.procrange[0] == 700 or args1.procrange[0] == 701:
            # Overriding dm with hdm and dm stay with dmrange
            if 'DiJets' in procnamebase:
                print "Interpreting Dijet"
                hdm = dm
                dm = args1.dmrange[0]
            if 'BBbar' in procnamebase:
                print "Interpreting BBbar"
                hdm = args1.hdmrange[0]

            print "med :  ", med
            print "hs  : ", hdm
            print "dm  : ", dm
            if 'BBbar' in procnamebase:
                if not checkRestrict(restrict,med,dm):
                    print "Unphysical Phase Space"
                    continue

            tmpMed = med
            tmpDM  = dm 
            tmpHdm = hdm

            if procnamebase.find("BBbar"):
                if med == 2*dm:
                    tmpDM = dm-10
        #pseudoscalar has two scan parameter:
        elif args1.procrange[0] == 702:
            tmpMed = med
            tmpDM  = dm
        #iDM has three scan parameter:
        elif args1.procrange[0] == 703:
            tmpMed = med
            tmpDM  = dm
            tmpHdm = args1.hdmrange[0]

#########################################
        for pProc in args1.procrange:
            rand=random.randrange(1000,9999,1)
            if pProc == 703 or pProc == 701 or pProc == 700:
                procname=procnamebase.replace("PROC",str(pProc)).replace("MED",str(tmpMed)).replace("XMASS",str(tmpDM)).replace("XHS",str(tmpHdm))
            elif pProc == 702:
                print "procnamebase = ", procnamebase
                procname=procnamebase.replace("PROC",str(pProc)).replace("MED",str(tmpMed)).replace("XMASS",str(tmpDM))

            if not args1.resubmit:
                for f in parameterdir:
                    if pProc == 700 or pProc == 701:
                        os.system('cp -r %s/%s/%s models/%s_%s_%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.system('echo cp -r %s/%s/%s models/%s_%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpHdm,tmpDM))
                        print "!!!!!",args1.gdm[0],args1.gq[0]
                        #print 'models/%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc) 
                        replace(procnamebase,tmpMed,tmpHdm,tmpDM,args1.gdm[0],args1.gq[0],pProc,rand,'models/%s_%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.chdir('models/%s_%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.system('python write_param_card.py')
                        #os.system('cp param_card.dat restrict_test.dat')                              
                        os.chdir(('%s/%s_MG5_aMC_v'+MGrelease) % (basedir,procnamebase))
                        os.system('mkdir MG_%s' % (procname))

                    elif pProc == 703:
                        os.system('cp -r %s/%s/%s models/%s_%s_%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.system('echo cp -r %s/%s/%s models/%s_%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpHdm,tmpDM))
                        print "!!!!!",args1.gdm[0],args1.gq[0]
                        #print 'models/%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc) #potential bug
                        replace(procnamebase,tmpMed,tmpHdm,tmpDM,args1.gdm[0],args1.gq[0],pProc,rand,'models/%s_%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.chdir('models/%s_%s_%s_%s_%s' % (f,tmpMed,tmpHdm,tmpDM,pProc))
                        os.system('python write_param_card.py')
                        #os.system('cp param_card.dat restrict_test.dat')
                        os.chdir(('%s/%s_MG5_aMC_v'+MGrelease) % (basedir,procnamebase))
                        os.system('mkdir MG_%s' % (procname))
                    elif pProc == 702:
                        os.system('cp -r %s/%s/%s models/%s_%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpDM,pProc))
                        os.system('echo cp -r %s/%s/%s models/%s_%s_%s' % (basedir,args1.carddir,f,f,tmpMed,tmpDM))
                        print "!!!!!",args1.gdm[0],args1.gq[0]
                        print 'models/%s_%s_%s_%s' % (f,tmpMed,tmpDM,pProc)
                        #potential bug
                        replace(procnamebase,tmpMed,1.,tmpDM,args1.gdm[0],args1.gq[0],pProc,rand,'models/%s_%s_%s_%s' % (f,tmpMed,tmpDM,pProc))
                        os.chdir('models/%s_%s_%s_%s' % (f,tmpMed,tmpDM,pProc))
                        os.system('python write_param_card.py')
                        #os.system('cp param_card.dat restrict_test.dat')
                        os.chdir(('%s/%s_MG5_aMC_v'+MGrelease) % (basedir,procnamebase))
                        os.system('mkdir MG_%s' % (procname))

                
                for f in parameterfiles:
                    with open('MG_%s/%s' % (procname,f), "wt") as fout: 
                        with open(basedir+'/'+args1.carddir+'/'+f        ,"rt") as fin: 
                            for line in fin:
                                tmpline =    line.replace('MED'  ,str(tmpMed))
                                tmpline = tmpline.replace('XMASS',str(tmpDM))
                                if pProc == 703:
                                    tmpline = tmpline.replace('XHS',str(tmpHdm))
                                tmpline = tmpline.replace('PROC' ,str(pProc))
                                tmpline = tmpline.replace('RAND' ,str(random.randrange(1000,9999,1)))
                                fout.write(tmpline)
            
                job_file = open(('%s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh') % (basedir,procnamebase,procname), "wt")
                job_file.write('#!/bin/bash\n')
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/  .     \n') % (basedir,procnamebase,procname))
                job_file.write('export SCRAM_ARCH=slc6_amd64_gcc530 \n')
                #job_file.write('export SCRAM_ARCH=slc6_amd64_gcc481 \n')
                job_file.write('cd /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_1_20/src \n')
                #job_file.write('scramv1 project CMSSW CMSSW_7_1_25_patch5 \n')
                #job_file.write('cd CMSSW_7_1_25_patch5/src \n')
                #job_file.write('scramv1 project CMSSW CMSSW_7_1_20 \n')
                #job_file.write('cd CMSSW_7_1_20/src \n')
                #job_file.write('scramv1 project CMSSW CMSSW_9_0_0_pre2 \n')
                #job_file.write('cd CMSSW_9_0_0_pre2/src \n')
                job_file.write('eval `scramv1 runtime -sh` \n')
                job_file.write('LHAPDF6TOOLFILE=$CMSSW_BASE/config/toolbox/$SCRAM_ARCH/tools/available/lhapdf6.xml \n')
                job_file.write('if [ -e $LHAPDF6TOOLFILE ]; then \n')
                job_file.write('  LHAPDFCONFIG=`cat $LHAPDF6TOOLFILE | grep "<environment name=\\"LHAPDF6_BASE\\"" | cut -d \\" -f 4`/bin/lhapdf-config \n')
                job_file.write('else \n')
                job_file.write('  LHAPDFCONFIG=`echo "$LHAPDF_DATA_PATH/../../bin/lhapdf-config"` \n')
                job_file.write('fi \n')
                job_file.write('export LHAPDF_DATA_PATH=`$LHAPDFCONFIG --datadir` \n')
                job_file.write('LHAPDFINCLUDES=`$LHAPDFCONFIG --incdir` \n')
                job_file.write('LHAPDFLIBS=`$LHAPDFCONFIG --libdir` \n')
                job_file.write('cd - \n')
                job_file.write('cd MG_%s/                       \n' % (procname) )
                job_file.write(('%s/%s_MG5_aMC_v'+MGrelease+'/bin/mg5_aMC  %s  \n') % (basedir,procnamebase,proc[0]) )
                if len(cust) > 0:
                    job_file.write('cp %s %s/                   \n' % (cust[0],procname))
                if args1.runcms.find("NLO") > -1:
                    job_file.write('mv %s process  \n' % (procname))
                    job_file.write('cd process     \n' )
                else:
                    job_file.write('cd  %s                      \n' % (procname) )
                pReweight=False
                for f in parameterfiles:
                    if f.find('dat') > -1:
                        job_file.write('mv ../%s Cards \n' % f)
                    if f.find('.f')  > -1:
                        job_file.write('mv ../%s SubProcesses \n' % f)
                    if f.find('reweight') > -1:
                        job_file.write('cp Cards/%s . \n' % f)
                        pReweight=True
                if args1.runcms.find("NLO") > -1:
                    job_file.write('echo "shower=OFF" > makegrid.dat  \n')
                    if pReweight:
                        job_file.write('echo "reweight=OFF" >> makegrid.dat  \n')
                job_file.write('echo "done"              >>  makegrid.dat  \n')
                if len(cust) > 0:
                    job_file.write('cat %s >> makegrid.dat \n' % (cust[0]))
                #if args1.runcms.find("NLO") == -1:
                job_file.write('echo "set gridpack true" >> makegrid.dat \n')
                job_file.write('echo "" >> makegrid.dat \n')
                job_file.write('echo "done">> makegrid.dat  \n')
                if args1.runcms.find("NLO") > -1:
                    job_file.write('cat makegrid.dat | ./bin/generate_events -n pilotrun \n')
                else:
                    job_file.write('cat makegrid.dat | ./bin/generate_events pilotrun \n')
                job_file.write('cd ..      \n')
                if args1.runcms.find("NLO") > -1:
                    job_file.write('echo "mg5_path = ../mgbasedir"  >> process/Cards/amcatnlo_configuration.txt \n')
                    job_file.write('echo "cluster_temp_path = None" >> process/Cards/amcatnlo_configuration.txt \n')  
                    job_file.write('cd process  \n')
                else:
                    job_file.write('mkdir process \n')
                    job_file.write('mv %s/pilotrun_gridpack.tar.gz                 process  \n' % (procname))
                    job_file.write('mv %s/Events/pilotrun/unweighted_events.lhe.gz process  \n' % (procname))
                    job_file.write('cd process  \n')
                    job_file.write('tar xzf pilotrun_gridpack.tar.gz  \n')
                    job_file.write('rm pilotrun_gridpack.tar.gz  \n')
                    job_file.write('echo "mg5_path = ../../mgbasedir" >> ./madevent/Cards/me5_configuration.txt \n')
                    job_file.write('echo "run_mode = 0" >> ./madevent/Cards/me5_configuration.txt \n')  
                    if len(spin) > 0: 
                        job_file.write('echo "import unweighted_events.lhe.gz"          >  madspinrun.dat \n')
                        job_file.write('cat %s                                          >> madspinrun.dat \n' % spin[0])
                        job_file.write('cat madspinrun.dat | MadSpin/madspin \n')
                        job_file.write('rm madspinrun.dat \n')
                        job_file.write('rm unweighted_events.lhe.gz \n')
                        job_file.write('rm -rf tmp* \n')
                        job_file.write('cp %s/%s/%s process/madspin_card.dat \n' % (basedir,args1.carddir,spin[0]))
                    if pReweight > 0: 
                        job_file.write('mkdir -p madevent/Events/pilotrun \n')
                        job_file.write('cp unweighted_events.lhe.gz madevent/Events/pilotrun \n')
                        #if args1.runcms.find("NLO") > -1:
                        #    job_file.write('echo "f2py_compiler=" `which gfortran` >> ./madevent/Cards/me5_configuration.txt \n')
                        job_file.write('export LIBRARY_PATH=$LD_LIBRARY_PATH \n')
                        job_file.write('cd madevent;./bin/madevent reweight pilotrun;cd .. \n')
                                   
                job_file.write('cd .. \n')
                job_file.write('cp    %s/cleangridmore.sh .      \n'  % (basedir))
                job_file.write('cp    %s/%s               runcmsgrid.sh      \n'  % (basedir,args1.runcms))
                job_file.write('./cleangridmore.sh               \n')
                job_file.write('mkdir  mgbasedir     \n')
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/MadSpin  mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/SysCalc  mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/input    mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/HELAS    mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/HEPTools mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/README   mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/Template mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/VERSION  mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/aloha    mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/bin      mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/madconfig  mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/madgraph   mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/mg5decay   mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/models     mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/tests      mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/vendor     mgbasedir \n') % (basedir,procnamebase))
                #job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/PLUGINS    mgbasedir \n') % (basedir,procnamebase))
                job_file.write(('cp -r %s/%s_MG5_aMC_v'+MGrelease+'/PLUGIN     mgbasedir \n') % (basedir,procnamebase))
                output  ='%s_tarball.tar.xz'                    % (procname)
                job_file.write('XZ_OPT="--lzma2=preset=9,dict=512MiB" tar -cJpsf '+output+' mgbasedir process runcmsgrid.sh \n')
                #job_file.write(('cp -r %s  %s/%s_MG5_aMC_v'+MGrelease+'/         \n') % (output,basedir,procnamebase))
                #job_file.write(('%s rm  eos/cms/store/user/%s/gridpack/%s  \n') % (eos,user,output))
                #job_file.write(('cmsStage %s   /store/user/%s/gridpack/%s  \n') % (output,user,output))
                #job_file.write(('rm  /afs/cern.ch/work/s/%s/analysis/bb_MET_Analysis_13TeV/phil_mg5_test/MadGraph5_aMCatNLO_Grid/gridpack/%s  \n') % (user,output))
                #job_file.write(('scp %s   /afs/cern.ch/work/s/%s/analysis/bb_MET_Analysis_13TeV/phil_mg5_test/MadGraph5_aMCatNLO_Grid/gridpack/%s  \n') % (output,user,output))
                
                job_file.write(('rm   /eos/user/%s/%s/gridpacks/%s  \n') % (user[0],user,output))
                job_file.write(('scp %s  /eos/user/%s/%s/gridpacks/%s  \n') % (output,user[0],user,output))

                job_file.close()
                os.chmod(('%s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh')             % (basedir,procnamebase,procname),0777)
            if os.path.isfile(('%s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh')        % (basedir,procnamebase,procname)):
                #print "Looking",('%s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh')      % (basedir,procnamebase,procname)
                #print "Loooking More",('%s/%s_MG5_aMC_v'+MGrelease+'/%s_tarball.tar.xz') % (basedir,procnamebase,procname)
                #if not os.path.isfile(('%s/%s_MG5_aMC_v'+MGrelease+'/%s_tarball.tar.xz') % (basedir,procnamebase,procname)):
                output     ='%s_tarball.tar.xz'                    % (procname)
                if not fileExists(user,output):
                    os.system(('echo bsub -q  %s -R "rusage[mem=12000]" %s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh') % (args1.queue,basedir,procnamebase,procname))
                    os.system(('bsub -q  %s -R "rusage[mem=12000]" %s/%s_MG5_aMC_v'+MGrelease+'/MG_%s/integrate.sh') % (args1.queue,basedir,procnamebase,procname))


           
#while not completed(args1.name,args1.medrange,args1.dmrange,basedir,args1.carddir):
#    print "Waiting ",datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#    time.sleep(60)
