// Mono-tau search on Run2024D Tau data (file_config_data.json).
//
// H1: a heavy charged boson W' coupling mainly to the 3rd generation (a proposed
//     explanation of the R(D), R(D*) B-anomalies) decays W' -> tau nu. The same
//     signature covers tau-philic dark-matter mediators (tau + invisible).
// Signature: one high-pT tau_h back-to-back with MET, pT(tau)/MET ~ 1,
//     discriminant m_T(tau, MET) with a Jacobian edge near M(W').
//
// Background from jets faking taus is estimated from data (fake-factor method):
//   MR (measurement): pT(tau)/MET > 2, multijet-dominated
//       FF(pT) = N(tight tau) / N(loose-not-tight tau)
//   AR (application): signal kinematics, loose-not-tight tau, weighted by FF
//   SR (signal): signal kinematics, tight tau
//
// Test 1 (counting): N(SR) vs fake prediction for m_T > X.
// Test 2 (charge asymmetry): after fake subtraction, a charged current from
//   u-quark PDFs gives A = (N+ - N-)/(N+ + N-) > 0, growing with mass; fakes
//   give A ~ 0. Fake-region asymmetry is printed as a built-in control.
//
// SM W -> tau nu, ttbar, and Z -> nunu + jet are NOT modelled; an excess over
// fakes alone is expected and needs MC before any W' claim.

#include "Config.C"
#include "Config.h"
#include "event.C"
#include "event.h"

#include <cmath>
#include <iostream>
#include <memory>

#include "TTreeReader.h"
#include "TTreeReaderArray.h"
#include "TTreeReaderValue.h"
#include "TVector2.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TFile.h"

namespace
{
    constexpr Double_t TAU_PT_MIN = 200.0;
    constexpr Double_t TAU_ETA_MAX = 2.1;
    constexpr Double_t TAU_DZ_MAX = 0.2;
    constexpr Double_t MET_MIN = 150.0;
    constexpr Double_t BALANCE_LOW = 0.7;
    constexpr Double_t BALANCE_HIGH = 1.3;
    constexpr Double_t MR_BALANCE_MIN = 2.0;
    constexpr Double_t DPHI_MIN = 2.4;

    // DeepTau 2018v2p5: vsJet/vsE 1..8 = VVVLoose..VVTight, vsMu 1..4 = VLoose..Tight
    constexpr UChar_t VSJET_LOOSE = 1;
    constexpr UChar_t VSJET_TIGHT = 5;
    constexpr UChar_t VSE_MIN = 4;
    constexpr UChar_t VSMU_MIN = 4;

    constexpr Double_t EXTRA_TAU_PT = 30.0;
    constexpr Double_t LEPTON_VETO_PT = 10.0;

    const char *TRIGGER = "HLT_LooseDeepTauPFTauHPS180_L2NN_eta2p1";

    const Double_t PT_BINS[] = {200, 250, 300, 400, 600, 3000};
    constexpr Int_t N_PT_BINS = 5;
    constexpr Int_t N_MT_BINS = 60;
    constexpr Double_t MT_RANGE_MAX = 3000.0;

    const Double_t COUNT_THRESHOLDS[] = {400, 600, 800, 1000, 1500, 2000};
    constexpr Double_t ASYM_SPLIT = 500.0;

    enum Charge
    {
        PLUS,
        MINUS,
        N_CHARGES
    };

    struct Histos
    {
        std::unique_ptr<TH1D> ptMrTight, ptMrLoose;
        std::unique_ptr<TH2D> ar[N_CHARGES];
        std::unique_ptr<TH1D> sr[N_CHARGES];
    };

    struct Estimate
    {
        Double_t value = 0;
        Double_t variance = 0;
    };

    bool isStandardDecayMode(UChar_t dm)
    {
        return dm == 0 || dm == 1 || dm == 10 || dm == 11;
    }

    Double_t transverseMass(Double_t pt, Double_t phi, Double_t met, Double_t metPhi)
    {
        return std::sqrt(2 * pt * met * (1 - std::cos(TVector2::Phi_mpi_pi(phi - metPhi))));
    }

