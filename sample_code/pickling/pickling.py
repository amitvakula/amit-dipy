# -*- coding: utf-8 -*-
"""
Created on Thu May 28 12:19:33 2015

@author: support
"""

import pickle

try: 
    import dipy
except:
    import sys
    sys.path.insert(1, "/Users/support/Documents/code/dipy_optimization/dipy")
    import dipy

item_to_pickle = "Hello! I'm about to be pickled!"

with open("a_pickled_string.pickle","w") as f:
    pickle.dump(item_to_pickle, f)
    
    
from dipy.data import read_stanford_labels
hardi_img, gtab, labels_img = read_stanford_labels()
data = hardi_img.get_data()
labels = labels_img.get_data()
affine = hardi_img.get_affine()
# this creates a mask which zeros (?) out all tissue which doesn't have label 1 or 2 (TODO: what is 1 or 2?)
white_matter = (labels == 1) | (labels == 2)
from dipy.reconst.shm import CsaOdfModel
from dipy.data import default_sphere
from dipy.direction import peaks_from_model

csa_model = CsaOdfModel(gtab, sh_order=6)
csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                             relative_peak_threshold=.8,
                             min_separation_angle=45,
                             mask=white_matter)


from dipy.tracking.local import ThresholdTissueClassifier

classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)


from dipy.tracking import utils
from dipy.tracking.local import OptimizedLocalTracking


seed_mask = labels == 2
seeds = utils.seeds_from_mask(seed_mask, density=[2, 2, 2], affine=affine)

op_tracking = OptimizedLocalTracking(csa_peaks, classifier, seeds, affine, step_size=.5)

"""
import copy_reg
def pickle_tissue_classifer(classifer_object):
    return (ThresholdTissueClassifier, (classifer_object, classifer_object.metric_map, classifer_object.threshold))
copy_reg.pickle(ThresholdTissueClassifier, pickle_tissue_classifer)
"""

m = classifier.get_metric_map()

with open("active_tissue_classifier_instance.pickle","w") as f:
    pickle.dump(op_tracking.tissue_classifier, f)

with open("op_local_tracking_instance.pickle","w") as f:
    pickle.dump(op_tracking, f)
