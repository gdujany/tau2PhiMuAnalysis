#!/usr/bin/python

# sample = 'data2012'
# sample = 'tau2PhiMuFromPDs'

from ROOT import TFile, TH1D
from ROOT import THStack, TLegend, TCanvas, TF1
from ROOT import gROOT, gStyle
import ROOT
from array import array

m_pi = 139.57018
gROOT.SetBatch()

def makeHistos():

    from ROOT import TTree, TLorentzVector

    tauRange = (1600, 1950) if sample == 'data2012' else (1740, 1810)
    
    histos = {}
    #histos['m_KK1'] = TH1D('m_KK1','Combinatorial mass;m_{KK} [MeV];',100,950,1800)
    histos['m_KK'] = TH1D('m_KK','Combinatorial mass;m_{KK} [MeV];',100,1008,1032)
    histos['m_Phi'] = TH1D('m_Phi','Mass constrined vertex;m_{#Phi} [MeV];',100,1008,1032)
    histos['m_DTF_Phi'] = TH1D('m_DTF_Phi','Mass Decay Tree Fitter m_{#Phi} constrained;m_{#Phi} [MeV];',100,1008,1030)
    histos['m_DTFTau_Phi'] = TH1D('m_DTFTau_Phi','Mass Decay Tree Fitter m_{#tau} constrained;m_{#Phi} [MeV];',100,1008,1030)

 
    inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/'+sample+'.root'
    inFile = TFile(inFile_name)
    tree = inFile.Get('DecayTreeTuple/DecayTree')

    tree.SetBranchStatus("*",0)
    branches = ['{0}_{1}'.format(i,j) for i in ('Tau', 'Phi', 'KPlus', 'KMinus', 'Mu') for j in ('M', 'PE', 'PX', 'PY', 'PZ')]
    branches += ['Tau_DTF_{0}_{1}'.format(i, j) for i in ('Tau', 'Phi', 'KPlus', 'KMinus', 'Mu') for j in ('M', 'E', 'PX', 'PY', 'PZ')]
    branches.extend(['Tau_DTFTau_Phi_M', 'Tau_DTF_PROB', 'Tau_DTFTau_PROB', 'Mu_ProbNNmu', 'Mu_ProbNNpi'])
    for var in branches:
        tree.SetBranchStatus(var,1)
        exec var+' = array("d",[0])'
        exec "tree.SetBranchAddress( '"+var+"', "+var+" )"

    nEvents = tree.GetEntries()
    #nEvents = 10000
    for cont, entrie in enumerate(tree):
        if cont == nEvents: break
        if cont % 20000 == 0:
            print 'processing entrie ', cont, ' / ', nEvents,' : ', (cont*100)/nEvents,'%'

        # TLorenzVectors
        tau = TLorentzVector()
        tau.SetXYZT(Tau_PX[0], Tau_PY[0], Tau_PZ[0], Tau_PE[0])
        phi = TLorentzVector()
        phi.SetXYZT(Phi_PX[0], Phi_PY[0], Phi_PZ[0], Phi_PE[0])
        mu = TLorentzVector()
        mu.SetXYZT(Mu_PX[0], Mu_PY[0], Mu_PZ[0], Mu_PE[0])
        Kp = TLorentzVector()
        Kp.SetXYZT(KPlus_PX[0], KPlus_PY[0], KPlus_PZ[0], KPlus_PE[0])
        Km = TLorentzVector()
        Km.SetXYZT(KMinus_PX[0], KMinus_PY[0], KMinus_PZ[0], KMinus_PE[0])

        pi_mu = TLorentzVector()
        pi_mu.SetXYZM(Mu_PX[0], Mu_PY[0], Mu_PZ[0], m_pi)
        pi_Kp = TLorentzVector()
        pi_Kp.SetXYZM(KPlus_PX[0], KPlus_PY[0], KPlus_PZ[0], m_pi)
        pi_Km = TLorentzVector()
        pi_Km.SetXYZM(KMinus_PX[0], KMinus_PY[0], KMinus_PZ[0], m_pi)

        DTF_tau = TLorentzVector()
        DTF_tau.SetXYZT(Tau_DTF_Tau_PX[0], Tau_DTF_Tau_PY[0], Tau_DTF_Tau_PZ[0], Tau_DTF_Tau_E[0])
        DTF_phi = TLorentzVector()
        DTF_phi.SetXYZT(Tau_DTF_Phi_PX[0], Tau_DTF_Phi_PY[0], Tau_DTF_Phi_PZ[0], Tau_DTF_Phi_E[0])
        DTF_mu = TLorentzVector()
        DTF_mu.SetXYZT(Tau_DTF_Mu_PX[0], Tau_DTF_Mu_PY[0], Tau_DTF_Mu_PZ[0], Tau_DTF_Mu_E[0])
        DTF_Kp = TLorentzVector()
        DTF_Kp.SetXYZT(Tau_DTF_KPlus_PX[0], Tau_DTF_KPlus_PY[0], Tau_DTF_KPlus_PZ[0], Tau_DTF_KPlus_E[0])
        DTF_Km = TLorentzVector()
        DTF_Km.SetXYZT(Tau_DTF_KMinus_PX[0], Tau_DTF_KMinus_PY[0], Tau_DTF_KMinus_PZ[0], Tau_DTF_KMinus_E[0])


        # Fill Histos
        #histos['m_KK1'].Fill((Kp+Km).M())
        histos['m_KK'].Fill((Kp+Km).M())
        histos['m_Phi'].Fill(phi.M())
        histos['m_DTF_Phi'].Fill(DTF_phi.M())
        histos['m_DTFTau_Phi'].Fill(Tau_DTFTau_Phi_M[0])

        histos['m_KKMu'].Fill((Kp+Km+mu).M())
        histos['m_PhiMu'].Fill((phi+mu).M())
        histos['m_Tau'].Fill(tau.M())
        histos['m_DTF_Tau'].Fill(DTF_tau.M())


        histos['m_KPi'].Fill((Kp+pi_Km).M())
        histos['m_PiK'].Fill((pi_Kp+Km).M())
        histos['m_KPi_fromMu'].Fill((Kp+pi_mu).M()) # K+ and pi- misID as mu-
        histos['m_KKPi'].Fill((Kp+Km+pi_mu).M())
        histos['m_PhiPi'].Fill((phi+pi_mu).M())
        histos['m_KPiPi_SS'].Fill((Kp+pi_Km+pi_mu).M())
        histos['m_KPiPi_OS'].Fill((Km+pi_Kp+pi_mu).M())
        histos['m_PiPi'].Fill((pi_Kp+pi_mu).M())

        if Tau_M[0]>1840 and Tau_M[0]< 1870:
            histos['m_KKPi_D'].Fill((Kp+Km+pi_mu).M())
        else:
            histos['m_KPi_fromMu_noD'].Fill((Kp+pi_mu).M()) # K+ and pi- misID as mu-
            histos['m_KPiPi_SS_noD'].Fill((Kp+pi_Km+pi_mu).M())
            histos['m_KPiPi_OS_noD'].Fill((Km+pi_Kp+pi_mu).M())
        

        histos['Tau_DTF_PROB'].Fill(Tau_DTF_PROB[0])
        histos['Tau_DTFTau_PROB'].Fill(Tau_DTFTau_PROB[0])

        histos['Mu_ProbNNmu'].Fill(Mu_ProbNNmu[0])
        histos['Mu_ProbNNpi'].Fill(Mu_ProbNNpi[0])

        if Tau_M[0] > 1747 and Tau_M[0] < 1807:
            histos['Tau_DTF_PROB_SR'].Fill(Tau_DTF_PROB[0])
            histos['Tau_DTFTau_PROB_SR'].Fill(Tau_DTFTau_PROB[0])
            histos['m_PiPi_noD'].Fill((pi_Kp+pi_mu).M())


    outFile = TFile('histos_'+sample+'.root','RECREATE')
    for histo in histos.values():
        histo.Write()
    outFile.Close()

