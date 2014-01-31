############################################################
##  JOB OPTIONS ##

# Class container with various options

decNumbers = dict( tau2PhiMuFromBD = 21513006,
                   tau2PhiMuFromPD = 21513007,
                   tau2PhiMuFromBDs = 23513006,
                   tau2PhiMuFromPDs = 23513007,
                   tau2PhiMuFromB = 31113045 )

MagString = dict(mu = 'MagUp', md = 'MagDown')
    

class VariousOptions:
    def __init__(self, name, MagnetPolarity='mu', CondDBtag=None, DDDBtag='dddb-20120831', input_file=None, isMC=True, isPrescaled=False, outputNtupleName=None):
        self.name = name
        self.MagnetPolarity = MagnetPolarity
        self.DDDBtag = DDDBtag
        self.CondDBtag = CondDBtag if CondDBtag else ('sim-20121025-vc-'+MagnetPolarity+'100' if isMC else 'cond-20121016')
        self.input_file = input_file
        self.outputNtupleName = name+'.root' if not outputNtupleName else outputNtupleName
        self.isPrescaled = isPrescaled
        self.isMC = isMC


class VariousOptionsMC(VariousOptions):
    def __init__(self, name, MagnetPolarity, input_file=None):
        """
        MagnetPolarity in ('mu', 'md')
        """
        VariousOptions.__init__(self, name, input_file=input_file, isMC=True, isPrescaled=False)
        self.decNumber = decNumbers[name[:-3]]
        if not self.input_file:
            self.input_file = 'inputFiles/MC/LFN/MC2012'+str(self.decNumber)+'Beam4000GeV-2012-'+MagString[MagnetPolarity]+'-Nu25-Pythia6Sim08cDigi13Trig0x409f0045Reco14aStripping20NoPrescalingFlaggedSTREAMSDST.py'
############################################################
# Options for various datasets
dataSamples = {}

MC_list = ['tau2PhiMuFromBD', 'tau2PhiMuFromPD', 'tau2PhiMuFromBDs', 'tau2PhiMuFromPDs', 'tau2PhiMuFromB']

for mc_type in MC_list:
    for MagnetPolarity in ('mu', 'md'):
        dataSamples[mc_type+'_'+MagnetPolarity] = VariousOptionsMC(name = mc_type+'_'+MagnetPolarity, MagnetPolarity = MagnetPolarity)

for MagnetPolarity in ('mu', 'md'):
    dataSamples['data2012_'+MagnetPolarity] = VariousOptions(
        name = 'data2012_'+MagnetPolarity, MagnetPolarity = MagnetPolarity, isMC=False, isPrescaled=True,
        input_file = 'inputFiles/data/LFN/LHCbCollision1290000000Beam4000GeV-VeloClosed-'+MagString[MagnetPolarity]+'RealDataReco14Stripping20DIMUONDST.py')

# list of datasamples to be analized
toAnalize = [dataSample for key, dataSample in dataSamples.items() if key[:-3] in MC_list]
toAnalize += [dataSamples['data2012_mu'], dataSamples['data2012_md']]

# For test
#toAnalize =  [dataSamples['tau2PhiMuFromPDs_mu']]
# dataSamples['data2012_md'].isPrescaled = False
# toAnalize = [dataSamples['data2012_md']]



dataSample = toAnalize[0]

# General options
isGrid = True #False
isStoreInCastor = False
nEvents = -1 #1000

#toAnalize = dataSamples.values()

############################################################

# Ganga options

if __name__ == '__main__':

    from subprocess import call

    def submitJob(dataSample):

        with open('dataSample.txt','w') as dsFile:
            dsFile.write(dataSample.name)

        filesPerJob = 5 if dataSample.isMC else 50
    
        j = Job( application = DaVinci( version = 'v33r8' ) )
        j.application.optsfile += [File('Rootuplizer.py')]
        j.application.optsfile += [File(dataSample.input_file)]
        j.inputsandbox += ['dataSample.txt']
        j.name = dataSample.name
        if isGrid:
            j.backend = Dirac()
            j.splitter = SplitByFiles ( filesPerJob = filesPerJob, bulksubmit=True )
            if isStoreInCastor:
                j.outputfiles += [MassStorageFile(dataSample.outputNtupleName)] #Like this it will ends up in my castor area $CASTORHOME/ganga/<job#>/<subjob#>/
            else:
                j.outputfiles += [SandboxFile(dataSample.outputNtupleName)]
                # rm = RootMerger()
                # rm.files = [dataSample.outputNtupleName]
                # rm.overwrite = True #False by default
                # rm.args = '-f2' #pass arguments to hadd
                # j.merger = rm
            j.do_auto_resubmit = True

        else:
            j.backend = Local()#Interactive()
            j.outputfiles += [SandboxFile(dataSample.outputNtupleName)] #Like this it will ends up in my working-dir
            #j.outputfiles += [MassStorageFile(output_Ntuple)] #Like this it will ends up in my castor area $CASTORHOME/ganga/<job#>/<subjob#>/
        j.submit()
        print 'submitted job: ', j.name
        call(['rm','dataSample.txt'])


    for dataSample in toAnalize[:]:
        submitJob(dataSample)
        
        
    #     #call(['ls', dataSample.input_file])
  