    Histos makeHistos()
    {
        Histos h;
        h.ptMrTight = std::make_unique<TH1D>("h_pt_MR_tight", "MR tight #tau;p_{T}^{#tau} [GeV];Events", N_PT_BINS, PT_BINS);
        h.ptMrLoose = std::make_unique<TH1D>("h_pt_MR_loose", "MR loose-not-tight #tau;p_{T}^{#tau} [GeV];Events", N_PT_BINS, PT_BINS);
        const char *tag[N_CHARGES] = {"plus", "minus"};
        for (int c = 0; c < N_CHARGES; ++c)
        {
            const TString t = tag[c];
            h.ar[c] = std::make_unique<TH2D>("h2_AR_" + t, "AR " + t + ";p_{T}^{#tau} [GeV];m_{T} [GeV]",
                                             N_PT_BINS, PT_BINS, N_MT_BINS, 0, MT_RANGE_MAX);
            h.sr[c] = std::make_unique<TH1D>("h_mT_SR_" + t, "SR " + t + ";m_{T} [GeV];Events", N_MT_BINS, 0, MT_RANGE_MAX);
        }
        return h;
    }

    std::unique_ptr<TH1D> fakeFactors(const Histos &h)
    {
        auto ff = std::unique_ptr<TH1D>((TH1D *)h.ptMrTight->Clone("h_fakeFactor"));
        ff->SetTitle("fake factor;p_{T}^{#tau} [GeV];FF");
        for (Int_t i = 1; i <= N_PT_BINS; ++i)
        {
            const Double_t t = h.ptMrTight->GetBinContent(i);
            const Double_t l = h.ptMrLoose->GetBinContent(i);
            const Double_t v = l > 0 ? t / l : 0;
            ff->SetBinContent(i, v);
            ff->SetBinError(i, (t > 0 && l > 0) ? v * std::sqrt(1 / t + 1 / l) : 0);
        }
        return ff;
    }

    Estimate fakePrediction(const TH2D &ar, const TH1D &ff, Double_t mtLow, Double_t mtHigh)
    {
        const Int_t first = ar.GetYaxis()->FindFixBin(mtLow);
        const Int_t last = ar.GetYaxis()->FindFixBin(mtHigh - 1e-6);
        Estimate e;
        for (Int_t i = 1; i <= N_PT_BINS; ++i)
        {
            Double_t n = 0;
            for (Int_t j = first; j <= last; ++j)
            {
                n += ar.GetBinContent(i, j);
            }
            const Double_t f = ff.GetBinContent(i);
            const Double_t fErr = ff.GetBinError(i);
            e.value += f * n;
            e.variance += f * f * n + n * n * fErr * fErr;
        }
        return e;
    }

    Double_t observed(const TH1D &sr, Double_t mtLow, Double_t mtHigh)
    {
        return sr.Integral(sr.GetXaxis()->FindFixBin(mtLow), sr.GetXaxis()->FindFixBin(mtHigh - 1e-6));
    }

    std::unique_ptr<TH1D> fakeHistogram(const TH2D &ar, const TH1D &ff, const char *name)
    {
        auto out = std::make_unique<TH1D>(name, "fake prediction;m_{T} [GeV];Events", N_MT_BINS, 0, MT_RANGE_MAX);
        for (Int_t j = 1; j <= N_MT_BINS; ++j)
        {
            const Estimate e = fakePrediction(ar, ff, out->GetXaxis()->GetBinLowEdge(j), out->GetXaxis()->GetBinUpEdge(j));
            out->SetBinContent(j, e.value);
            out->SetBinError(j, std::sqrt(e.variance));
        }
        return out;
    }

    Double_t asymmetry(Double_t plus, Double_t minus)
    {
        return (plus + minus) > 0 ? (plus - minus) / (plus + minus) : 0;
    }

    Double_t asymmetryError(Double_t plus, Double_t minus, Double_t varPlus, Double_t varMinus)
    {
        const Double_t sum = plus + minus;
        if (sum <= 0)
        {
            return 0;
        }
        return 2 / (sum * sum) * std::sqrt(minus * minus * varPlus + plus * plus * varMinus);
    }

    void runCountingTest(const Histos &h, const TH1D &ff)
    {
        std::cout << "\n[Test 1] counting: SR vs jet->tau fake prediction" << std::endl;
        for (Double_t x : COUNT_THRESHOLDS)
        {
            Double_t nObs = 0;
            Estimate fake;
            for (int c = 0; c < N_CHARGES; ++c)
            {
                nObs += observed(*h.sr[c], x, MT_RANGE_MAX);
                const Estimate e = fakePrediction(*h.ar[c], ff, x, MT_RANGE_MAX);
                fake.value += e.value;
                fake.variance += e.variance;
            }
            const Double_t denom = std::sqrt(std::max(fake.value, 1.0) + fake.variance);
            std::cout << "  m_T > " << x << " GeV:  observed " << nObs << "   fakes " << fake.value
                      << " +- " << std::sqrt(fake.variance) << "   excess " << (nObs - fake.value) / denom << " sigma" << std::endl;
        }
    }

