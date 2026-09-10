#include "TauHadHadDataMass.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "TMath.h"

#include "BranchReader.h"
#include "Selector.h"
#include "HistogramWriter.h"

namespace
{
// ----------------------------------------------------------------------
// The per-tau selection for the tau_h tau_h channel. Every tau candidate
// must pass ALL of these to count. Straight from the CMS Z'->tautau
// analysis note (Table 23) and arXiv:2412.04357 Sec. 6.3 -- the same
// list documented in WITHROOT/README.md, applied here to real data:
//
//   Tau_pt > 70 GeV          the di-tau trigger is only ~90% efficient
//                            above this; below it, data is unreliable
//   |Tau_eta| < 2.1          tracker acceptance / where DeepTau works
//   |Tau_dz| < 0.2 cm        tau comes from the main collision vertex,
//                            not from a pileup collision
//   DeepTau VSjet >= 6 (Tight)   reject ordinary QCD jets faking a tau
//   DeepTau VSmu  >= 4 (Tight)   reject muons faking a 1-prong tau
//   DeepTau VSe   >= 4 (Loose)   reject electrons faking a tau.
//                            NOTE: the analysis note uses Loose-vs-e
//                            specifically for the tau_h tau_h channel
//                            (Table 23); the later published paper uses
//                            Medium for every channel. Loose is the
//                            channel-correct choice, so it is used here.
//   Tau_decayMode in {0,1,2,10,11}   real 1-prong / 3-prong topologies
//                            only (mode 5/6 = reconstruction failures)
// ----------------------------------------------------------------------
const std::string TAU_SELECTION =
    "Tau_pt > 70 && abs(Tau_eta) < 2.1 && abs(Tau_dz) < 0.2"
    " && Tau_idDeepTau2018v2p5VSjet >= 6"
    " && Tau_idDeepTau2018v2p5VSmu >= 4"
    " && Tau_idDeepTau2018v2p5VSe >= 4"
    " && (Tau_decayMode == 0 || Tau_decayMode == 1 || Tau_decayMode == 2"
    " || Tau_decayMode == 10 || Tau_decayMode == 11)";

// Run3 di-tau HLT trigger paths, in order of preference. The plain
// HPS35 path is the main tau_h tau_h trigger (successor of the Run2
// HLT_DoubleMediumChargedIsoPFTau* paths); the two "_PFJet" variants
// have a lower tau pT threshold at the cost of also needing a jet.
// Only the paths that actually exist as branches in the input file are
// used, OR'd together -- an event passes the trigger requirement if it
// fired any of them.
const std::vector<std::string> TRIGGER_PATHS = {
    "HLT_DoubleMediumDeepTauPFTauHPS35_L2NN_eta2p1",
    "HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet60",
    "HLT_DoubleMediumDeepTauPFTauHPS30_L2NN_eta2p1_PFJet75",
};

// Build "(pathA == 1 || pathB == 1 || ...)" from the trigger paths that
// exist in the tree. Returns "" if none are present (then no trigger
// requirement is applied -- useful for older/private samples that lack
// these HLT branches).
std::string buildTriggerCut(TTree *Events, std::vector<std::string> &enabledPaths)
{
    std::string cut;
    for (const std::string &path : TRIGGER_PATHS)
    {
        if (Events->GetBranch(path.c_str()) == nullptr)
        {
            continue;
        }
        enabledPaths.push_back(path);
        cut += (cut.empty() ? "(" : " || ");
        cut += path + " == 1";
    }
    if (!cut.empty())
    {
        cut += ")";
    }
    return cut;
}

// Take the flat (leg1, leg2, leg1, leg2, ...) arrays that Selector
// returns -- valid because the cut guarantees exactly 2 selected taus
// per event -- pair them up per event, apply deltaR(tau1,tau2) > 0.3,
// and fill:
//   mRec : m_rec(Z') via Eq. (1) of arXiv:2412.04357
//            m_rec = sqrt[ (E1+E2+|pT_miss|)^2 - (pz1+pz2)^2 ]
//          with pT_miss = -(pT1_vis + pT2_vis), pz_miss = 0.
//   mVis : the naive invariant mass of the two visible 4-vectors,
//          (tau1 + tau2).M() -- WRONG for taus (each visible tau is
//          missing its neutrino), kept only so the difference from
//          m_rec is visible in the plots.
void computeMasses(Selector &selector, const std::string &cut, Long64_t maxEvents,
                   std::vector<Double_t> &mRec, std::vector<Double_t> &mVis)
{
    std::vector<Double_t> pt = selector.select("Tau_pt", cut, maxEvents);
    std::vector<Double_t> eta = selector.select("Tau_eta", cut, maxEvents);
    std::vector<Double_t> phi = selector.select("Tau_phi", cut, maxEvents);
    std::vector<Double_t> mass = selector.select("Tau_mass", cut, maxEvents);

    const size_t nEvents = pt.size() / 2;
    for (size_t k = 0; k < nEvents; k++)
    {
        const size_t i1 = 2 * k;
        const size_t i2 = 2 * k + 1;

        // pt/eta/phi/mass -> px/py/pz/E for each visible tau
        const Double_t px1 = pt[i1] * std::cos(phi[i1]);
        const Double_t py1 = pt[i1] * std::sin(phi[i1]);
        const Double_t pz1 = pt[i1] * std::sinh(eta[i1]);
        const Double_t E1 = std::sqrt(px1 * px1 + py1 * py1 + pz1 * pz1 + mass[i1] * mass[i1]);

        const Double_t px2 = pt[i2] * std::cos(phi[i2]);
        const Double_t py2 = pt[i2] * std::sin(phi[i2]);
        const Double_t pz2 = pt[i2] * std::sinh(eta[i2]);
        const Double_t E2 = std::sqrt(px2 * px2 + py2 * py2 + pz2 * pz2 + mass[i2] * mass[i2]);

        // deltaR(tau1, tau2) = sqrt(dEta^2 + dPhi^2), dPhi wrapped to [-pi, pi].
        // < 0.3 means the two "taus" overlap -- almost certainly one
        // detector object counted twice, so drop the event.
        const Double_t dEta = eta[i1] - eta[i2];
        Double_t dPhi = phi[i1] - phi[i2];
        while (dPhi > TMath::Pi())
        {
            dPhi -= 2.0 * TMath::Pi();
        }
        while (dPhi < -TMath::Pi())
        {
            dPhi += 2.0 * TMath::Pi();
        }
        const Double_t dR = std::sqrt(dEta * dEta + dPhi * dPhi);
        if (dR <= 0.3)
        {
            continue;
        }

        // m_vis : naive sum of the two visible 4-vectors
        const Double_t Esum = E1 + E2;
        const Double_t pxSum = px1 + px2;
        const Double_t pySum = py1 + py2;
        const Double_t pzSum = pz1 + pz2;
        const Double_t mVisSq = Esum * Esum - pxSum * pxSum - pySum * pySum - pzSum * pzSum;
        mVis.push_back(std::sqrt(std::max(0.0, mVisSq)));

        // m_rec : missing pT estimated as -(pT1+pT2); transverse part of
        // (p1 + p2 + p_miss) cancels exactly, so only pz survives.
        const Double_t missPt = std::sqrt(pxSum * pxSum + pySum * pySum);
        const Double_t energyTerm = E1 + E2 + missPt;
        const Double_t mRecSq = energyTerm * energyTerm - pzSum * pzSum;
        mRec.push_back(std::sqrt(std::max(0.0, mRecSq)));
    }
}
} // namespace

void TauHadHadDataMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                            const std::string &inputFilePath)
{
    // ======================================================================
    // 1. BRANCH ENABLING
    // Reconstructed Tau_* kinematics + IDs, Tau_charge for the
    // opposite-sign requirement, plus whichever di-tau HLT paths exist.
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_dz",
                           "Tau_charge", "Tau_decayMode",
                           "Tau_idDeepTau2018v2p5VSjet", "Tau_idDeepTau2018v2p5VSmu",
                           "Tau_idDeepTau2018v2p5VSe"});

    std::vector<std::string> enabledTriggerPaths;
    const std::string triggerCut = buildTriggerCut(Events, enabledTriggerPaths);
    reader.enableBranches(enabledTriggerPaths);

    if (triggerCut.empty())
    {
        std::cerr << "TauHadHadDataMass: none of the expected di-tau HLT paths were "
                  << "found in this file -- running WITHOUT a trigger requirement."
                  << std::endl;
    }
    else
    {
        std::cout << "TauHadHadDataMass: di-tau trigger = " << triggerCut << std::endl;
    }

    if (debug)
    {
        std::cout << "TauHadHadDataMass: DEBUG mode has no dedicated column dumps yet."
                  << std::endl;
    }

    Selector selector(Events);

    // Real collision data has no "M-<number>" in its path, so the plotted
    // mass range is a wide fixed window (the search spans 250-6000 GeV,
    // not one hypothesis). For a private MC signal sample the range is
    // instead scaled to that sample's generated mass.
    const bool looksLikeData = (inputFilePath.find("M-") == std::string::npos);
    Double_t histMax = 3000.0;
    Int_t histBins = 300;
    if (!looksLikeData)
    {
        const size_t pos = inputFilePath.find("M-");
        const Double_t massPoint = std::atof(inputFilePath.c_str() + pos + 2);
        if (massPoint > 0)
        {
            histMax = 2.0 * massPoint;
            histBins = 250;
        }
    }

    const std::string outFile = "outputs/hadhad_data_mass.root";

    // ======================================================================
    // 2. EVENT SELECTION (all combined -- every hadronic decay mode)
    //
    // A tau passes if it satisfies TAU_SELECTION *and* the event has
    // exactly two such taus *and* those two are opposite charge *and*
    // (if available) the event fired the di-tau trigger.
    //
    //   Sum$(TAU_SELECTION) == 2                exactly two good taus
    //   Sum$(Tau_charge * (TAU_SELECTION)) == 0 the two are opposite sign
    //                                           (+1 and -1 cancel)
    // ======================================================================
    std::string fullCut =
        TAU_SELECTION +
        " && Sum$(" + TAU_SELECTION + ") == 2" +
        " && Sum$(Tau_charge * (" + TAU_SELECTION + ")) == 0";
    if (!triggerCut.empty())
    {
        fullCut += " && " + triggerCut;
    }

    std::vector<Double_t> mRecAll, mVisAll;
    computeMasses(selector, fullCut, maxEvents, mRecAll, mVisAll);

    std::cout << "TauHadHadDataMass: " << mRecAll.size() << " tau_h tau_h events "
              << "(2 opposite-sign selected taus, dR>0.3"
              << (triggerCut.empty() ? "" : ", triggered") << ") out of " << maxEvents
              << "." << std::endl;

    HistogramWriter::write(mRecAll, "m_rec_hadhad", histBins, 0, histMax, outFile, "RECREATE");
    HistogramWriter::write(mVisAll, "m_vis_hadhad", histBins, 0, histMax, outFile, "UPDATE");

    // ======================================================================
    // 3. PER-PRONG BREAKDOWN: same selection, but additionally requiring
    // BOTH selected taus to have the same Tau_decayMode.
    //   Sum$((TAU_SELECTION) && Tau_decayMode == d) == 2
    // means exactly two taus pass the selection AND have decay mode d.
    // ======================================================================
    const std::vector<std::pair<Int_t, std::string>> decayModes = {
        {0, "OneProng0PiZero"},
        {1, "OneProng1PiZero"},
        {2, "OneProng2PiZero"},
        {10, "ThreeProng0PiZero"},
        {11, "ThreeProng1PiZero"},
    };

    for (const auto &dm : decayModes)
    {
        const Int_t mode = dm.first;
        const std::string &name = dm.second;
        const std::string modeStr = std::to_string(mode);

        std::string cut =
            TAU_SELECTION + " && Tau_decayMode == " + modeStr +
            " && Sum$((" + TAU_SELECTION + ") && Tau_decayMode == " + modeStr + ") == 2" +
            " && Sum$(Tau_charge * ((" + TAU_SELECTION + ") && Tau_decayMode == " + modeStr + ")) == 0";
        if (!triggerCut.empty())
        {
            cut += " && " + triggerCut;
        }

        std::vector<Double_t> mRec, mVis;
        computeMasses(selector, cut, maxEvents, mRec, mVis);
        std::cout << "TauHadHadDataMass: " << mRec.size() << " events with both taus "
                  << name << " (decayMode " << mode << ")." << std::endl;

        HistogramWriter::write(mRec, "m_rec_hadhad_" + name, histBins, 0, histMax, outFile, "UPDATE");
    }
}
