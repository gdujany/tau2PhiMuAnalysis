#!/usr/bin/env python

from ROOT import TFile, TTree
import os

store_dir = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/'
inFile_names = [ 'D2PhiPi']#, 'tau2PhiMu','data2012']

triggers = ['L0Global_TIS', 'L0MuonDecision_TOS', 'Hlt1TrackAllL0Decision_TOS', 'Hlt1TrackMuonDecision_TOS', 'Hlt2CharmHadD2HHHDecision_TOS', 'Hlt2IncPhiDecision_TOS']

L0_list = ['L0Global_TIS', 'L0MuonDecision_TOS']
HLT1_list = ['Hlt1TrackAllL0Decision_TOS', 'Hlt1TrackMuonDecision_TOS']
HLT2_list = ['Hlt2CharmHadD2HHHDecision_TOS', 'Hlt2IncPhiDecision_TOS']
triggers = [L0_list, HLT1_list, HLT2_list]


cut_string = ' && '.join(['('+' || '.join(['Tau_'+i+'==1' for i in line])+')' for line in triggers])
print cut_string

for name in inFile_names:
    print 'now processing '+name
    inFile = TFile(store_dir+name+'_mixed.root')
    inTree = inFile.Get('DecayTreeTuple/DecayTree')
    outFile = TFile(store_dir+name+'.root', 'recreate')
    directory = outFile.mkdir('DecayTreeTuple')
    directory.cd()
    outTree = inTree.CopyTree(cut_string)
    outFile.Write()
    directory.Purge()
    outFile.Close()
    



