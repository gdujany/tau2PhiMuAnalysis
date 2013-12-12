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

    histos['m_KKMu'] = TH1D('m_KKMu','Combinatorial mass;m_{KK#mu} [MeV];',100,*tauRange)
    histos['m_PhiMu'] = TH1D('m_PhiMu','Combinatorial mass;m_{#Phi#mu} [MeV];',100,*tauRange)
    histos['m_Tau'] = TH1D('m_Tau','Mass constrined vertex;m_{#tau} [MeV];',100,*tauRange)
    histos['m_DTF_Tau'] = TH1D('m_DTF_Tau','Mass Decay Tree Fitter m_{#Phi} constrained;m_{#tau} [MeV];',100,*tauRange)


    histos['m_KPi'] = TH1D('m_KPi','Combinatorial mass;m_{K^{+}#pi^{-}} [MeV];',100,630,860)
    histos['m_PiK'] = TH1D('m_PiK','Combinatorial mass;m_{#pi^{+}K^{-}} [MeV];',100,630,860)
    histos['m_KPi_fromMu'] = TH1D('m_KPi_fromMu','Combinatorial mass kaon and pion misID as muon;m_{K#pi} [MeV];',100,850,1450)
    histos['m_KPi_fromMu_noD'] = TH1D('m_KPi_fromMu_noD','Combinatorial mass kaon and pion misID as muon not in the D- peak;m_{K#pi} [MeV];',100,850,1450)
    histos['m_KKPi'] = TH1D('m_KKPi','Combinatorial mass;m_{KK#pi} [MeV];',100,1600,2000)
    histos['m_KKPi_D'] = TH1D('m_KKPi_D','Combinatorial mass, in peak KK#mu;m_{KK#pi} [MeV];',100,1600,2000)
    histos['m_PhiPi'] = TH1D('m_PhiPi','Combinatorial mass;m_{#Phi#pi} [MeV];',100,1600,2000)
    histos['m_KPiPi_OS'] = TH1D('m_KPiPi_OS','Combinatorial mass;m_{K^{-}#pi^{+}#pi^{-}} [MeV];',100,1050,1950)
    histos['m_KPiPi_OS_noD'] = TH1D('m_KPiPi_OS_noD','Combinatorial mass not in D- region;m_{K^{-}#pi^{+}#pi^{-}} [MeV];',100,1050,1950)
    histos['m_KPiPi_SS'] = TH1D('m_KPiPi_SS','Combinatorial mass;m_{K^{+}#pi^{-}#pi^{-}} [MeV];',100,1050,1950)
    histos['m_KPiPi_SS_noD'] = TH1D('m_KPiPi_SS_noD','Combinatorial mass not in D- region;m_{K^{+}#pi^{-}#pi^{-}} [MeV];',100,1050,1950)
    histos['m_PiPi'] = TH1D('m_PiPi','Combinatorial mass #pi^{+} from K, #pi^{-} from #mu;m_{#pi^{+}#pi^{-}} [MeV];',100,300,1350)
    histos['m_PiPi_noD'] = TH1D('m_PiPi_noD','Combinatorial mass #pi^{+} from K, #pi^{-} from #mu, not in D peak;m_{#pi^{+}#pi^{-}} [MeV];',100,300,1350)
    

    histos['Tau_DTF_PROB'] =  TH1D('Tau_DTF_PROB','Probability DecayTreeFitter m_{#Phi} constrained;probability;',100,0,1)
    histos['Tau_DTFTau_PROB'] =  TH1D('Tau_DTFTau_PROB','Probability  DecayTreeFitter m_{#tau} constrained;probability m_{#tau} constrained;',100,0,1)
    histos['Tau_DTF_PROB_SR'] =  TH1D('Tau_DTF_PROB_SR','Probability DecayTreeFitter m_{#Phi} constrained;probability;',100,0,1)
    histos['Tau_DTFTau_PROB_SR'] = TH1D('Tau_DTFTau_PROB_SR','Probability  DecayTreeFitter m_{#tau} constrained;probability m_{#tau} constrained;',100,0,1)

    histos['Mu_ProbNNmu'] = TH1D('Mu_ProbNNmu','Probability to be a #mu;probability to be a #mu;',100,0,1) 
    histos['Mu_ProbNNpi'] = TH1D('Mu_ProbNNpi','Probability to be a #pi;probability to be a #pi;',100,0,1) 


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

def setPlotAttributes(graph, color = ROOT.kBlue, markerStyle = 20):
    graph.SetMarkerStyle(markerStyle)
    graph.SetMarkerColor(color)
    graph.SetLineColor(color)

