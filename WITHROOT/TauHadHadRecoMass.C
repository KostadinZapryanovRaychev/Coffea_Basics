#include "TauHadHadRecoMass.h"

#include <algorithm>
#include <cmath>
#include <iostream>

#include "BranchReader.h"
#include "Selector.h"
#include "HistogramWriter.h"
#include "MassPointUtils.h"

void TauHadHadRecoMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                            const std::string &inputFilePath)
{
    // ======================================================================
    // 1. BRANCH ENABLING
    // GenVisTau So GenVisTau is the truth-level answer to "if this tau decayed hadronically, what would its visible decay products look like combined?"
    // It exists only for hadronic decays — a tau that decayed to a muon or electron has no GenVisTau
    // nGenVisTau - how many gen-level hadronic taus are in this event
    // GenVisTau_pt - the transverse momentum of hadronic tau decay without the neutrino
    // GenVisTau_eta -  we need this to construct the 4-vector of the hadronic tau decay
    // GenVisTau_phi - we need this to construct the 4-vector of the hadronic tau decay
    // GenVisTau_mass - we need this to construct the 4-vector of the hadronic tau decay
    // GenVisTau_charge - we need this to select events with exactly two hadronic taus of opposite charge
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nGenVisTau", "GenVisTau_pt", "GenVisTau_eta",
                           "GenVisTau_phi", "GenVisTau_mass", "GenVisTau_charge"});

    if (debug)
    {
        std::cout << "TauHadHadRecoMass: DEBUG mode has no dedicated column dumps yet."
                  << std::endl;
    }

    // ======================================================================
    // 2. SELECT EVENTS WITH EXACTLY TWO OPPOSITE-SIGN GENVIS TAUS
    // ======================================================================
    Selector selector(Events);

    const std::string cut = "nGenVisTau == 2 && Sum$(GenVisTau_charge) == 0";

    std::vector<Double_t> pt = selector.select("GenVisTau_pt", cut, maxEvents);
    std::vector<Double_t> eta = selector.select("GenVisTau_eta", cut, maxEvents);
    std::vector<Double_t> phi = selector.select("GenVisTau_phi", cut, maxEvents);
    std::vector<Double_t> mass = selector.select("GenVisTau_mass", cut, maxEvents);

    const size_t nEvents = pt.size() / 2; // two GenVisTau entries per selected event
    std::cout << "TauHadHadRecoMass: " << nEvents << " tau_h tau_h candidate events "
              << "(exactly 2 opposite-sign GenVisTau) out of " << maxEvents << "."
              << std::endl;

    // ======================================================================
    // 3. m_rec(Z') PER EVENT, following Eq. (1) of arXiv:2412.04357:
    //
    //   m_rec = sqrt[ (E1+E2+|pT_miss|)^2 - (pz1+pz2)^2 ]
    //
    // where pT_miss = -(pT1_vis + pT2_vis) (zero net transverse momentum
    // assumed for the Z') and pz_miss = 0. Note the transverse part of
    // (p1vis + p2vis + p_miss) cancels to exactly zero by construction
    // (pT_miss is defined to cancel the visible legs' combined pT), which
    // is why only the pz term survives under the square root below --
    // that simplification is exact, not an approximation.
    // ======================================================================
    std::vector<Double_t> mRec;
    mRec.reserve(nEvents);
    for (size_t k = 0; k < nEvents; k++)
    {
        // we use this because
        // k=0 → i1=0, i2=1 → event0's two legs ✓
        // k=1 → i1=2, i2=3 → event1's two legs ✓
        // k=2 → i1=4, i2=5 → event2's two legs ✓
        const size_t i1 = 2 * k;
        const size_t i2 = 2 * k + 1;

        // reconstruct the 4-vectors of the two GenVisTau legs, by the formulae in the NanoAOD documentation (https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#GenVisTau)
        const Double_t px1 = pt[i1] * std::cos(phi[i1]);
        const Double_t py1 = pt[i1] * std::sin(phi[i1]);
        const Double_t pz1 = pt[i1] * std::sinh(eta[i1]);
        const Double_t E1 = std::sqrt(px1 * px1 + py1 * py1 + pz1 * pz1 + mass[i1] * mass[i1]);

        const Double_t px2 = pt[i2] * std::cos(phi[i2]);
        const Double_t py2 = pt[i2] * std::sin(phi[i2]);
        const Double_t pz2 = pt[i2] * std::sinh(eta[i2]);
        const Double_t E2 = std::sqrt(px2 * px2 + py2 * py2 + pz2 * pz2 + mass[i2] * mass[i2]);

        const Double_t missPt = std::sqrt((px1 + px2) * (px1 + px2) + (py1 + py2) * (py1 + py2));
        const Double_t energyTerm = E1 + E2 + missPt;
        const Double_t pzTerm = pz1 + pz2;

        const Double_t mRecSquared = energyTerm * energyTerm - pzTerm * pzTerm;
        mRec.push_back(std::sqrt(std::max(0.0, mRecSquared)));
    }

    // ======================================================================
    // 4. PLOTTING
    // ======================================================================
    const Double_t M = MassPointUtils::extractMassPoint(inputFilePath);
    HistogramWriter::write(mRec, "m_rec_hadhad", 250, 0, 2.0 * M,
                           "outputs/hadhad_rec_mass.root", "RECREATE");
}
