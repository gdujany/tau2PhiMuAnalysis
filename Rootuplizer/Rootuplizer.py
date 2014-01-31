# Use DaVinci v33r8 and ganga 6
import sys, os
# to be able to import jobSetup using gaudirun
sys.path.append(os.getcwd())
from jobSetup import *

try:
    dataSample = dataSamples[open('dataSample.txt').readline()] 
except IOError:
    pass # keep dataSample defined in jobSetup.py and loaded with from import *



#location = '/Event/AllStreams/pPhys/Particles'

line = "LFVLinesTau2PhiMuLine"
#line = "BetaSJpsi2MuMuDetachedLine"
#location = "/Event/Dimuon/Phys/"+line+"/Particles" #check if it's the correct one
location = "Phys/"+line+"/Particles" #check if it's the correct one

dec = '[tau- -> ^(phi(1020) -> ^K+ ^K-) ^mu-]CC'

from Gaudi.Configuration import *
import GaudiKernel.SystemOfUnits as Units

from Configurables import DeterministicPrescaler

############################################################
## Get data and selection
############################################################

from PhysSelPython.Wrappers import Selection, SelectionSequence, DataOnDemand, AutomaticData
from StandardParticles import StdLooseMuons, StdLooseKaons
from Configurables import FilterDesktop, CombineParticles, OfflineVertexFitter, LoKi__HDRFilter 
from GaudiKernel.PhysicalConstants import c_light

# Here I reconstruct the tau with complicated things and cut ...
# The output will then go to the tuple-maker

evtPreselectors = []

if dataSample.isPrescaled:
    prescaler =  DeterministicPrescaler("Prescaler", AcceptFraction = 0.1)
    evtPreselectors.append(prescaler)
    
# Stripping filter
strippingFilter = LoKi__HDRFilter( 'StripPassFilter', Code="HLT_PASS('Stripping"+line+"Decision')", Location="/Event/Strip/Phys/DecReports" )
evtPreselectors.append(strippingFilter)

# Muons and kaons
looseMuons = DataOnDemand(Location = 'Phys/StdLooseMuons/Particles')
looseKaons = DataOnDemand(Location = 'Phys/StdLooseKaons/Particles')


# Select Phi
recoPhi = CombineParticles("Phi2KK")
recoPhi.DecayDescriptor = 'phi(1020) -> K+ K-'
recoPhi.DaughtersCuts = {"K+": "(ISLONG) & (TRCHI2DOF < 3 ) & (TRGHOSTPROB<0.3) & ( BPVIPCHI2 () >  9 ) & (PT>300*MeV) & (PIDK > 5)"}
recoPhi.CombinationCut =  "(ADAMASS('phi(1020)')<10*MeV)"
recoPhi.MotherCut = " ( VFASPF(VCHI2) < 10 ) & (MIPCHI2DV(PRIMARY)> 16.)"


phi_selection = Selection('SelPhi2KK', Algorithm = recoPhi, RequiredSelections = [ looseKaons ])


# Select Tau
recoTau = CombineParticles("Tau2PhiMu")
recoTau.DecayDescriptor = '[tau- -> phi(1020) mu-]cc'
recoTau.DaughtersCuts = { "mu-" : " ( PT > 300 * MeV )  & ( BPVIPCHI2 () >  9 ) & ( TRCHI2DOF < 3 )& (TRGHOSTPROB<0.3)" }
recoTau.CombinationCut = "(ADAMASS('tau-')<150*MeV)"

recoTau.MotherCut = "( VFASPF(VCHI2) < 10 ) &  ( (BPVLTIME () * c_light)   > 200 * micrometer ) &  ( BPVIPCHI2() < 100 ) "

tau_selection = Selection('SelTau2PhiMu', Algorithm = recoTau, RequiredSelections = [ looseMuons, phi_selection ])


tau_sequence = SelectionSequence('SeqTau2PhiMu',
                                 TopSelection = tau_selection,
                                 EventPreSelector = evtPreselectors)

                                 

# ## Per i dati forse funziona:

# tau_stripped = AutomaticData(Location = location)
## #prescaler =  DeterministicPrescaler("Prescaler", AcceptFraction = 1.0)
# tau_filter = FilterDesktop('tauFilter', Code = 'ALL')
# tau_selection = Selection('SelTau2PhiMu', Algorithm = tau_filter, RequiredSelections = [ tau_stripped ])
# tau_sequence = SelectionSequence('SeqTau2PhiMu',
#                                  TopSelection = tau_selection)
                                   #EventPreSelector = prescaler)


############################################################

############################################################
## Make tuple
############################################################

