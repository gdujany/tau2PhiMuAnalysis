#!/usr/bin/env python

##########################
###   Options parser   ###
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description = 'sPlots.py')
    parser.add_argument('-d','--dataset',help='make also dataset',action='store_true')
    args = parser.parse_args()
########################## 

import ROOT as r
import sys
sys.path.append('/afs/cern.ch/user/g/gdujany/pyUtils')
from MultiPlot import MultiPlot

r.gROOT.ProcessLine('.L /afs/cern.ch/user/g/gdujany/LHCb/LFV/tau2PhiMuAnalysis/MVA/exploreVariables/DasSignal/MySPlot.cxx+')
r.gSystem.Load('MySPlot_cxx')





def makeRooDataset(input_tree, vars, helpingVars):
    '''
    Return RooDataset, take as input the file with nTuple and a dictionary
    with {var_name : (x_min, x_max)}
    and a tuple (helpingVars) with variables without range (take all)
    '''
   
    rooVars = {}
    for var, spread in vars.items():
        rooVars[var] = r.RooRealVar(var, var, spread[0], spread[1])

    for var in helpingVars:
        rooVars[var] = r.RooRealVar(var, var, 0)
        rooVars[var].setConstant(False)

    def chunks(l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]
    vars_slices = chunks(rooVars.values(), 6)
    dataArgSet = r.RooArgSet(*vars_slices[0])
    for var_slice in vars_slices[1:]:
        dataArgSet.add(r.RooArgSet(*var_slice))

    
    print 'making dataSet'
    dataSet = r.RooDataSet("taus","taus RooDataSet", input_tree, dataArgSet)
    return dataSet


def addExpressions(dataSet):
    rooVars = {}
    for var, spread in vars.items():
        rooVars[var] = r.RooRealVar(var, var, spread[0], spread[1])
    for var in helpingVars:
        rooVars[var] = r.RooRealVar(var, var, 0)
        rooVars[var].setConstant(False)

    Pi_M = r.RooRealVar('Pi_M', 'Pi_M', 139.57018)

    argList = r.RooArgList(rooVars['Phi_M'], Pi_M, rooVars['Phi_PX'], rooVars['Mu_PX'], rooVars['Phi_PY'], rooVars['Mu_PY'])
    argList.add(r.RooArgList(rooVars['Phi_PZ'], rooVars['Mu_PZ'], rooVars['Phi_PE'], rooVars['Mu_P']))
        
    PhiPi_M = r.RooFormulaVar('PhiPi_M', 'sqrt(@0*@0 + @1*@1 -2*(@2*@3+@4*@5+@6*@7)+2*@8*sqrt(@1*@1+@9*@9))',argList)
    
    dataSet.addColumn(PhiPi_M)
    return dataSet

def addModel(w):
    x = w.factory(x_var+'['+str(x_var_range[0])+','+str(x_var_range[1])+']')
    x.setUnit('MeV')
    
    numBins = 100
    x.setBins(numBins)

    # D peak
    w.factory('''RooCBShape::Dpeak({0},
        mean_D[1860,1830,1890],
        sigma_D[7,0,15],
        alpha_D[0.5,0,5],
        n_D[3]
        )'''.format(x_var))
    
    # Background
    w.factory('''RooChebychev::background('''+x_var+''',
        {a1[-0.5,-1,1],
        a2[-0.1,-1,1],
        a3[0.05,-1,1]}
        )''')

    # Together
    w.factory('''SUM::modelPdf(
    n_Dpeak[100000, 0, 100000000] * Dpeak,
    n_bkg[10000000, 0, 10000000000] * background
    )''')

    w.pdf('modelPdf').graphVizTree("modelPDF.dot")

    return w