def drawMultiPlot(outFile_name='plots.pdf',title='', plot_name='',logy=False, squarePad=False, **h_dict):
    hs = THStack('hs',title)
    leg = TLegend(.80, 0.83, .97, .96,"")
    if squarePad:
        c2 = TCanvas('c2', 'c2',700,700)
    else:
        c2 = TCanvas('c2', 'c2')
    
    for cont, (label, histo) in enumerate(h_dict.items()):
        setPlotAttributes(histo, colori[cont])
        hs.Add(histo.Clone())
        leg.AddEntry(histo,label,'l')

    if logy: c2.SetLogy()
    hs.Draw('nostack')
    leg.Draw("same")
    leg.SetFillColor(0)
    c2.Update()  
    c2.Print(outFile_name)
    c2.Print('plots/'+sample+'/'+plot_name+'.pdf')


def makePlots():
    
    histoFile = TFile('histos_'+sample+'.root')
    histos = {}
    for key in histoFile.GetListOfKeys():
        histos[key.GetName()] = histoFile.Get(key.GetName())

    outFile_name = 'plots_'+sample+'.pdf'
    c1 = TCanvas('c1', 'c1')
    c1.Print(outFile_name+'[')

    
    # Plot comparing m_Phi various method
    drawMultiPlot(outFile_name,';m_{KK [MeV]};', 'm_phi',
                  **{'m_{KK}' : histos['m_KK'],
                   'm_{#Phi}' : histos['m_Phi'],
                   'm_{#Phi} DTF #tau' : histos['m_DTFTau_Phi'],
                   'm_{#Phi} DTF #Phi' : histos['m_DTF_Phi']})

        

    # Plot comparing m_Tau various method
    drawMultiPlot(outFile_name, ';m_{KK#mu [MeV]};', 'm_tau',
                  **{'m_{KK#mu}' : histos['m_KKMu'],
                     'm_{#Phi#mu}' : histos['m_PhiMu'],
                     'm_{#tau} DTF #Phi' : histos['m_DTF_Tau']})
    
 
    # m_KPi and m_PiK
    drawMultiPlot(outFile_name, ';m_{K#pi} [MeV];', 'm_KPi',
                  **{'m_{K#pi}' : histos['m_KPi'],
                     'm_{#piK}' : histos['m_PiK']})
    
   
    # m_KKpi and m_PhiPi
    drawMultiPlot(outFile_name, ';m_{KK#pi} [MeV];', 'm_KKPi',
                  **{'m_{KK#pi}' : histos['m_KKPi'],
                     'm_{#Phi#pi}' : histos['m_PhiPi']})

    # m_KPiPi_SS and KPiPi_OS
    drawMultiPlot(outFile_name, ';m_{K#pi#pi} [MeV];', 'm_KPiPi',
                  **{'m_{K^{+}#pi^{-}#pi^{-}}' : histos['m_KPiPi_SS'],
                     'm_{K^{-}#pi^{+}#pi^{-}}' : histos['m_KPiPi_OS']})
    drawMultiPlot(outFile_name, 'not in D peak;m_{K#pi#pi} [MeV];', 'm_KPiPi_noD',
                  **{'m_{K^{+}#pi^{-}#pi^{-}}' : histos['m_KPiPi_SS_noD'],
                     'm_{K^{-}#pi^{+}#pi^{-}}' : histos['m_KPiPi_OS_noD']})
    
 
    #Plot various histos
    for key in ('m_PiPi', 'm_PiPi_noD', 'm_KPi_fromMu','m_KPi_fromMu_noD' , 'm_KKPi_D' ,'Tau_DTF_PROB', 'Tau_DTFTau_PROB'):
        histos[key].Draw()
        c1.Update()  
        c1.Print(outFile_name)



    # Fit m_DTF_Phi
    gStyle.SetOptFit(1111)
    histo = histos['m_DTF_Phi']

    from ROOT import RooFit, RooRealVar, RooDataHist, RooArgList
    x = RooRealVar('x', 'm_{#Phi} [MeV]', 1008,1032)
    ral = RooArgList(x)
    dh = RooDataHist ("dh","dh",ral,RooFit.Import(histo))
    frame = x.frame(RooFit.Title('Mass Decay Tree Fitter m_{#Phi} constrained'))
    dh.plotOn(frame)

    mean = RooRealVar("mean","mean",1020,1010,1025) 
    sigma = RooRealVar("sigma","sigma",3,0.1,10)
    alpha = RooRealVar('alpha', 'alpha', 1, 0.1, 10)
    param_n = RooRealVar('param_n','param_n', 2, 0.1, 10)
    #pdf = ROOT.RooGaussian("gauss","gauss",x,mean,sigma)
    pdf = ROOT.RooBreitWigner('BW','BW',x,mean, sigma)
    #pdf = ROOT.RooVoigtian('voit','voit', x, mean, sigma)
    #pdf = ROOT.RooCBShape('CB','CB', x, mean, sigma, alpha, param_n)

    fit_region = x.setRange("fit_region",1015,1025)
    pdf.fitTo(dh, RooFit.Range("fit_region"))
    pdf.paramOn(frame, RooFit.Layout(0.1,0.44,0.9))
    pdf.plotOn(frame)
    chi2 = round(frame.chiSquare(),2)
    leg = TLegend(0.3,0,.10,.10)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(0,'#chi^{2} ='+str(chi2),'')
    frame.addObject(leg)
    
    frame.Draw()
    c1.Update()  
    c1.Print(outFile_name)


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
 

    c1.Print(outFile_name+']')


