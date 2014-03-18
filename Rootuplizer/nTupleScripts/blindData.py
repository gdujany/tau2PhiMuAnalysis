#!/usr/bin/env python

from ROOT import TFile, TTree
inFile_name = 'store/data2012_mu.root'
#inFile_name = 'store/tau2PhiMuFromPDs_mu.root'

outFile_name = 'test.root'

inFile = TFile(inFile_name)

inTree = inFile.Get('DecayTreeTuple/DecayTree')

outFile = TFile(outFile_name, 'recreate')
directory = outFile.mkdir('DecayTreeTuple')
directory.cd()
outTree = inTree.CopyTree('Tau_M<1747 || Tau_M>1807')
outFile.Write()
directory.Purge()
outFile.Close()