def makeSPlots(w, outFile_name='test.root', input_tree=None):

    data = w.data('data')
    modelPdf = w.pdf('modelPdf')
    x = w.var(x_var)
    print '\n'
    x.Print()
    print '\n'
    fit_region = x.setRange('fit_region',x_var_range[0],x_var_range[1])
    result = modelPdf.fitTo(data, r.RooFit.Save(), r.RooFit.Range('fit_region'), r.RooFit.NumCPU(2), r.RooFit.SumW2Error(True))

   
    c = drawFitPlot(w, 'plotFit.pdf')
    c1=c.Clone('First fit')
   

    # Fix parameters other then yields
    params_names = ['mean_D', 'sigma_D', 'alpha_D', 'n_D', 'a1', 'a2', 'a3']
    for param in params_names:
        w.var(param).setConstant()    

    #print '\nNew Fit\n'
    #result = modelPdf.fitTo(data, r.RooFit.Save(), r.RooFit.Range('fit_region'), r.RooFit.NumCPU(2), r.RooFit.SumW2Error(True))#,r.RooFit.Minos(True))
    #drawFitPlot(w, 'plot2Fit.pdf')

    n_Dpeak = w.var('n_Dpeak')
    n_bkg = w.var('n_bkg')

    print 'before sWeights'
    print 'n_Dpeak = ', n_Dpeak.getVal()
    print 'n_bkg = ', n_bkg.getVal()
    
    #sData = r.RooStats.SPlot('sData', 'An sPlot', data, modelPdf, r.RooArgList(n_Dpeak, n_bkg))
    sData = r.MySPlot('sData', 'An sPlot', data, modelPdf, r.RooArgList(n_Dpeak, n_bkg),'fit_region')

    print 'check sWeights'
    print 'n_Dpeak = ', n_Dpeak.getVal(),'=',sData.GetYieldFromSWeight('n_Dpeak')
    print 'n_bkg = ', n_bkg.getVal(),'=',sData.GetYieldFromSWeight('n_bkg')

    for i in xrange(10):
        print sData.GetSWeight(i, 'n_Dpeak'),'+',sData.GetSWeight(i, 'n_bkg'),'=',sData.GetSumOfEventSWeight(i)

    c = drawFitPlot(w, 'plotFit2.pdf')
    c2=c.Clone('Second fit')
    

    # print 'Import dataset with sWeights'
    getattr(w, 'import')(data, r.RooFit.Rename('dataWithSWeights'))

    outFile = r.TFile(outFile_name,'recreate')
    outFile.WriteTObject(c1)
    outFile.WriteTObject(c2)
    if input_tree != None:
        makeTree(sData, input_tree)
    outFile.Write()
    outFile.Close()
    
    return sData, c1, c2

def drawFitPlot(w, outputFile_name):

    # Mass plot
    frame = w.var(x_var).frame(r.RooFit.Title(' Combined mass KK#pi '))
    #data = w.data('dataWithSWeights')
    data = w.data('data')
    modelPdf = w.pdf('modelPdf')
    data.plotOn(frame)
    norm = data.sumEntries()
    modelPdf.plotOn(frame,r.RooFit.Components('Dpeak'), r.RooFit.LineColor(r.kRed), r.RooFit.LineStyle(2), r.RooFit.LineWidth(1),r.RooFit.NormRange('fit_region'))#,r.RooFit.Normalization(norm,r.RooAbsReal.NumEvent))
    modelPdf.plotOn(frame,r.RooFit.Components('background'), r.RooFit.LineColor(r.kBlack), r.RooFit.LineStyle(2), r.RooFit.LineWidth(1),r.RooFit.NormRange('fit_region'))#,r.RooFit.Normalization(norm,r.RooAbsReal.NumEvent))
    modelPdf.plotOn(frame, r.RooFit.LineWidth(2),r.RooFit.NormRange('fit_region'))#,r.RooFit.Normalization(norm,r.RooAbsReal.NumEvent))
    # Legends
    parameters_on_legend = r.RooArgSet(w.var('n_bkg'), w.var('n_Dpeak'), w.var('mean_D'), w.var('sigma_D'), w.var('alpha_D'))
    modelPdf.paramOn(frame, r.RooFit.Layout(0.1,0.44,0.5),r.RooFit.Parameters(parameters_on_legend))#(0.1,0.44,0.9))
    chi2 = round(frame.chiSquare(),2)
    leg = r.TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c = r.TCanvas('c','c')
    frame.Draw()
    c.Print(outputFile_name)
    return c
    

def makeTree(sData, input_tree):

    print 'In makeTree()'
    dataSet = sData.GetSDataSet()
    sw_argset = dataSet.get()
    mass_var = sw_argset.find(x_var)
    tau_mass_inDataset = sw_argset.find('Tau_M') # useful for aligning tree with dataset
    
    # output branches
    from array import array
    tau_mass = array('d',[0])
    n_Dpeak_sw = array('d',[0])
    n_bkg_sw = array('d',[0])
    sum_sw = array('d',[0])


    #outFile = r.TFile(outFile_name,'recreate')
    outTree = r.TTree('sWeightsTree', 'sWeightsTree')
    outTree.Branch(x_var, tau_mass, x_var+'/D')
    outTree.Branch('n_Dpeak_sw', n_Dpeak_sw, 'n_Dpeak_sw/D')
    outTree.Branch('n_bkg_sw', n_bkg_sw, 'n_bkg_sw/D')
    outTree.Branch('sum_sw', sum_sw, 'sum_sw/D')

    evtMax = -1
    cont = 0
    for entry in input_tree:
        if cont == evtMax: break
        dataSet.get(cont)
        tau_mass[0] =  mass_var.getVal()
        tau_mass_inTree = getattr(entry,'Tau_M')
        if abs(tau_mass_inDataset.getVal() - tau_mass_inTree) > 0.1:
            n_Dpeak_sw[0] = 0
            n_bkg_sw[0] = 0
            sum_sw[0] = 0
        else:
            n_Dpeak_sw[0] = sData.GetSWeight(cont, 'n_Dpeak')
            n_bkg_sw[0] = sData.GetSWeight(cont,'n_bkg') 
            sum_sw[0] = sData.GetSumOfEventSWeight(cont)
            cont += 1

        outTree.Fill()

    outTree.Write()

    #outFile.Write()
    #outFile.Close()

