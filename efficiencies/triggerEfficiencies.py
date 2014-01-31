#!/usr/bin/env python

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'Evaluate triger efficiency')
    parser.add_argument('-a','--all',help='recompute efficiencies running over ntuples',action='store_true')
    parser.add_argument('--onData',help='run on data instead of MC',action='store_true')
    args = parser.parse_args()
##########################


from efficiencies import *
from ROOT import TFile, TTree
from array import array
import sys
sys.path.append('..')
from pyUtils import *


# Triggers:
L0_list = ['L0Global_TIS', 'L0Global_TOS', 'L0HadronDecision_TOS', 'L0MuonDecision_TOS', 'L0DiMuonDecision_TOS']
HLT1_list = ['Hlt1TrackAllL0Decision_TOS', 'Hlt1TrackMuonDecision_TOS']
HLT2_list = ['Hlt2CharmHadD2HHHDecision_TOS', 'Hlt2IncPhiDecision_TOS', 'Hlt2SingleMuonDecision_TOS', 'Hlt2CharmHadLambdaC2KPKDecision_TOS', 'Hlt2CharmHadLambdaC2KPPiDecision_TOS', 'Hlt2TopoMu3BodyBBDTDecision_TOS']

def get_counters(tree):
    '''
    Receive as an input the tree and give as an output a dictionary with the number of events wich pass each trigger line
    I also have keys "Total", "Total_L0", "Total_HLT1" and "Total_HLT2"
    '''
    tree.SetBranchStatus("*",0)
    branches = ['Tau_'+i for i in L0_list+ HLT1_list + HLT2_list]

    counters = {}
    for trigger in L0_list + HLT1_list + HLT2_list:
        counters[trigger] = 0
    
    for var in branches:
        tree.SetBranchStatus(var,1)
        exec var+' = array("d",[0])'
        exec "tree.SetBranchAddress( '"+var+"', "+var+" )"

    nEvents = tree.GetEntries()
    #nEvents = 10000
    counters['Total'] = nEvents
    for trigger in ('L0', 'HLT1', 'HLT2'):
        counters['Total_'+trigger] = 0
    
    for cont, entrie in enumerate(tree):
        if cont == nEvents: break
        if cont % 20000 == 0:
            print 'processing entrie ', cont, ' / ', nEvents,' : ', (cont*100)/nEvents,'%'

        isPassedL0 = False
        for trigger in L0_list:
            exec 'if Tau_'+trigger+'[0]: counters[trigger] += 1; isPassedL0 = True'

        isPassedHLT1 = False
        if isPassedL0:
            counters['Total_L0'] += 1
            for trigger in HLT1_list:
                exec 'if Tau_'+trigger+'[0]: counters[trigger] += 1; isPassedHLT1 = True'

        isPassedHLT2 = False
        if isPassedHLT1:
            counters['Total_HLT1'] += 1
            for trigger in HLT2_list:
                exec 'if Tau_'+trigger+'[0]: counters[trigger] += 1; isPassedHLT2 = True'

        if isPassedHLT2:
            counters['Total_HLT2'] += 1

    return counters
        

        

def get_efficiencies(counters):
    '''
    Receive the dictionary of counters produced by the function get_counters and return a
    dictionary of efficiencies, one for each trigger line, with respect to the previous trigger stage
    '''

    efficiencies = {}
    
    for trigger in L0_list + ['Total_L0']:
        efficiencies[trigger] = Efficiency(N_gen=counters['Total'], N_sel=counters[trigger])

    for trigger in HLT1_list + ['Total_HLT1']:
        efficiencies[trigger] = Efficiency(N_gen=counters['Total_L0'], N_sel=counters[trigger])

    for trigger in HLT2_list + ['Total_HLT2']:
        efficiencies[trigger] = Efficiency(N_gen=counters['Total_HLT1'], N_sel=counters[trigger])

    return efficiencies
    

def printEfficiencies(efficiencies):
    def printEff(eff):
        val, err = roundPair(eff.eff, eff.s_eff)
        print '{0:<37} {1} +- {2}'.format(trigger+':', val, err)

    for trigger in sorted([tr for tr in efficiencies if tr.startswith('L0') or tr.endswith('L0')], key=lambda tr: efficiencies[tr].eff):
        printEff(efficiencies[trigger])
    print ''

    for trigger in sorted([tr for tr in efficiencies if tr.startswith('Hlt1') or tr.endswith('HLT1')], key=lambda tr: efficiencies[tr].eff):
        printEff(efficiencies[trigger])
    print ''

    for trigger in sorted([tr for tr in efficiencies if tr.startswith('Hlt2') or tr.endswith('HLT2')], key=lambda tr: efficiencies[tr].eff):
        printEff(efficiencies[trigger])
    print ''

    


if __name__ == '__main__':

    import pickle

    file_label = 'MC' #'data'
    #file_label = 'data'

    if args.all:
        if args.onData:
            inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012.root'
        else:
         inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMuFromPDs.root'

        inFile = TFile(inFile_name)
        tree = inFile.Get('DecayTreeTuple/DecayTree')

        counters = get_counters(tree)
        pickle.dump(counters, open('pickles/trigger_conts_'+file_label+'.pkl','wb'))
        ##counters = pickle.load(open('pickles/trigger_conts_'+file_label+'.pkl','rb'))
        efficiencies = get_efficiencies(counters)
        pickle.dump(efficiencies, open('pickles/trigger_effs_'+file_label+'.pkl','wb'))


    else:
        efficiencies = pickle.load(open('pickles/trigger_effs_'+file_label+'.pkl','rb'))



    printEfficiencies(efficiencies)


    


    