colori=[ROOT.kBlue, ROOT.kRed, ROOT.kGreen+2, ROOT.kMagenta+1, ROOT.kOrange-3, ROOT.kYellow, ROOT.kCyan]

from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList, RooDataSet, RooArgSet, RooChebychev, RooAddPdf, RooPolynomial, RooExponential

def makeRooDataset():
    inFile_name = '/afs/cern.ch/user/g/gdujany/work/LHCb/LFV/store/data2012.root'
    inFile = TFile(inFile_name)
    tree = inFile.Get('DecayTreeTuple/DecayTree')
   
    Phi_M = RooRealVar('Phi_M', 'Phi_M', 1008,1032)
    Tau_DTF_Phi_M = RooRealVar('Tau_DTF_Phi_M', 'Tau_DTF_Phi_M', 1008,1032)

    dataArgSet = RooArgSet(Phi_M, Tau_DTF_Phi_M)
    print 'Making a dataset from file', inFile_name
    dataSet = RooDataSet("phi_mass_dataset","phi_mass_dataset", tree, dataArgSet)
    dataSet.SaveAs('rooDataSet.root')
    return dataSet



    
def makeFit():

    inFile = TFile('rooDataSet.root')
    dataSet = inFile.Get('phi_mass_dataset')
    
    # Fit m_DTF_Phi
    gStyle.SetOptFit(1111)
    #histo = histos['m_DTF_Phi']
    x_var = 'Phi_M'
    x = RooRealVar(x_var, 'm_{#Phi}', 1008,1032, 'MeV')
    #x = RooRealVar(x_var, 'm_{#Phi}', 1010,1027, 'MeV')
    x.setBins(200)
    #ral = RooArgList(x)
    #dh = RooDataHist ("dh","dh",ral,RooFit.Import(histo))
    
    
    # Signal
    mean = RooRealVar("mean","mean",1020,1010,1025) 
    sigma = RooRealVar("sigma","sigma",3,0.1,10)
    alpha = RooRealVar('alpha', 'alpha', 1, 0.1, 10)
    param_n = RooRealVar('param_n','param_n', 2, 0.1, 10)
    #pdf = ROOT.RooGaussian("gauss","gauss",x,mean,sigma)
    signal = ROOT.RooBreitWigner('BW','BW',x,mean, sigma)
    #signal = ROOT.RooVoigtian('voit','voit', x, mean, sigma)
    #signal = ROOT.RooCBShape('CB','CB', x, mean, sigma, alpha, param_n)

    # Background
    a1 = RooRealVar('a0','a0',0.,-0.0000001,0.0000001) #,0.5,0.,1.)
    #a2 = RooRealVar('a1','a1',0.1,-1.,1.) #-0.2,0.,1.)
    #a3 = RooRealVar('a2','a2',-0.1,1.,-1.)
    esp = RooRealVar('esp','esp',0.,-0.5,0.5) #,0.5,0.,1.)
    #background = RooChebychev('background','Background',x,RooArgList(a1))
    #background = RooPolynomial('background','Background',x,RooArgList(a1))
    background = RooExponential('background','Background',x,esp)
   
    # Toghether
    pdf_list = RooArgList(signal, background)   
    ratio_SB = RooRealVar("ratio_SB","ratio_SB",0.7, 0, 1)
    ratio_list = RooArgList(ratio_SB)
    modelPdf = RooAddPdf('ModelPdf', 'ModelPdf', pdf_list, ratio_list)

    # Fit
    fit_region = x.setRange("fit_region",1010,1027)
    result = modelPdf.fitTo(dataSet, RooFit.Save(), RooFit.Range("fit_region"))

    # Frame
    frame = x.frame(RooFit.Title(' #Phi mass '))
    dataSet.plotOn(frame)
    modelPdf.paramOn(frame, RooFit.Layout(0.1,0.44,0.9))
    signal_set = RooArgSet(signal)
    modelPdf.plotOn(frame,RooFit.Components(signal_set), RooFit.LineColor(ROOT.kGreen+2), RooFit.LineStyle(2), RooFit.LineWidth(1))
    background_set = RooArgSet(background)
    modelPdf.plotOn(frame,RooFit.Components(background_set), RooFit.LineColor(ROOT.kBlack), RooFit.LineStyle(2), RooFit.LineWidth(1))
    modelPdf.plotOn(frame, RooFit.LineWidth(2))
    
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)

    c1 = TCanvas('c1', 'c1')
    frame.Draw()
    c1.Update()  
    c1.Print('plotFit.pdf')


   #  # Traditional Root way to fit