    void printAsymmetry(const char *label, const Histos &h, const TH1D &ff, Double_t low, Double_t high)
    {
        const Double_t nPlus = observed(*h.sr[PLUS], low, high);
        const Double_t nMinus = observed(*h.sr[MINUS], low, high);
        const Estimate fPlus = fakePrediction(*h.ar[PLUS], ff, low, high);
        const Estimate fMinus = fakePrediction(*h.ar[MINUS], ff, low, high);

        const Double_t sPlus = nPlus - fPlus.value;
        const Double_t sMinus = nMinus - fMinus.value;
        const Double_t aSig = asymmetry(sPlus, sMinus);
        const Double_t eSig = asymmetryError(sPlus, sMinus, nPlus + fPlus.variance, nMinus + fMinus.variance);
        const Double_t aFake = asymmetry(fPlus.value, fMinus.value);
        const Double_t eFake = asymmetryError(fPlus.value, fMinus.value, fPlus.variance, fMinus.variance);

        std::cout << "  " << label << ": tau+ " << nPlus << "  tau- " << nMinus << std::endl;
        std::cout << "    A(fake-subtracted) = " << aSig << " +- " << eSig
                  << "   A(fakes, control) = " << aFake << " +- " << eFake << std::endl;
        if (eSig > 0)
        {
            std::cout << "    => " << (aSig / eSig > 3 ? "positive asymmetry: charged-current origin (W-like)"
                                                         : "no significant charged-current asymmetry")
                      << std::endl;
        }
    }

    void runAsymmetryTest(const Histos &h, const TH1D &ff)
    {
        std::cout << "\n[Test 2] tau charge asymmetry" << std::endl;
        printAsymmetry("m_T < 500 GeV (SM W tail)", h, ff, 0, ASYM_SPLIT);
        printAsymmetry("m_T > 500 GeV (W' region)", h, ff, ASYM_SPLIT, MT_RANGE_MAX);
    }
} // namespace