from Configurables import FitDecayTrees, DecayTreeTuple, TupleToolDecayTreeFitter, TupleToolDecay, TupleToolTrigger, TupleToolTISTOS, TupleToolPropertime, PropertimeFitter, TupleToolKinematic, TupleToolGeometry, TupleToolEventInfo, TupleToolPrimaries, TupleToolPid, TupleToolTrackInfo, TupleToolRecoStats, TupleToolMCTruth, TupleToolMCBackgroundInfo, LoKi__Hybrid__TupleTool
from DecayTreeTuple.Configuration import *


tuple = DecayTreeTuple() # I can put as an argument a name if I use more than a DecayTreeTuple
tuple.Inputs = [ tau_sequence.outputLocation() ]
tuple.Decay = dec
tuple.ToolList = ['TupleToolKinematic',
                  'TupleToolEventInfo',
                  'TupleToolTrackInfo',
                  'TupleToolPid',
                  #'TupleToolTrackIsolation',
                  #'TupleToolTrigger',
                  #'TupleToolAngles',
                  #'TupleToolPropertime',
                  #'TupleToolP2VV',
                  #"TupleToolTISTOS",
                  ]

# tuple.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_All")
# tuple.LoKi_All.Variables = {'P2' : 'P*P',}

if dataSample.isMC:
    from Configurables import MCDecayTreeTuple, MCTupleToolKinematic, TupleToolMCTruth
    tuple.addTupleTool('TupleToolMCTruth/MCTruth')
    tuple.MCTruth.ToolList = ['MCTupleToolKinematic',
                      ]
    #tuple.addTupleTool( "TupleToolMCBackgroundInfo")

branches = {'Tau' : '[tau- -> (phi(1020) -> K+ K-) mu-]CC', #automatically choose the head
            'Phi' : '[tau- -> ^(phi(1020) -> K+ K-) mu-]CC',
            'KPlus' : '[tau- -> (phi(1020) -> ^K+ K-) mu-]CC',
            'KMinus' : '[tau- -> (phi(1020) -> K+ ^K-) mu-]CC',
            'Mu' : '[tau- -> (phi(1020) -> K+ K-) ^mu-]CC'}

tuple.addBranches(branches)

tuple.Tau.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_Tau")
tuple.Tau.LoKi_Tau.Variables =  {
    "DMASS" : "DMASS('tau-')",
    "BPVDIRA" : "BPVDIRA",
    "IPS_Tau" : "MIPCHI2DV(PRIMARY)",
    "VFASPF_VCHI2" : "VFASPF(VCHI2)",
    "VFASPF_CHI2DOF" : "VFASPF(VCHI2/VDOF)",
    "CTAU" : "BPVLTIME () * c_light",
    "BPVIPCHI2" : "BPVIPCHI2()",

    }

tuple.Phi.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_Phi")
tuple.Phi.LoKi_Phi.Variables =  {
    'DMASS' : "DMASS('phi(1020)')",
    'VFASPF_VCHI2' : 'VFASPF(VCHI2)',
    'MIPCHI2DV_PRIMARY' : 'MIPCHI2DV(PRIMARY)',

#    'M_KK1' : "CHILD(M,1)",#+CHILD(PE,2))^2",# - (CHILD(PX,1)+CHILD(PX,2))^2 - (CHILD(PY,1)+CHILD(PY,2))^2 -(CHILD(PZ,1)+CHILD(PZ,2))^2 ",
#    'M_KK2' : "AM"
    }

tuple.Mu.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_Mu")
tuple.Mu.LoKi_Mu.Variables =  {
    'LoKi_PT' : 'PT',
    'BPVIPCHI2' : 'BPVIPCHI2()',
    'TRCHI2DOF' : 'TRCHI2DOF',
    'TRGHOSTPROB' : 'TRGHOSTPROB',
    }

def mySharedConf(branch):
  atool=branch.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_K")
  atool.Variables =  {
      'LoKi_PT' : 'PT',
      'TRCHI2DOF' : 'TRCHI2DOF',
      'TRGHOSTPROB' : 'TRGHOSTPROB',
      'BPVIPCHI2' : 'BPVIPCHI2()',
      }

mySharedConf(tuple.KPlus)
mySharedConf(tuple.KMinus)

# Decay Tree fitter

variables_All = ('M', 'MM', 'P', 'PT', 'E', 'PX', 'PY', 'PZ')
particles_functors = {'Tau' : '{}',
                      'Phi' : 'CHILD({}, 1)',
                      'KPlus' : 'CHILD(CHILD({}, 1), 1)',
                      'KMinus' : 'CHILD(CHILD({}, 2), 1)',
                      'Mu' : 'CHILD({}, 2)'}
