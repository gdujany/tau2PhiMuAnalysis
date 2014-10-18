from Gaudi.Configuration import *

eos_root = '/afs/cern.ch/user/g/gdujany/eos'

import os
if not os.listdir(eos_root):
    raise OSError('EOS not mounted, please type:\n eosmount '+eos_root)

import sys, os, re
# to be able to import jobSetup using gaudirun
sys.path.append(os.getcwd())
from jobSetup import *

str_LFNs = open(dataSample.input_file).read()

LF_dir = re.compile(r'LFN:(/lhcb/MC/2012/ALLSTREAMS.DST/.*/0000/).*dst')
directory=re.search(LF_dir,str_LFNs).group(1)

eos_dir = '/lhcb/grid/prod'

files = [eos_dir+directory+file for file in os.listdir(eos_root+eos_dir+directory)]

from GaudiConf import IOHelper
IOHelper().inputFiles(['PFN:root://eoslhcb.cern.ch//eos'+file for file in files], clear=True)

