import logging

import awkward as ak

logger = logging.getLogger(__name__)


##we will provide here loaded events from nanoAOD
def get_tau_collection(events):
    """Return the Tau collection after validating that it exists."""
    if events is None:
        error_msg = "\n[ERROR] Cannot read Tau from a None events object\n"
        logger.error(error_msg)
        raise ValueError(error_msg)
    

    if "Tau" not in events.fields:
        available = list(events.fields)
        error_msg = (
            f"\n[ERROR] Tau not found. Available: {available}\n"
            "Ensure the input NanoAOD file contains reconstructed taus.\n"
        )
        logger.error(error_msg)
        raise AttributeError(error_msg)

    return events.Tau

# getting only taus deepTauCollection
def get_deep_taus(taus):

   """Return the DeepTau collection after validating that it exists."""
   deepTauVSe = taus.idDeepTau2018v2p5VSe
   first_ten_deepTauVSe = deepTauVSe[:10]
   #    for i, value in enumerate(first_ten_deepTauVSe):
   #        print(f"DeepTauVSe[{i}] = {value.tolist()}")
   return deepTauVSe

def get_tresholded_deep_taus(deepTauVSe,taus, threshold=1):
    """Select good DeepTau taus based on a threshold."""
    good_deep_taus_mask = deepTauVSe >= threshold
    good_deep_taus = taus[good_deep_taus_mask]

    n_good_deep_taus = ak.sum(good_deep_taus_mask)
    if n_good_deep_taus == 0:
        logger.warning("⚠ Warning: No events passed DeepTau selection!")
    
    return good_deep_taus


deep_taus_tresholds = {
    "VVVLoose": 1,
    "VVLoose": 2,
    "VLoose": 3,
    "Loose": 4,
    "Medium": 5,
    "Tight": 6,
    "VTight": 7,
    "VVTight": 8,
}




