import numpy as np
import tqdm
import spikeinterface.full as si
import voltron

def compute_stability(sorting):
    sr = sorting.get_sampling_frequency()
    cluster_ids = sorting.get_unit_ids()

    stabilities = {}
    for cluster_id in cluster_ids:
        st = sorting.get_unit_spike_train(cluster_id)
        st = st / sr
    
        t = np.arange(0, st[-1], 10)

        binned = voltron.binspikes(st, t)
        stabilities[cluster_id] = binned
    return stabilities


def compute_autocorrelation(sorting):
    sr = sorting.get_sampling_frequency()
    cluster_ids = sorting.get_unit_ids()

    autocorrs = {}
    for cluster_id in tqdm.tqdm(cluster_ids):
        st = sorting.get_unit_spike_train(cluster_id)
        st = st / sr
        
        t = np.arange(0, st[-1], 0.001)

        binned = voltron.binspikes(st, t)
        autocorr = voltron.autocorrelation(binned, 100)
        autocorrs[cluster_id] = autocorr
    return autocorrs
