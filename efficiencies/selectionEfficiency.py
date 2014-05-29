#!/usr/bin/env python

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'Evaluate selection efficiency')
    parser.add_argument('-a','--all',help='recompute efficiencies running over ntuples',action='store_true')
    args = parser.parse_args()
##########################

from efficiencies import *
from ROOT import TFile, TTree
import sys
sys.path.append('..')
from pyUtils import *

def get_N_gen(tree):
    return tree.GetEntries()
    

def get_N_sel(tree):
    return tree.GetEntries()



if __name__ == '__main__':

    args.all = True

    if args.all:
        inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/tau2PhiMu_triggerNotApplied.root'
        inFile = TFile(inFile_name)
        tree_sel = inFile.Get('DecayTreeTuple/DecayTree')
        tree_gen = inFile.Get('MCDecayTreeTuple/MCDecayTree')

        N_gen = get_N_gen(tree_gen)
        N_sel = get_N_sel(tree_sel)

        eff = Efficiency(N_gen = N_gen, N_sel = N_sel)

        pickle.dump(eff, open('pickles/selection_eff.pkl','wb'))
        
    
    
