root -l -b -q main.C
DEBUG=1 root -l -q main.C - if we want to print

## RecoTauMassKinematics: reconstructed-Tau mass + kinematics over multiple files

C++ counterpart of `NAOD_TAU/reco_tau_kinematics.py` and `NAOD_TAU/reco_tau_mass.py`,
combined into one module (`RecoTauMassKinematics.h/.C`). Run it with:

```bash
root -l -b -q RunRecoTauMassKinematics.C
```

It reads the files listed in `file_config_reco.json` (same "root_files" format as
`NAOD_TAU/file_config_batch_all_mass_points.json`: `name`, `path`, `tree`,
`enabled`), pools every file's surviving tau pairs into one set of histograms, and
writes them to `outputs/reco_tau_mass_kinematics.root`. Add or disable entries in
`file_config_reco.json` to run it over a different set of paths.

Selection, per event: take the two leading-pT `Tau` objects, require opposite
sign, `|Δφ| > 2.5`, both `pT > 20 GeV` and `|η| < 2.3`, and pair `|pz| < 300 GeV`
— the same cuts as `reco_tau_kinematics.py`.

Histograms written (all 1D, fixed ranges, no per-mass-point scaling — same as
the python scripts):

- `reco_tau_mass` — invariant mass from `TLorentzVector::M()`.
- `reco_tau_mass_formula` — the same mass, computed by hand from
  `E = sqrt(px^2+py^2+pz^2+m^2)`, as a cross-check that it agrees with `.M()`.
  The macro also prints `max |m_reco - m_reco_formula|` to stdout; it should be
  at float precision.