#     func = TF1('myBW', '[0]*TMath::BreitWigner(x,[1],[2])', 1010,1025)
# #    func = TF1('myfunc', '[0]*TMath::Gaus(x,[1],[2])', 1010,1025)
#     func = TF1('myfunc', '[0]*TMath::Voigt(x-[1],[2],[3])', 1010,1025)
#     func.SetParameter(0,1048)
#     func.SetParName(0,'Norm')
#     func.SetParameter(1,1020)
#     func.SetParName(1,'mean')
#     func.SetParameter(2,4)
#     func.SetParName(2,'gamma')

#     func = TF1('myfunc', '[0]*TMath::Voigt(x-[1],[2],[3])', 1010,1025)
#     func.SetParameter(0,1048)
#     func.SetParName(0,'Norm')
#     func.SetParameter(1,1020)
#     func.SetParName(1,'mean')
#     func.SetParameter(2,4)
#     func.SetParName(2,'sigma')
#     func.SetParameter(3,4)
#     func.SetParName(2,'gamma')
    
#     histo.Fit('myfunc')
#     #histo.Fit('gaus')
#     histo.Draw()
#     c1.Update()  
#     c1.Print(outFile_name)
 

  #  c1.Print(outFile_name+']')






if __name__ == '__main__':
    
    #sample = 'data2012'
    #sample = 'tau2PhiMuFromPDs'
    
    #makeHistos()
    #makeRooDataset()
    makeFit()
   