tuple.Tau.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_DTF")
tuple.Tau.LoKi_DTF.Variables = {'DTF_CHI2' : "DTF_CHI2(False, 'phi(1020)')",
                                'DTF_NDOF' : "DTF_NDOF(False, 'phi(1020)')",
                                'DTF_CHI2NDOF' : "DTF_CHI2NDOF(False, 'phi(1020)')",
                                'DTF_PROB' : "DTF_PROB(False, 'phi(1020)')"}
                                
for partName, partFunctor in particles_functors.items():
    for var in variables_All:
        tuple.Tau.LoKi_DTF.Variables['DTF_{}_{}'.format(partName, var)] = "DTF_FUN ( {} , False, 'phi(1020)' )".format(partFunctor).format(var)
#tuple.Tau.LoKi_DTF.OutputLevel = VERBOSE

tuple.Tau.LoKi_DTF.Variables.update({
    'DTFTau_CHI2NDOF' : "DTF_CHI2NDOF(False, 'tau-')",
    'DTFTau_PROB' : "DTF_PROB(False, 'tau-')",
    'DTFTau_Phi_M' : "DTF_FUN ( CHILD(M, 1) , False, 'tau-' )"
    })

# Triggers:
L0_list = ['L0HadronDecision', 'L0MuonDecision', 'L0DiMuonDecision']
HLT1_list = ['Hlt1TrackAllL0Decision', 'Hlt1TrackMuonDecision']
HLT2_list = ['Hlt2CharmHadD2HHHDecision', 'Hlt2IncPhiDecision', 'Hlt2SingleMuonDecision', 'Hlt2CharmHadLambdaC2KPKDecision', 'Hlt2CharmHadLambdaC2KPPiDecision', 'Hlt2TopoMu3BodyBBDTDecision']

tuple.Tau.addTupleTool('TupleToolTISTOS/TISTOS')
tuple.Tau.TISTOS.VerboseL0   = True
tuple.Tau.TISTOS.VerboseHlt1 = True
tuple.Tau.TISTOS.VerboseHlt2 = True
tuple.Tau.TISTOS.TriggerList = L0_list + HLT1_list + HLT2_list



## Still have to add triggers and MC-match

if dataSample.isMC:
    mcTuple = MCDecayTreeTuple() # I can put as an argument a name if I use more than a MCDecayTreeTuple
    #mcTuple.Inputs = [ tau_sequence.outputLocation() ]
    mcTuple.ToolList = ['MCTupleToolKinematic',
                        'TupleToolEventInfo'
                      ]
    mcTuple.addBranches(branches)

    ## at a certain point add personalized leaves with LoKi::Hybrid::TupleTool
    ## Still have to add triggers

    mcTuple.Decay = dec


############################################################


############################################################
## Configure DaVinci
from Configurables import DaVinci

DaVinci().Lumi = not dataSample.isMC
DaVinci().Simulation = dataSample.isMC
DaVinci().DataType = '2012'
DaVinci().EvtMax = nEvents # 100000

DaVinci().DDDBtag = dataSample.DDDBtag 
DaVinci().CondDBtag = dataSample.CondDBtag 

#DaVinci().EventPreFilters += [strippingFilter]
if dataSample.isMC: DaVinci().UserAlgorithms += [mcTuple]

#MySequencer = GaudiSequencer('Sequence')
#MySequencer.Members = [ strippingFilter, tau_sequence.sequence(), tuple ]
#DaVinci().appendToMainSequence(MySequencer)

tau_sequence.sequence().Members += [tuple]
DaVinci().appendToMainSequence( [ tau_sequence.sequence() ])
#DaVinci().UserAlgorithms += [tuple]

#DaVinci().UserAlgorithms += [ strippingFilter, tau_sequence.sequence(), tuple]

DaVinci().HistogramFile = "DVHistos.root"
DaVinci().TupleFile = dataSample.outputNtupleName


# Come funzionano le sequenze? Perche' cerca di fare la tupla anche negli eventi dove non passa la selezione e non ricostruisce il tau?
# Qual'e` la differenza tra appendToMainSequence e UserAlgorithms+= ?

### DEBUG #######
# from Configurables import PrintDecayTree, PrintDecayTree
# printTree = PrintDecayTree(Inputs = [ location ])

# DaVinci().appendToMainSequence( [ printTree ] )

# from Configurables import PrintMCTree, PrintMCDecayTreeTool
# mctree = PrintMCTree("PrintTrueTau")
# mctree.addTool(PrintMCDecayTreeTool, name = "PrintMC")
# mctree.PrintMC.Information = "Name"
# mctree.ParticleNames = [ "tau+", "tau-" ]
# mctree.Depth = 1
# DaVinci().appendToMainSequence( [ mctree ] )



## N.B.
# need to find a smart way to obtain both tuple with all gens and only selected