def makeComparePlots():
    # global sample
    # sample = 'compare'

    histos2 = {}
    histoFile = {}
    for sample in ('data2012', 'tau2PhiMuFromPDs'):
        histoFile[sample] = TFile('histos_'+sample+'.root')
        histos = {}
        for key in histoFile[sample].GetListOfKeys():
            histos[key.GetName()] = histoFile[sample].Get(key.GetName())
        histos2[sample] = histos
        histos['m_KPiPi'] = histos['m_KPiPi_OS'].Clone()
        histos['m_KPiPi'].SetNameTitle('m_KPiPi','Combinatorial mass;m_{K#pi#pi} [MeV];')
        histos['m_KPiPi'].Add(histos['m_KPiPi_SS'])
        histos['m_KPiPi_noD'] = histos['m_KPiPi_OS_noD'].Clone()
        histos['m_KPiPi_noD'].SetNameTitle('m_KPiPi_noD','Combinatorial mass, no D peak;m_{K#pi#pi} [MeV];')
        histos['m_KPiPi_noD'].Add(histos['m_KPiPi_SS_noD'])

    outFile_name = 'plots_comparison.pdf'
    c1 = TCanvas('c1', 'c1')
    c1.Print(outFile_name+'[')

    for histos in histos2.values():
        for histo in histos.values():
            histo.Scale(1./histo.Integral())

    compare_dict = dict(Tau_DTF_PROB = ('Probability DTF m_{#Phi} constrained;prob;', 'DTF_prob_phi'),
                        Tau_DTFTau_PROB = ('Probability DTF m_{#tau} constrained;prob;', 'DTF_prob_tau'),
                        Tau_DTF_PROB_SR = ('Probability DTF m_{#Phi} constrained, background in signal region;prob;', 'DTF_prob_phi_SR'),
                        Tau_DTFTau_PROB_SR = ('Probability DTF m_{#tau} constrained, background in signal region;prob;', 'DTF_prob_tau_SR'),
                        m_Phi = ('Phi mass;m_{#Phi [MeV]};', 'm_phi'),
                        m_Tau = ('Tau mass;m_{#tau [MeV]};', 'm_tau'),
                        m_KPi = ('Combinatorial mass;m_{K^{+}#pi^{-}} [MeV];', 'm_KPi'),
                        m_PhiPi = ('Combinatorial mass;m_{#Phi#pi} [MeV];', 'm_PhiPi'),
                        m_KPi_fromMu = ('Combinatorial mass;m_{K^{+}#pi^{-}} #mu misID as #pi [MeV];', 'm_KPi_fromMu'),
                        m_KPi_fromMu_noD = ('Combinatorial mass no D peak;m_{K^{+}#pi^{-}} #mu misID as #pi [MeV];', 'm_KPi_fromMu_noD'),
                        m_KPiPi = ('Combinatorial mass;m_{K#pi#pi} [MeV];', 'm_KPiPi'),
                        m_KPiPi_noD = ('Combinatorial mass no D peak;m_{K#pi#pi} [MeV];', 'm_KPiPi_noD'),
                        Mu_ProbNNmu = ('Mu_ProbNNmu','Probability to be a #mu;probability to be a #mu;'), 
                        Mu_ProbNNpi = ('Mu_ProbNNpi','Probability to be a #pi;probability to be a #pi;'),
                        )

    isLogY = {key: key in ('Tau_DTF_PROB', 'Tau_DTFTau_PROB', 'Tau_DTF_PROB_SR', 'Tau_DTFTau_PROB_SR', 'Mu_ProbNNmu', 'Mu_ProbNNpi') for key in compare_dict.keys()}

    for key, (title, name) in compare_dict.items():
        drawMultiPlot(outFile_name, title, name, isLogY[key], #isLogY[key],
                      **{'signal' : histos2['tau2PhiMuFromPDs'][key],
                         'background' : histos2['data2012'][key]})
    
    
    c1.Print(outFile_name+']')



if __name__ == '__main__':
    
    sample = 'data2012'
    sample = 'tau2PhiMuFromPDs'
    
    
    for sample in ('data2012', 'tau2PhiMuFromPDs'):
        #makeHistos()
        makePlots()
    sample = 'compare'
    makeComparePlots()