- `reco_tau_mass_formula_neutrino` — the mother boson (Z/Z') mass estimate,
  adding the missing transverse momentum of the escaping tau neutrinos via
  Eq. (1) of arXiv:2412.04357 / PRD 111, 112004:
  `pT_miss = -(pT1_vis + pT2_vis)`, `pz_miss = 0`,
  `m_rec = sqrt[(E1+E2+|pT_miss|)^2 - (pz1+pz2)^2]`. This should sit closer to
  the true resonance mass than the other two, since it partially accounts for
  the neutrinos they both ignore.
- `reco_tau_pz`, `reco_tau_delta_r`, `reco_tau_cos_delta_phi`, `reco_tau_eta` —
  pair kinematics, same as the python `reco_tau_kinematics.py` output.

{
"inputFile": "../nanoaodsim_coffea_1.root"
}

What is NANOAOD
https://indico.cern.ch/event/708041/papers/3276172/files/8621-nanoaod_acat19_v2.pdf

how to do analysis

https://codimd.web.cern.ch/PMpenr-wQXGb49NavQSu1w?view

https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendationForRun3
tau pdg recommendations

Article

https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.112004

Meaning of columns

https://cms-xpog.docs.cern.ch/autoDoc/NanoAODv12/2022/2023/doc_DYJetsToLL_M-50_TuneCP5_13p6TeV-madgraphMLM-pythia8_Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2.html

interesting to be checked

https://github.com/cms-tau-pog/TauIDSFs/blob/master/docs/TESunc.png

root h_nTau_selection.root
TFile \*f = TFile::Open("tau_pog_mass.root");
f->ls()
new TBrowser();

Each column is called a branch ?

Event Tau_pt Tau_eta Muon_pt Jet_pt HLT_IsoMu24
0 ... ... ... ... ...
1 ... ... ... ... ...
2 ... ... ... ... ...

1782 branches ---> Columns X 60806 rows each

1. Task to try to print each branch for event 1 and to try to understand the meaning of it

rm -f /tmp/main*test /Users/macbookpro/Documents/BAN-Doctor-Degree/Tools/Coffea/WITHROOT/*\_column\_.txt

2.  LHE
    │
    │ hard scattering / matrix element
    ▼
    GEN / GenParticles
    │
    │ parton shower + hadronization
    ▼
    GEN particles / stable final-state particles
    │
    ▼
    SIM
    │
    │ detector simulation
    ▼
    DIGI
    │
    │ detector electronics response
    ▼
    RECO
    │
    │ reconstructed tracks, vertices, jets, electrons, muons, etc.
    ▼
    PAT / MiniAOD
    │
    ▼
    NanoAOD
    │
    ▼
    Analysis

The generator record is usually represented by collections/branches related to:

GenPart
GenJet
GenJetAK8
GenMET

Depending on the format and production, you may also see generator-level information associated with:

GenEventInfo
Generator
Pileup
GenPart\_\*

This is probably the most important one for what you're describing.

Typical branches:

GenPart_pt
GenPart_eta
GenPart_phi
GenPart_mass
GenPart_pdgId
GenPart_status
GenPart_statusFlags
GenPart_genPartIdxMother

masseless quark model ???

Workflow
NanoAOD
↓
BranchReader
↓
Selector
↓
HistogramWriter
↓
ROOT histograms

--- The main hadronic tau decays

τ⁻ → π⁻ ντ

τ⁻ → K⁻ ντ

τ⁻ → π⁻ π⁰ ντ

τ⁻ → K⁻ π⁰ ντ

τ⁻ → π⁻ π⁰ π⁰ ντ

τ⁻ → K⁻ π⁰ π⁰ ντ

τ⁻ → π⁻ π⁺ π⁻ ντ

τ⁻ → K⁻ π⁺ π⁻ ντ

---

---- The main leptonic channels

τ− → e−νˉe​ντ​
τ− → μ−νˉμ​ντ​

---- The main semi leptonic channels

τ− →e−νˉe​ντ

τ− →μ−νˉμ​ντ​​

---

so we look for this channel the following channels

Z′ → τ+τ −→ (μ− (antiνμ) ​(ντ)​) (π+( anti ντ)​) checked

Z′ → τ+τ −→ (μ−νˉμ​ντ​) (K+ντ​)

Q Electric charge
B Baryon number
L Lepton number

Color charge (in strong interactions)

energy
momentum

The magnetic moment (\(\vec{\mu }\)) of a point-like Dirac particle is defined as

\_\_
mu = g( q/2m ) S

g- gyromagnetic momment
m - mass of particle
q - electric charge
s - sping ( for fermions 1/2)

magnetic moment of tau = -5.34 times 10^{-27} J/T.

electric dipole moment
dτ =1.5×10−17e cm. or e+ <---> e- this distance equals to 1.5 X 10 of power of -17 distance

Imaginary electric dipole moment it has again very small

τWEAK DIPOLE MOMENT (dwτ)τWEAK DIPOLE MOMENT (dwτ)τWEAK DIPOLE MOMEN ----- HADJIISKA TO EXPLAIN ME THIS !!!!

https://pdg.lbl.gov/2026/listings/contents_listings.html from here decays
Γ1 particle−≥0 neutrals≥0K0ντ(“1-prong”)(85.24±0.06 ) %
Γ2 particle−≥0 neutrals≥0K0Lντ(84.58±0.06 ) %
Γ3 μ− [a]νμ ντ (17.37±0.04 ) %

for electron channel from the manuel

Cut Barrel EndCap
H/E < 0.060 0.065
σiηiη < 0.011 0.031
|∆ηin| < 0.004 N/A
|∆φin| < 0.020 N/A
|1/E − 1/p| 0.013 0.013
ECAL PF Cluster Isolation < 0.160 0.120
HCAL PF Cluster Isolation < 0.120 0.120
Tracker Isolation < 0.08 0.08

Ht should be also examinated

The search is motivated by
B Meson anomalies

𝐵 → 𝐾+ 𝜈 𝜈¯

Flavour universality states that each flavour (or generation of leptons ), is equally likely to interact with a W boson.

The new ATLAS result is based on a study of its full dataset from the second run of the LHC, collected between 2015 and 2018. The analysis looked at over 100 million top-quark-pair collision events. The top quark decays promptly into a W boson and a bottom quark, so this sample provides 100 million pairs of W bosons. By counting the number of these events with two electrons (and no muon) or two muons (and no electron), physicists can test whether the W boson decays more often into an electron or a muon.

Z→e+e− Г=83.4093 MeV
Z→μ+μ− Г=83.4087 Me
Z→τ+τ− Г=83.2205 MeV

Z→e+e−,
Z→μ+μ−,
Z→τ+τ−,
Z→ννˉ,
Z→q+qˉ,

Γe​,Γμ​,Γτ​,Γν​,Γq​,…

ΓZ ​≃2.5 GeV = 2500 МеV
ГZtau/tau = 83 MeV

those are on tree level ( meaning from Quantum field theory we cound only first order processes without loop)

One of the decayse of B mesons are to D meson and tau and tau neutrino

B→Dτντ​

B→Deνe​

B→Dμνμ​​

We expecte each of this to be euqally distributted the

R(D)=Γ(B→Dτντ)/Γ(B→Dℓνℓ) we expect this for instance to be close to some number

SM predictions is due to LFU R(D)SM​≈0.294

but experimmentally we observe a value

R(D)exp ≈ 0.347
​

| Quantity                   | What it compares/measures                       |                  SM |         Experiment |
| -------------------------- | ----------------------------------------------- | ------------------: | -----------------: |
| (R(D))                     | (B\to D\tau\nu) vs (B\to D\ell\nu)              |     (0.299\pm0.004) |    (0.342\pm0.026) |
| (R(D^\*))                  | (B\to D^_\tau\nu) vs (B\to D^_\ell\nu)          |     (0.257\pm0.005) |    (0.287\pm0.012) |
| (R(J/\psi))                | (B_c\to J/\psi\tau\nu) vs (B_c\to J/\psi\mu\nu) |     (0.258\pm0.004) |      (0.52\pm0.20) |
| (BR(B^+\to K^+\nu\bar\nu)) | Fraction of (B^+) decays into (K^+\nu\bar\nu)   | (4.29\times10^{-6}) | (2.3\times10^{-5}) |

the B meson anomalies

predicts

R(D),R(D
∗
),R(J/ψ),BR(B→Kν
ν
ˉ
)

↓

experiments measure them

↓

some measurements have shown deviations

↓

physicists ask whether

SM+new interaction
​

fits everything better.

Candidate new interactions include:

Z
′
​

W
′
​

leptoquark
​

new scalars
​

Table 20: Electron ID Selections.
Cut Barrel EndCap
H/E < 0.060 0.065
σiηiη < 0.011 0.031
|∆ηin| < 0.004 N/A
|∆φin| < 0.020 N/A
|1/E − 1/p| 0.013 0.013
ECAL PF Cluster Isolation < 0.160 0.120
HCAL PF Cluster Isolation < 0.120 0.120
Tracker Isolation < 0.08 0.08

https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2

Table 21: µ Identification
Cut
recoMu.isGlobalMuon()
muon::isPFMuon()
recoMu.globalTrack()-> normalizedChi2()< 10
recoMu.globalTrack()-> hitPattern().numberOfValidMuonHits()> 0
recoMu.numberOfMatchedStations()> 1
fabs(recoMu.muonBestTrack()-> dxy(vertex-> position()))< 0.2
fabs(recoMu.muonBestTrack()-> dz(vertex-> position()))< 0.5
recoMu.innerTrack()-> hitPattern().numberOfValidPixelHits()> 0
recoMu.innerTrack()-> hitPattern().trackerLayersWithMeasurement()> 5

Table 22: Reconstructed Tau Decay Modes
HPS Tau Decay Modes
Single Charged Hadron + Zero Strip
Single Charged Hadron + One Strip
Single Charged Hadron + Two Strips
Two Charged Hadrons
Three Hadrons

Table 23: τh
ID criteria.
TauIDAlgorithm TauIdDeepTau2017v2p1
Isolation Tight
Prongs 1 or 3 hp
|η(τh
)| < 2.1
Discriminator against µ Tight (for all channels)
Discriminator against e loose (τhτh
), Medium (eτh and µτh
)

the following: ∆pT
(τ`/h
, τh
490 ),
cos[∆φ(τ`/h
, τh
)], mreco(τ`/h
, τh
), and cos{∆φ[pT
(τh
), E
miss
T
491 ]}.

N
signal
​

=N
observed
​

−N
background
​

    ​

So if you don't know the QCD background accurately, you can't reliably determine whether you have a signal.

Muons are measured in the pseudorapidity range |𝜂| <2.4,
To suppress muons from hadron decays and other nonprompt sources, an additional requirement is imposed on the relative isolation, defined as the ratio of the energy from neutral and charged PF candidates in a cone of Δ⁢𝑅≡√(Δ⁢𝜂)2+(Δ⁢𝜙)2<0.4
Electrons are reconstructed using energy deposits in the ECAL detector that have a matching track in (𝜂,𝜙) space in the silicon tracking system, within |𝜂| <2.4. Electron candidates that fall in the transition region between the barrel and the end cap of the CMS detector, located at 1.44 <|𝜂| <1.57,
To identify electrons, we use the high-energy electron pairs (HEEP) ID for the selection of signal events;
Events are required to have one 𝜏h candidate accompanied by a 𝜇, 𝑒, or second 𝜏h candidate of opposite-sign (OS) charge, all within |𝜂| <2.1. To avoid possible overlaps among the three channels, we reject events containing additional lepton candidates of any flavor beyond the selected OS lepton candidate pair. Specifically, the additional lepton can be a 𝜇 or 𝑒 candidate with 𝑝T>10  GeV and |𝜂| <2.1
𝑍′ bosons through quark-antiquark annihilation, events from vector boson fusion are suppressed by vetoing events with a pair of jets 𝑗1,2, each of which passes 𝑝T >30  GeV and |𝜂| <4.7, with a pseudorapidity separation |Δ⁢𝜂⁡(𝑗1,𝑗2)|>4.2 and an invariant mass above 500 GeV.

A. The 𝜏𝜇⁢𝜏h SR
The 𝜏𝜇⁢𝜏h events are required to satisfy the single-muon trigger, whose efficiency exceeds 90% over the full 𝜂 range for the selected muon candidates with 𝑝T>35  GeV. Muons are also required to be well isolated and to pass the tight ID criteria defined in Ref. [38]. The 𝜏h candidate is required to satisfy 𝑝T >20  GeV. The two candidates are required to be well separated in (𝜂,𝜙) space by the criterion Δ⁢𝑅≡√(Δ⁢𝜙⁡(𝜏𝜇,𝜏h))2+(Δ⁢𝜂⁡(𝜏𝜇,𝜏h))2>0.3. We reject events containing 𝑏 jet candidates with 𝑝T>30  GeV and |𝜂| <2.4. Events from DY, 𝑊 +jets, and QCD multijet production are significantly suppressed by requiring the 𝜏𝜇 and 𝜏h candidates to have a large azimuthal separation given by cos⁡Δ⁢𝜙⁡(𝜏𝜇,𝜏h)<−0.98. In addition, we require that
→
𝑝
miss
T lie in the direction opposite that of the 𝜏h or of the 𝜏𝜇 candidate with the highest 𝑝T (leading lepton, ℓl), by requiring cos⁡Δ⁢𝜙⁡(𝑝miss
T,ℓl)<−0.95. This requirement further reduces the contribution of 𝑊 +jets and QCD multijet events. The transverse mass of the leading lepton and
→
𝑝
miss
T, 𝑚T⁡(𝑝miss
T,ℓl)=√𝑝miss
T⁡𝑝T⁡(ℓl)⁢(1−cos⁡(Δ⁢𝜙⁡(𝑝miss
T,ℓl))), is required to be greater than 150 GeV for further suppression of 𝑊 +jets events.

B. The 𝜏𝑒⁢𝜏h SR
Similar selection criteria are applied to the 𝜏𝑒⁢𝜏h channel, with the following differences. We require these events to satisfy a single-electron trigger that has an efficiency above 90% for electrons after the requirement 𝑝T >35⁢(55)  GeV for data collected in 2016 (2017–2018).

C. The 𝜏h⁢𝜏h SR
For the 𝜏h⁢𝜏h channel we select events that satisfy a dedicated trigger [29] with at least two 𝜏h candidates. We require each 𝜏h candidate to have 𝑝T>70  GeV, ensuring a trigger efficiency of at least 90%. The two 𝜏h candidates must be separated by Δ⁢𝑅 >0.3. Events with any 𝑏 jet candidate having 𝑝T>30  GeV and |𝜂| <2.4 are removed, to suppress top quark backgrounds. To reduce the contribution of DY events, the reconstructed mass of the 𝜏h pair is required to exceed 100 GeV. To discriminate against 𝑊 +jets and QCD multijet events, we require the two 𝜏h candidates to have a large azimuthal separation, cos⁡Δ⁢𝜙⁡(𝜏1
h,𝜏2
h)<−0.95, while the
→
𝑝
miss
T and the leading- 𝑝T 𝜏h candidate 𝜏l
h are required to satisfy |cos⁡Δ⁢𝜙⁡(𝑝miss
T,𝜏l
h)|>0.9. Further suppression of the contribution of QCD multijet events is achieved with a requirement 𝑝miss
T>30  GeV.

how much tau leptons in one event
distrubution it Pt
how much are hadronic decayed
how much are leptonic decayed
how much are muonic channel
how much electronic channel

in each event

one prong two prong to know more

stacked plots root or overlayed

LHC Run 3: DeepTau, PNet, and UParT the Algo used for rectostruntict tao leptons

## Hadronically decayed tau selection

Used in `main.C` as `hadronicTauCuts["tauDecayedHadronically"]`.

| Variable      | Requirement         |
| ------------- | ------------------- |
| pT(τ)         | > 70 GeV            |
| \|η(τ)\|      | < 2.1               |
| \|dz(τ)\|     | < 0.2 cm            |
| DeepTau VSjet | ≥ 6 (Tight)         |
| DeepTau VSmu  | ≥ 4 (Tight)         |
| DeepTau VSe   | ≥ 5 (Medium)        |
| decayMode     | ∈ {0, 1, 2, 10, 11} |

### Why each cut is there

**pT(τ) > 70 GeV**
A trigger requirement, not a tau-physics one. The dedicated di-tau trigger
only reaches ~90% efficiency above 70 GeV (arXiv:2412.04357, Sec. 6.3), so
lower-pT candidates aren't reliably recorded in real data. It also rejects
much of the QCD-jet background, whose steeply falling spectrum piles up
near threshold.

**|η(τ)| < 2.1**
Keeps candidates inside the region where DeepTau's jet/e/μ rejection is
reliable. Tighter than HPS's raw |η| < 2.3 fiducial reach
(CMS-AN-2020-134, Table 56). pg 60

**|dz(τ)| < 0.2 cm**
Vertex association: requires the tau's leading track to originate close to
the event's primary vertex along the beam axis, rejecting taus
reconstructed from pileup (a separate, simultaneous pp collision).

**DeepTau VSjet ≥ 6 (Tight)**
The main purity driver. HPS builds a tau-shaped candidate out of any
1-or-3-track jet fragment; without this cut, the tau collection is
dominated by ordinary QCD jets misreconstructed as taus (jet→τ_h fake rate
~0.6% at this WP vs. ~60% genuine efficiency, per the paper).

**DeepTau VSmu ≥ 4 (Tight)**
Rejects real muons that a track plus a minimal calorimeter deposit can
fake as a 1-prong tau candidate.

**DeepTau VSe ≥ 5 (Medium)**
Rejects real electrons, whose ECAL shower plus a track can fake a
1-prong(+strip) tau candidate. Looser than VSjet/VSmu since electron fakes
are a smaller background here (CMS Sec. 5.2 specifies Medium for this WP
across channels).

**decayMode ∈ {0, 1, 2, 10, 11}**
Restricts to physically real topologies: 1-prong (0, 1, 2: π/K ± up to
2π⁰) and 3-prong (10, 11: 3π/K ± optional π⁰). Excludes modes 5/6
(2-prong), which the Tau POG documents as reconstruction failures rather
than real decays.

Cross-checked against: arXiv:2412.04357 / PRD 111, 112004 (Sec. 6.3),
CMS-AN-2020-134 (Tables 56/57), and the CMS Tau POG Run-3 ID
recommendations page.

### Does this "guarantee" a tau decayed hadronically?

No. It's a purity-maximizing selection, not a certainty:

- It only uses reconstructed detector quantities — the generator-level
  truth (`GenPart_pdgId`/`status`) isn't checked at all.
- Even at VSjet Tight, ~0.6% of real jets still fake a τ_h candidate.
  Given how much larger the QCD jet cross section is than the signal,
  that small fake rate can still be a real background — exactly why CMS
  builds a dedicated data-driven QCD estimate (the ABCD method) rather
  than relying on the cut alone.
- What it does deliver is high purity — a candidate passing all seven
  rows is very likely (order 90%+, depending on process and pT) a genuine
  hadronic tau, not a jet/electron/muon — good enough to build an
  analysis on, the same standard CMS itself uses.

  ​

  ​/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD

  data_tier_name:"NANOAOD"
  modification_time:1741034371
  modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
  creation_date:1737132344
  dataset_id:15216132
  name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
  physics_group_name:"NoGroup"
  primary_dataset.name:"Tau"
  xtcrosssection:0
  primary_ds_name:"Tau"
  create_by:"WMAgent"
  dataset_access_type:"VALID"
  status:"VALID"
  acquisition_era_name:"Run2024C"
  last_modification_date:1741034371
  processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
  prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
  creation_time:1737132344
  created_by:"WMAgent"
  datatype:"data"
  primary_ds_type:"data"
  last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
  processing_version:1

Dataset: /Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD
Dataset size: 77820791067 (77.8GB) Number of blocks: 15 Number of events: 50839148 Number of files: 74 Dataset size: 7.7820791067e+10 (77.8GB) Creation time: 2025-01-17 16:45:44 Cross section: 0 Physics group: NoGroup Status: VALID Type: data
Release, Blocks, Files, Runs, Configs, Parents, Children, Sites, Origin sites, Physics Groups XSDB Sources: dbs3rucio hide
DAS service: dbs3 DAS api: filesummaries
median_cdate:1737309579
nfiles:74
num_lumi:24600
name:[]interface {}{"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"}
size:77820791067
num_file:74
nblocks:15
nevents:50839148
median_ldate:1737309579
nlumis:24600
max_ldate:1738017634

DAS service: rucio DAS api: dataset4dataset
states:mongo.DASRecord{"T1_IT_CNAF_Tape":"AVAILABLE",
"T1_UK_RAL_Disk":"AVAILABLE",
"T1_US_FNAL_Disk":"AVAILABLE",
"T1_US_FNAL_Tape_Test":"AVAILABLE",
"T2_FR_GRIF":"AVAILABLE",
"T2_KR_KISTI":"AVAILABLE",
"T2_UA_KIPT":"AVAILABLE",
"T2_UK_London_IC":"AVAILABLE",
"T2_US_Caltech":"AVAILABLE"}
rses:mongo.DASRecord{"T1_IT_CNAF_Tape":[]interface {}{},
"T1_UK_RAL_Disk":[]interface {}{},
"T1_US_FNAL_Disk":[]interface {}{},
"T1_US_FNAL_Tape_Test":[]interface {}{},
"T2_FR_GRIF":[]interface {}{},
"T2_KR_KISTI":[]interface {}{},
"T2_UA_KIPT":[]interface {}{},
"T2_UK_London_IC":[]interface {}{},
"T2_US_Caltech":[]interface {}{}}
bytes:77820791067
available_bytes:77820791067
length:74
nblocks:15
available_length:74
size:77820791067
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"

DAS service: dbs3 DAS api: dataset_info
modification_time:1741034371
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
xtcrosssection:0
create_by:"WMAgent"
data_tier_name:"NANOAOD"
last_modification_date:1741034371
dataset_access_type:"VALID"
primary_ds_type:"data"
acquisition_era_name:"Run2024C"
processing_version:1
status:"VALID"
modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
created_by:"WMAgent"
physics_group_name:"NoGroup"
datatype:"data"
creation_time:1737132344
dataset_id:15216132
creation_date:1737132344
primary_ds_name:"Tau"
primary_dataset.name:"Tau"

DAS service: dbs3 DAS api: dataset_info
modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
data_tier_name:"NANOAOD"
dataset_access_type:"VALID"
status:"VALID"
create_by:"WMAgent"
processing_version:1
acquisition_era_name:"Run2024C"
xtcrosssection:0
creation_date:1737132344
primary_dataset.name:"Tau"
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
last_modification_date:1741034371
primary_ds_name:"Tau"
created_by:"WMAgent"
datatype:"data"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
dataset_id:15216132
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
primary_ds_type:"data"
modification_time:1741034371
physics_group_name:"NoGroup"
creation_time:1737132344

DAS service: dbs3 DAS api: datasetlist
dataset_id:15216132
dataset_access_type:"VALID"
primary_ds_type:"data"
data_tier_name:"NANOAOD"
creation_date:1737132344
acquisition_era_name:"Run2024C"
physics_group_name:"NoGroup"
primary_ds_name:"Tau"
processing_version:1
last_modification_date:1741034371
prep_id:"ReReco-Run2024C-Tau-2024CDEReprocessing-00001"
xtcrosssection:0
last_modified_by:"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=cmsunified/CN=658085/CN=Robot: CMS Unified account"
create_by:"WMAgent"
processed_ds_name:"Run2024C-2024CDEReprocessing-v1"
name:"/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"

dasgoclient -query="dataset=/Tau/Run2024C-2024CDEReprocessing-v1/NANOAOD"

GenPart is in my case for MC in this case LHE input from MGraph5 provided to Pythia for further hadroniztion and further decay and adding stuff or something like that Z -> tau tau - > more channels

https://arxiv.org/abs/2606.17569

dasgoclient -query="file dataset=/Tau/Run2018A-Nano25Oct2019-v1/NANOAOD"

/eos/cms/store/data/Run2018A/Tau/NANOAOD/Nano25Oct2019-v1/230000/02785FC8-0354-A04D-8996-3AD8D18DCF7A.root

most probably tau_mass is the mass of reconstructed tau by alhorithms for its recconstruction and it varies till 1.788 GeV which the real value

root -l -b -q TauVisibleMassCheck.C

root -l -b -q TauVisibleMassFormula.C

root -l -b -q TauVisibleMassPtEtaPhi.C

        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/5213f2f4-68ec-4738-9cf9-88b5d7474a3e.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e727db27-b76b-4183-8b35-a6fe52a4cd86.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/008ca5f3-4b34-4e83-a897-fc34bb87343e.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/639c0075-3dce-41c7-843f-0c948d77d07c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/c3be4954-8bbb-40a3-8a2b-6c5ca249b5d3.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b203470e-65a4-408c-ad56-b33bd78da615.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/ce7c3bd1-8426-45ae-8e41-e287be9d306f.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/7a4a144f-efb6-4d06-8ccf-014c9dde3c35.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b064c16b-2b75-45b5-ab56-982074f0cf87.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/db16f8c4-da36-499e-92cb-1dc63df8f99c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/8cd8fe52-2b8d-4914-b08c-d2809313687d.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6da3a189-910e-4810-9a40-84cde5ced5c4.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/372b8298-7c6e-4f2c-8f0b-8b1c5d3e0445.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/06e27c51-bd3a-482f-9933-889a454e03fe.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/4029594a-fe25-498a-b67b-961bf6c830fa.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6b9ce373-8d81-4236-a473-1b16d8ff3cb9.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3c9cd887-453b-4610-a27b-799d30393af3.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/232998a3-e6ae-48a6-a9d8-f85e21e0e0f8.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/4e33a138-0f1e-4b37-b830-ce155616ff97.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/5db80087-a1f8-44ab-80e9-07aa66c8b31c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/225d069a-3f6f-4c07-a063-4a547aed20cc.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fca85820-ec7c-47f5-ac0c-fe10c36ceb4b.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3d9a88bf-6c26-49f4-a99f-8a90306ccd24.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/1b62f6a3-7479-46ad-a03e-5f253c505666.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/246b69a4-e4a5-43f7-bcf4-44980a2fbd5c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/179455b3-0e99-46ec-820a-ee459fd92a4c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/ec0b8891-960b-4fcf-8457-0cbe47f00e93.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fcc1ed71-7505-4878-8504-6511ef646505.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/b9881b4b-ac7c-44ea-8b41-ddebf7763a5c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/858431e5-2c3f-4550-919f-6b05c66c962a.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/e3c95d01-59e6-4b0c-a490-e975581a4a64.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/3fc6b439-5aba-4223-959d-35f367b8ac0c.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/85a75b9d-e7cf-432a-8b88-089f36eca845.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/a0cede5b-1d6b-4f0a-896c-43cd4cd7b7f6.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/a6860b04-39b6-47d0-a840-5a220deea206.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/84b616f0-0ef5-453b-9939-4ca3e9c65fec.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/bd30ca45-6a76-4762-9161-1ae5d2b66765.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/93a2aef6-6ca9-41b2-afa6-f133033cbb89.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/91360ec3-338d-410e-a0d9-931265420326.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/7c9625a5-2703-49bd-821b-2c8a7e13ebcc.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/fea9cb8a-dc5a-4eed-b679-70a50e3757b7.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/6d093332-f256-4c51-a70c-b74b273e3462.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cebd697a-93e9-44fc-aa77-4341e06fd818.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/0fac4495-aedc-4352-8d51-e63c30df57c2.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/873737d7-47eb-4463-a878-eb1be19991ef.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/40fd4f68-40be-49d5-bafd-6afd7d871f02.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/d1d8adc5-0d71-4352-a6fd-09237ba20940.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/f2724d44-d212-4573-a89b-b58af07da313.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/96a28fdb-28fd-4803-8830-af3080c6dc3b.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cefe0cd0-2cb4-4e57-856a-96b73120ad42.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/15b9ecc2-541e-4a82-9651-6bbf973c7f11.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/0019cbeb-f99c-4a57-a911-5f72f5d9de28.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/17bbd269-64d3-450f-ac60-98bc1eb9efe3.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/8aba0f8c-1304-4f17-bfab-cdbd05f6d465.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/870a8b9c-853e-4f80-b289-e869a82a02ef.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/10132535-1c6c-44b8-ae7b-4233289e6e88.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cec64127-dbc0-4332-b6b2-d5d9635154fd.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/2086bc7e-93fd-43a0-b768-206a78dc7688.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/cb3f442a-0549-47cb-8f2a-ed8542989887.root",
        "root://cms-xrd-global.cern.ch//store/data/Run2024D/Tau/NANOAOD/MINIv6NANOv15-v1/120000/d9e19696-586f-4161-84fc-b0932c35f5ae.root"

TODO to find the json file with good lumisections
