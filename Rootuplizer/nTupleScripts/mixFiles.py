#!/usr/bin/env python
import os

from ROOT import TChain, TTree, TFile

frac_dict = {'tau2PhiMuFromPD': 0.6212705033179445, 'tau2PhiMuFromBD': 0.023306318907189004, 'tau2PhiMuFromBDs': 0.9620888091312731, 'tau2PhiMuFromB': 1.0, 'tau2PhiMuFromPDs': 0.9596286149718892}

# frac_dict = dict(
#     tau2PhiMuFromPDs = 0.960,
#     tau2PhiMuFromBDs = 0.962,
#     # tau2PhiMuFromPD = 0.621,
#     # tau2PhiMuFromBD = 0.023,
#     # tau2PhiMuFromB = 1.,
#     )


store_dir = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/'
outFile_name = store_dir+'tau2PhiMu.root'
#outFile_name = 'lalla.root'

os.chdir(store_dir)


ch_gen = TChain('MCDecayTreeTuple/MCDecayTree')
ch_sel = TChain('DecayTreeTuple/DecayTree')

# Need to initialize them or it crashes
tree = 0
MCtree = 0

for key, frac in frac_dict.items():
    for MagnetPolarization in ('mu', 'md'):
        inFile_name = key+'_'+MagnetPolarization+'.root'
        print 'adding '+inFile_name
        inFile = TFile(inFile_name)
        tree = inFile.Get('DecayTreeTuple/DecayTree')
        MCtree = inFile.Get('MCDecayTreeTuple/MCDecayTree')
        num_sel = tree.GetEntries()*frac
        num_gen = MCtree.GetEntries()*frac
        inFile.Close()
        ch_gen.Add(inFile_name, long(num_gen))
        ch_sel.Add(inFile_name, long(num_sel))


outFile = TFile.Open(outFile_name,'RECREATE')
gen_dir = outFile.mkdir('MCDecayTreeTuple')
sel_dir = outFile.mkdir('DecayTreeTuple')
gen_dir.cd()
print 'Writing MCDecayTreeTuple'
gen_dir.WriteTObject(ch_gen.CloneTree())
gen_dir.Purge()
sel_dir.cd()
print 'Writing DecayTreeTuple'
sel_dir.WriteTObject(ch_sel.CloneTree())
sel_dir.Purge()
outFile.Write()
outFile.Close()

