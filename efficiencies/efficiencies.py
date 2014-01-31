from __future__ import division
import pickle
from math import sqrt, log10, floor

 
class Efficiency:
    '''
    Class to store and evaluate information about a single efficiency (e1 or e2)
    '''
    def __init__(self, eff=None, s_eff=None, N_gen=None, N_sel=None, s2_N_gen=None, s2_N_sel=None, cov_N_gen_sel=None):
        if((eff==None or s_eff==None) and (N_gen==None or N_sel==None) and (s2_N_gen==None or s2_N_sel==None or cov_N_gen_sel==None)):
            self.eff = 0
            self.s_eff = 1
        elif(eff==None and s_eff==None and (s2_N_gen==None or s2_N_sel==None or cov_N_gen_sel==None)):
            self.eff = N_sel/N_gen
            self.s_eff = sqrt( self.eff * (1-self.eff) / N_gen )
        elif(eff==None or s_eff==None):
            self.eff = N_sel/N_gen
            if N_sel != 0:
                self.s_eff = N_sel/N_gen * sqrt( s2_N_sel/N_sel**2 + s2_N_gen/N_gen**2 - 2*cov_N_gen_sel/(N_sel*N_gen) )
            else:
                self.s_eff = 0
        else:
            self.eff = eff
            self.s_eff = s_eff
  
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
 
