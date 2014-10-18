#!/usr/bin/env python
from __future__ import division

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'Evaluate selection efficiency')
    parser.add_argument('-a','--all',help='recompute efficiencies running over ntuples',action='store_true')
    parser.add_argument('-n', '--D2PhiPi',help='run on normalization sample instead of tau2PhiMu',action='store_true')
    args = parser.parse_args()
##########################

import pickle, sys
from math import sqrt, log10, floor
sys.path.append('/afs/cern.ch/user/g/gdujany/LHCb/LFV/')
from tau2PhiMuAnalysis import roundPair

 
class Efficiency:
    '''
    Class to store and evaluate information about a single efficiency (e1 or e2)
    '''
    def __init__(self, eff=None, s_eff=None, N_gen=None, N_sel=None, s2_N_gen=None, s2_N_sel=None, cov_N_gen_sel=None):
        
        self.eff = 0
        self.s_eff = 0
        
        if N_gen != None and N_sel != None:
            self.eff = N_sel/N_gen
            if s2_N_gen != None and s2_N_sel != None and cov_N_gen_sel != None:
                self.s_eff = N_sel/N_gen * sqrt( s2_N_sel/N_sel**2 + s2_N_gen/N_gen**2 - 2*cov_N_gen_sel/(N_sel*N_gen) )
            else: self.s_eff = sqrt( self.eff * (1-self.eff) / N_gen )

        if eff != None: self.eff = eff
        if s_eff != None: self.s_eff = s_eff
  
    def s_rel_eff(self):
        return self.s_eff/self.eff 

    def __str__(self):
        return 'efficiency = '+str(self.eff)+'\n'+\
            'error = '+str(self.s_eff)+'\n'+\
            'relative error = '+str(self.s_rel_eff())

    def saveToFile(self, fileName = "efficiency.txt"):
        pickle.dump(self, open( fileName, "wb" ))
        
    def loadFromFile(self,fileName = "efficiency.txt"):
        return pickle.load( open( fileName, "rb" ) )

    def __str__(self):
        val, err = roundPair(self.eff, self.s_eff)
        return val+' +- '+err

    #def __r

    def __add__(self, other):
        res = Efficiency()
        res.eff = self.eff + other.eff
        res.s_eff = sqrt(self.s_eff**2 + other.s_eff**2)
        return res

    def __sub__(self, other):
        res = Efficiency()
        res.eff = self.eff - other.eff
        res.s_eff = sqrt(self.s_eff**2 + other.s_eff**2)
        return res

    def __mul__(self, other):
        res = Efficiency()
        res.eff = self.eff * other.eff
        res.s_eff = res.eff * sqrt( (self.s_eff/self.eff)**2 + (other.s_eff/other.eff)**2)
        return res


if __name__ == '__main__':
     
    import os

    norm_str = ' -n' if args.D2PhiPi else ''
     

    if args.all:
        os.system('./selectionEfficiency.py -a'+norm_str)
        os.system('./triggerEfficiencies.py -a'+norm_str)


    gen_effs = dict(
        tau2PhiMu = Efficiency(eff=0.1),
        D2PhiPi = Efficiency(eff=0.1),
        )

    file_label = 'D2PhiPi' if args.D2PhiPi else 'tau2PhiMu'
    gen_eff = gen_effs[file_label]
    sel_eff = pickle.load(open('pickles/selection_eff_'+file_label+'.pkl','rb'))
    trig_eff = pickle.load(open('pickles/trigger_effs_'+file_label+'.pkl','rb'))['trigger']

    total_eff = sel_eff * trig_eff  #gen_eff * sel_eff * trig_eff
    
    def printEff(name, eff):
        val, err = roundPair(eff.eff, eff.s_eff)
        print name+' efficiency '+ file_label + ' = '+val+' +- '+err

    printEff('Generator', gen_eff)
    printEff('Selection', sel_eff)
    printEff('Trigger', trig_eff)
    printEff('Total', total_eff)
     
     
     

     
         
