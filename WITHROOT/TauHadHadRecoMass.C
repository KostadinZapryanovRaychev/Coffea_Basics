#include "TauHadHadRecoMass.h"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <utility>

#include "BranchReader.h"
#include "Selector.h"
#include "HistogramWriter.h"
#include "MassPointUtils.h"

namespace
{
// Runs the Selector::select() calls for a given cut, pairs up consecutive
// (leg1, leg2) entries (see the k/i1/i2 discussion -- valid whenever the
// cut guarantees exactly 2 matching GenVisTau per selected event), and
// computes m_rec(Z') per event via Eq. (1) of arXiv:2412.04357:
//
//   m_rec = sqrt[ (E1+E2+|pT_miss|)^2 - (pz1+pz2)^2 ]
//
// pT_miss = -(pT1_vis + pT2_vis) (zero net Z' transverse momentum
// assumed), pz_miss = 0. The transverse part of (p1vis+p2vis+p_miss)
// cancels to exactly zero by construction, which is why only the pz term
// survives under the square root -- an exact simplification, not an
// approximation.
std::vector<Double_t> computeHadHadMasses(Selector &selector, const std::string &cut,
                                          Long64_t maxEvents)
{
    std::vector<Double_t> pt = selector.select("GenVisTau_pt", cut, maxEvents);
    std::vector<Double_t> eta = selector.select("GenVisTau_eta", cut, maxEvents);
    std::vector<Double_t> phi = selector.select("GenVisTau_phi", cut, maxEvents);
    std::vector<Double_t> mass = selector.select("GenVisTau_mass", cut, maxEvents);

    const size_t nEvents = pt.size() / 2; // two GenVisTau entries per selected event
    std::vector<Double_t> mRec;
    mRec.reserve(nEvents);

    for (size_t k = 0; k < nEvents; k++)
    {
        const size_t i1 = 2 * k;
        const size_t i2 = 2 * k + 1;

        // px = pt*cos(phi), py = pt*sin(phi), pz = pt*sinh(eta),
        // E = sqrt(px^2 + py^2 + pz^2 + mass^2)
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

    return mRec;
}
} // namespace

void TauHadHadRecoMass::run(TTree *Events, Bool_t debug, Long64_t maxEvents,
                            const std::string &inputFilePath)
{
    // ======================================================================
    // 1. BRANCH ENABLING
    // GenVisTau is the truth-level answer to "if this tau decayed
    // hadronically, what would its visible decay products look like
    // combined?" It exists only for hadronic decays -- a tau that
    // decayed to a muon or electron has no GenVisTau entry.
    // nGenVisTau       - how many gen-level hadronic taus are in this event
    // GenVisTau_pt     - transverse momentum of the visible hadrons (no neutrino)
    // GenVisTau_eta    - needed to build the 4-vector (gives pz, E)
    // GenVisTau_phi    - needed to build the 4-vector, and for pT_miss
    // GenVisTau_mass   - needed for E = sqrt(px^2+py^2+pz^2+mass^2)
    // GenVisTau_charge - used only for the opposite-sign event selection
    // GenVisTau_status - decay mode / prong: 0=1prong0pi0, 1=1prong1pi0,
    //                    2=1prong2pi0, 10=3prong0pi0, 11=3prong1pi0,
    //                    15=other (see the NanoAOD GenVisTau doc)
    // ======================================================================
    BranchReader reader(Events);
    reader.enableBranches({"nGenVisTau", "GenVisTau_pt", "GenVisTau_eta", "GenVisTau_phi",
                           "GenVisTau_mass", "GenVisTau_charge", "GenVisTau_status"});

    if (debug)
    {
        std::cout << "TauHadHadRecoMass: DEBUG mode has no dedicated column dumps yet."
                  << std::endl;
    }

    Selector selector(Events);
    const Double_t M = MassPointUtils::extractMassPoint(inputFilePath);
    const std::string outFile = "outputs/hadhad_rec_mass.root";

    // ======================================================================
    // 2. ALL PRONGS COMBINED: exactly two opposite-sign GenVisTau per
    // event, no decay-mode restriction -- every hadronic decay mode mixed
    // together, same as before.
    // ======================================================================
    const std::string allCut = "nGenVisTau == 2 && Sum$(GenVisTau_charge) == 0";
    std::vector<Double_t> mRecAll = computeHadHadMasses(selector, allCut, maxEvents);

    std::cout << "TauHadHadRecoMass: " << mRecAll.size() << " tau_h tau_h candidate events "
              << "(all prongs) out of " << maxEvents << "." << std::endl;

    HistogramWriter::write(mRecAll, "m_rec_hadhad", 250, 0, 2.0 * M, outFile, "RECREATE");

    // ======================================================================
    // 3. PER-PRONG BREAKDOWN: same selection, but additionally requiring
    // BOTH legs to have the same GenVisTau_status (decay mode). This is
    // an event-level requirement (Sum$(GenVisTau_status==s)==2 means
    // exactly two objects in the event have that status), on top of the
    // per-object cut GenVisTau_status==s -- together they guarantee
    // exactly two same-status entries per selected event, so the
    // consecutive-pair math in computeHadHadMasses() still applies.
    // ======================================================================
    const std::vector<std::pair<Int_t, std::string>> prongCategories = {
        {0, "OneProng0PiZero"},
        {1, "OneProng1PiZero"},
        {2, "OneProng2PiZero"},
        {10, "ThreeProng0PiZero"},
        {11, "ThreeProng1PiZero"},
        {15, "Other"},
    };

    for (const auto &category : prongCategories)
    {
        const Int_t status = category.first;
        const std::string &name = category.second;

        const std::string cut = "nGenVisTau == 2 && GenVisTau_status == " + std::to_string(status) +
                                " && Sum$(GenVisTau_status == " + std::to_string(status) + ") == 2" +
                                " && Sum$(GenVisTau_charge) == 0";

        std::vector<Double_t> mRec = computeHadHadMasses(selector, cut, maxEvents);
        std::cout << "TauHadHadRecoMass: " << mRec.size() << " events with both legs "
                  << name << " (status " << status << ")." << std::endl;

        HistogramWriter::write(mRec, "m_rec_hadhad_" + name, 250, 0, 2.0 * M, outFile, "UPDATE");
    }
}
