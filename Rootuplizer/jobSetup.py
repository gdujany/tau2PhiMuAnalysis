 ############################################################
##  JOB OPTIONS ##
#
# works with ganga v600r19 (later versions can have troubles with splitting data because too many files)

# Class container with various options

decNumbers = dict( tau2PhiMuFromBD = 21513006,
                   tau2PhiMuFromPD = 21513007,
                   tau2PhiMuFromBDs = 23513006,
                   tau2PhiMuFromPDs = 23513007,
                   tau2PhiMuFromB = 31113045,
                   #Ds2PhiMuNu = 23573003,
                   Ds2PhiMuNuFromB = 23513013,
                   Ds2PhiMuNuFromD = 23513014,
                   D2PhiPiFromB = 21103013,
                   D2PhiPiFromD = 21103014,
                   DsIncl = 23960000,
                   #DIncl = 21960000,
                   )

MagString = dict(mu = 'MagUp', md = 'MagDown')
    

class VariousOptions:
    def __init__(self, name, MagnetPolarity='mu', CondDBtag=None, DDDBtag='dddb-20120831', input_file=None, isMC=True, isPrescaled=False, isNormalization=False, outputNtupleName=None):
        self.name = name
        self.MagnetPolarity = MagnetPolarity
        self.DDDBtag = DDDBtag
        self.CondDBtag = CondDBtag if CondDBtag else ('sim-20121025-vc-'+MagnetPolarity+'100' if isMC else 'cond-20121016')
        self.input_file = input_file
        self.outputNtupleName = name+'.root' if not outputNtupleName else outputNtupleName
        self.isPrescaled = isPrescaled
        self.isNormalization = isNormalization
        self.isMC = isMC


class VariousOptionsMC(VariousOptions):
    def __init__(self, input_file=None,**argd):
        """
        MagnetPolarity in ('mu', 'md')
        """
        VariousOptions.__init__(self, input_file=input_file, isMC=True, isPrescaled=False, **argd)
        self.decNumber = decNumbers[self.name[:-3]]
        if not self.input_file:
            if 'DsIncl' in self.name: ac = 'a'
            elif  'D2PhiPi' in self.name: ac = 'e'
            else: ac = 'c'
            self.input_file = 'inputFiles/MC/LFN/MC2012'+str(self.decNumber)+'Beam4000GeV-2012-'+MagString[self.MagnetPolarity]+'-Nu25-Pythia6Sim08'+ac+'Digi13Trig0x409f0045Reco14aStripping20NoPrescalingFlaggedSTREAMSDST.py'
############################################################
# Options for various datasets
dataSamples = {}

MC_list = [
    'tau2PhiMuFromBD', 'tau2PhiMuFromPD', 'tau2PhiMuFromBDs', 'tau2PhiMuFromPDs', 'tau2PhiMuFromB',
    'D2PhiPiFromB', 'D2PhiPiFromD',
    #'Ds2PhiMuNuFromB', 'Ds2PhiMuNuFromD', 
    #, 'Ds2PhiMuNu', 'DsIncl'
           ]

for mc_type in MC_list:
    for MagnetPolarity in ('mu', 'md'):
        dataSamples[mc_type+'_'+MagnetPolarity] = VariousOptionsMC(name = mc_type+'_'+MagnetPolarity, MagnetPolarity = MagnetPolarity)

# for data_type in ['D2PhiPiFromB', 'D2PhiPiFromD']:
#     for MagnetPolarity in ('mu', 'md'):
#         dataSamples[data_type+'_'+MagnetPolarity].isNormalization = True 

for MagnetPolarity in ('mu', 'md'):
    dataSamples['data2012_'+MagnetPolarity] = VariousOptions(
        name = 'data2012_'+MagnetPolarity, MagnetPolarity = MagnetPolarity, isMC=False, isPrescaled=True,
        input_file = 'inputFiles/data/LFN/LHCbCollision1290000000Beam4000GeV-VeloClosed-'+MagString[MagnetPolarity]+'RealDataReco14Stripping20DIMUONDST.py')

# dataSamples['test_stripping'] = VariousOptions(
#         name = 'test_stripping', isMC=False,  input_file = 'inputFiles/data/LFN/Reco14_Run125113.py')



# list of datasamples to be analized
toAnalize = [dataSample for key, dataSample in dataSamples.items() if key[:-3] in MC_list]
toAnalize += [dataSamples['data2012_mu'], dataSamples['data2012_md']]
# toAnalize += [dataSamples['test_stripping']]
# toAnalize = [dataSamples['data2012_md'], dataSamples['data2012_mu']]
#toAnalize = toAnalize[-1:]


# For test
#toAnalize =  [dataSamples['tau2PhiMuFromPDs_md']]
# dataSamples['data2012_md'].isPrescaled = False
# toAnalize = [dataSamples['data2012_md']]
# toAnalize = [dataSamples['Ds2PhiMuNu_mu'], dataSamples['Ds2PhiMuNu_md']]
#toAnalize = [dataSamples['DsIncl_mu'], dataSamples['DsIncl_md']]

#toAnalize =  [dataSamples['Ds2PhiMuNuFromD_md']]
#toAnalize =  [dataSamples['D2PhiPiFromD_mu']]

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
    
        j = Job( application = DaVinci(version = 'v36r0') )
        j.application.optsfile += [File('Rootuplizer.py')]
        j.application.optsfile += [File(dataSample.input_file)]
        #j.inputdata = j.application.readInputData(dataSample.input_file)
        j.inputsandbox += ['dataSample.txt']
        j.name = dataSample.name
        if isGrid:
            j.backend = Dirac()
            j.splitter = SplitByFiles(filesPerJob = filesPerJob, bulksubmit=True )
            j.backend.settings['BannedSites']  = ['LCG.IN2P3.fr', 'LCG.GRIDKA.de', 'LCG.PIC.es']
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


    for dataSample in toAnalize[12:]:
        submitJob(dataSample)
        
        
    # #     #call(['ls', dataSample.input_file])
  