void TauWprimeMonoTau()
{
    TH1::AddDirectory(kFALSE);
    std::vector<RootFileEntry> rootFiles = loadRootFileList("file_config_data.json");
    std::cout << "TauWprimeMonoTau: " << rootFiles.size() << " file(s) to process." << std::endl;

    Histos h = makeHistos();
    Long64_t nRead = 0, nTrigger = 0, nSingleTau = 0, nMR = 0, nAR = 0, nSR = 0;
    bool warnedNoTrigger = false;

    for (const RootFileEntry &file : rootFiles)
    {
        std::cout << "reading: " << file.path << std::endl;
        TTree *Events = getEventsTree(file.path);
        if (!Events)
        {
            continue;
        }

        TTreeReader reader(Events);
        TTreeReaderArray<Float_t> tauPt(reader, "Tau_pt");
        TTreeReaderArray<Float_t> tauEta(reader, "Tau_eta");
        TTreeReaderArray<Float_t> tauPhi(reader, "Tau_phi");
        TTreeReaderArray<Float_t> tauDz(reader, "Tau_dz");
        TTreeReaderArray<Short_t> tauCharge(reader, "Tau_charge");
        TTreeReaderArray<UChar_t> tauDecayMode(reader, "Tau_decayMode");
        TTreeReaderArray<UChar_t> tauVsJet(reader, "Tau_idDeepTau2018v2p5VSjet");
        TTreeReaderArray<UChar_t> tauVsE(reader, "Tau_idDeepTau2018v2p5VSe");
        TTreeReaderArray<UChar_t> tauVsMu(reader, "Tau_idDeepTau2018v2p5VSmu");
        TTreeReaderArray<Float_t> muPt(reader, "Muon_pt");
        TTreeReaderArray<Float_t> muEta(reader, "Muon_eta");
        TTreeReaderArray<Bool_t> muLooseId(reader, "Muon_looseId");
        TTreeReaderArray<Float_t> muIso(reader, "Muon_pfRelIso04_all");
        TTreeReaderArray<Float_t> elPt(reader, "Electron_pt");
        TTreeReaderArray<Float_t> elEta(reader, "Electron_eta");
        TTreeReaderArray<UChar_t> elCutBased(reader, "Electron_cutBased");
        TTreeReaderValue<Float_t> metPt(reader, "PuppiMET_pt");
        TTreeReaderValue<Float_t> metPhi(reader, "PuppiMET_phi");

        std::unique_ptr<TTreeReaderValue<Bool_t>> trigger;
        if (Events->GetBranch(TRIGGER))
        {
            trigger = std::make_unique<TTreeReaderValue<Bool_t>>(reader, TRIGGER);
        }
        else if (!warnedNoTrigger)
        {
            std::cout << "WARNING: " << TRIGGER << " missing, running without trigger requirement" << std::endl;
            warnedNoTrigger = true;
        }

        while (reader.Next())
        {
            ++nRead;
            if (trigger && !**trigger)
            {
                continue;
            }
            ++nTrigger;

            bool extraLepton = false;
            for (size_t i = 0; i < muPt.GetSize() && !extraLepton; ++i)
            {
                extraLepton = muPt[i] > LEPTON_VETO_PT && std::abs(muEta[i]) < 2.4 && muLooseId[i] && muIso[i] < 0.3;
            }
            for (size_t i = 0; i < elPt.GetSize() && !extraLepton; ++i)
            {
                extraLepton = elPt[i] > LEPTON_VETO_PT && std::abs(elEta[i]) < 2.5 && elCutBased[i] >= 2;
            }
            if (extraLepton)
            {
                continue;
            }

            size_t iTau = SIZE_MAX;
            int nCandidates = 0, nExtraTaus = 0;
            for (size_t i = 0; i < tauPt.GetSize(); ++i)
            {
                const bool baseId = isStandardDecayMode(tauDecayMode[i]) && tauVsE[i] >= VSE_MIN &&
                                    tauVsMu[i] >= VSMU_MIN && std::abs(tauDz[i]) < TAU_DZ_MAX &&
                                    std::abs(tauEta[i]) < TAU_ETA_MAX;
                if (!baseId)
                {
                    continue;
                }
                if (tauPt[i] > TAU_PT_MIN && tauVsJet[i] >= VSJET_LOOSE)
                {
                    ++nCandidates;
                    iTau = i;
                }
                else if (tauPt[i] > EXTRA_TAU_PT && tauVsJet[i] >= VSJET_TIGHT)
                {
                    ++nExtraTaus;
                }
            }
            if (nCandidates != 1 || nExtraTaus > 0)
            {
                continue;
            }
            ++nSingleTau;

            const Double_t pt = tauPt[iTau];
            const bool tight = tauVsJet[iTau] >= VSJET_TIGHT;
            const Double_t balance = *metPt > 0 ? pt / *metPt : 1e9;

            if (balance > MR_BALANCE_MIN)
            {
                ++nMR;
                (tight ? h.ptMrTight : h.ptMrLoose)->Fill(std::min(pt, PT_BINS[N_PT_BINS] - 1));
                continue;
            }

            const Double_t dPhi = std::abs(TVector2::Phi_mpi_pi(tauPhi[iTau] - *metPhi));
            const bool signalKinematics = *metPt > MET_MIN && balance > BALANCE_LOW &&
                                          balance < BALANCE_HIGH && dPhi > DPHI_MIN;
            if (!signalKinematics)
            {
                continue;
            }

            const Charge c = tauCharge[iTau] > 0 ? PLUS : MINUS;
            const Double_t mT = std::min(transverseMass(pt, tauPhi[iTau], *metPt, *metPhi), MT_RANGE_MAX - 1);
            if (tight)
            {
                ++nSR;
                h.sr[c]->Fill(mT);
            }
            else
            {
                ++nAR;
                h.ar[c]->Fill(std::min(pt, PT_BINS[N_PT_BINS] - 1), mT);
            }
        }
    }

    std::cout << "\nevents read: " << nRead << "  trigger: " << nTrigger << "  single-tau: " << nSingleTau
              << "  MR: " << nMR << "  AR: " << nAR << "  SR: " << nSR << std::endl;

    auto ff = fakeFactors(h);
    std::cout << "fake factors per pT bin:" << std::endl;
    for (Int_t i = 1; i <= N_PT_BINS; ++i)
    {
        std::cout << "  " << PT_BINS[i - 1] << "-" << PT_BINS[i] << " GeV: " << ff->GetBinContent(i)
                  << " +- " << ff->GetBinError(i) << std::endl;
    }

    runCountingTest(h, *ff);
    runAsymmetryTest(h, *ff);

    auto fakePlus = fakeHistogram(*h.ar[PLUS], *ff, "h_mT_fake_plus");
    auto fakeMinus = fakeHistogram(*h.ar[MINUS], *ff, "h_mT_fake_minus");

    const std::string outFile = "outputs/tau_wprime_monotau.root";
    TFile out(outFile.c_str(), "RECREATE");
    h.ptMrTight->Write();
    h.ptMrLoose->Write();
    ff->Write();
    for (int c = 0; c < N_CHARGES; ++c)
    {
        h.ar[c]->Write();
        h.sr[c]->Write();
    }
    fakePlus->Write();
    fakeMinus->Write();
    out.Close();
    std::cout << "\nTauWprimeMonoTau: wrote " << outFile << std::endl;
}