def dataSet2Tree(dataSet, outFile_name):
    
    print 'Making new tree'
    varsArgSet = dataSet.get()
    itVars = varsArgSet.createIterator()
    vars = []
    while(True):
        try:
            vars.append(itVars.GetName())
            itVars.Next()
        except ReferenceError: break

    vars = ['PhiPi_M', 'Tau_DTF_Tau_M', 'Tau_M']
    
    print vars

    outFile = r.TFile(outFile_name,'recreate')
    outTree = r.TTree('tree', 'tree')

    from array import array
    rooVars = {}
    pointers ={}
    for var in vars:
        exec var +'= array("d",[0])'
        exec "outTree.Branch('"+var+"', "+var+", '"+x_var+"/D')"
        rooVars[var] = varsArgSet.find(var)

    cont = -1
    while(True):
        cont += 1
        try:
            dataSet.get(cont)
            for var in vars:
                exec var+'[0] = rooVars[var].getVal()'
        except ReferenceError: break


    nEntries = dataSet.numEntries()
    nEntries = 100
    print nEntries
    for cont in xrange(nEntries):
        dataSet.get(cont)
        for var in vars:
            exec var+'[0] = rooVars[var].getVal()'
        outTree.Fill()    
        

    #outFile.Write()
    #outFile.Close()
            
   

if __name__ == '__main__':

    r.gROOT.SetBatch()

    dataFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012.root'
    dataSet_name = 'rooDataSet.root'
    # dataFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012_triggerNotApplied.root'
    # dataSet_name = 'rooDataSet_triggerNotApplied.root'
    outFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012_sWeights2.root'
    
    inputFile = r.TFile(dataFile_name)
    tree = inputFile.Get('DecayTreeTuple/DecayTree')

    if args.dataset:
        x_var = 'Tau_M'
        x_var_range = (1700, 1900) #(1600, 1950),
        
        vars = dict(
            Tau_M = x_var_range,
            Tau_DTF_Tau_M = x_var_range,
            )

        helpingVars = ['{}_{}'.format(i,j) for i in ('Phi', 'Mu') for j in ('PX', 'PY', 'PZ')] + ['Phi_M', 'Phi_PE', 'Mu_P']

        dataSet = makeRooDataset(tree, vars, helpingVars)
        cuts_str = ''
        data = dataSet.reduce( r.RooFit.Cut(cuts_str) )
        data = addExpressions(data)
        data.SaveAs('datasetDelendo.root')

    #############################################################
    dataFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012_treeForSPlot.root'
    inputFile = r.TFile(dataFile_name)
    tree = inputFile.Get('treeForSPlot')
    
    x_var = 'PhiPi_M'
    x_var_range = (1720,1900)#(1720, 1900) #(1600, 1950)
    vars = dict(
        PhiPi_M = x_var_range,
        Tau_M = (1700,1900),
        Tau_DTF_Tau_M = (1700,1900),
        )

    helpingVars = []#['Tau_M']
    dataSet = makeRooDataset(tree, vars, helpingVars)
    dataSet.SaveAs('datasetDelendo2.root')
    #############################################################
        
       
    data = r.TFile('datasetDelendo2.root').Get('taus')

    x_var = 'PhiPi_M'
    x_var_range = (1720,1900)#(1720, 1900) #(1600, 1950)

    #cuts_x_var = x_var+'>'+str(x_var_range[0])+' & '+x_var+'<'+str(x_var_range[1])
    #data = data.reduce( r.RooFit.Cut(cuts_x_var) )
    #x_var = 'Tau_M'
    #x_var_range = (1700, 1900)
    
    #assert(1==2)
    #dataSet2Tree(data, '/tmp/gdujany/testTree.root')
           

    w = r.RooWorkspace('w')
    w = addModel(w)       
    getattr(w,'import')(data, r.RooFit.Rename('data'))

    #w.var(x_var).setRange('newRange',*x_var_range)
    
    sData, c1, c2 = makeSPlots(w, outFile_name, tree)
#    sData = makeSPlots(w, 'fitPlot.pdf')
    
    #w.SaveAs('w.root')
    #w = r.TFile('w.root').Get('w')

    # print 'About to make tree'
    # makeTree(sData, outFile_name, tree)

    
