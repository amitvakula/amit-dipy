
# coding: utf-8

# In[1]:

import multiprocessing


# In[2]:

"""
==============================
Introduction to Basic Tracking
==============================

Local fiber tracking is an approach used to model white matter fibers by
creating streamlines from local directional information. The idea is as
follows: if the local directionality of a tract/pathway segment is known, one
can integrate along those directions to build a complete representation of that
structure. Local fiber tracking is widely used in the field of diffusion MRI
because it is simple and robust.

In order to perform local fiber tracking, three things are needed: 1) A method
for getting directions from a diffusion data set. 2) A method for identifying
different tissue types within the data set. 3) A set of seeds from which to
begin tracking.  This example shows how to combine the 3 parts described above
to create a tractography reconstruction from a diffusion data set.
"""

"""
To begin, let's load an example HARDI data set from Stanford. If you have
not already downloaded this data set, the first time you run this example you
will need to be connected to the internet and this dataset will be downloaded
to your computer.
"""


# In[3]:

from dipy.data import read_stanford_labels

hardi_img, gtab, labels_img = read_stanford_labels()
data = hardi_img.get_data()
labels = labels_img.get_data()
affine = hardi_img.get_affine()


# In[4]:

# metrics for stanford data
#print type(data)
#print data.ndim
#print data.shape
#
#print type(labels)
#print labels.ndim
#print labels.shape


# In[5]:

# this creates a mask which zeros (?) out all tissue which doesn't have label 1 or 2 (TODO: what is 1 or 2?)
white_matter = (labels == 1) | (labels == 2)


# In[6]:

from dipy.reconst.shm import CsaOdfModel
from dipy.data import default_sphere
from dipy.direction import peaks_from_model

csa_model = CsaOdfModel(gtab, sh_order=6)
csa_peaks = peaks_from_model(csa_model, data, default_sphere,
                             relative_peak_threshold=.8,
                             min_separation_angle=45,
                             mask=white_matter)


# In[7]:

from dipy.tracking.local import ThresholdTissueClassifier

classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)


# In[8]:

from dipy.tracking import utils
from dipy.tracking.local import LocalTracking, OptimizedLocalTracking
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors
import time

seed_mask = labels == 2
seeds = utils.seeds_from_mask(seed_mask, density=[2, 2, 2], affine=affine)
#print type(seeds)
#print len(seeds)
#print seeds.shape
#print seeds[0]


# In[9]:

# Initialization of LocalTracking. The computation happens in the next step.
# TODO: determine how large the data set is and what method LocalTracking is using  
start = time.time()

streamlines = LocalTracking(csa_peaks, classifier, seeds, affine, step_size=.5)
#mid = time.time()
# Compute streamlines and store as a list.
streamlines = list(streamlines)
end = time.time()
print('total time to do streamline computation with naiive class: ' + str(end-start))


# In[10]:

# Initialization of LocalTracking. The computation happens in the next step.
# TODO: determine how large the data set is and what method LocalTracking is using  
start = time.time()

#streamlines = LocalTracking(csa_peaks, classifier, seeds, affine, step_size=.5)
#mid = time.time()
# Compute streamlines and store as a list.
#streamlines = list(streamlines)

streamlines = []
for seed in seeds:
    seed_lst = []
    seed_lst.append(seed)
    streamlines.append(list(LocalTracking(csa_peaks, classifier, seed_lst, affine, step_size=.5)))
end = time.time()

"""
# Prepare the display objects.
color = line_colors(streamlines)
streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

# Create the 3d display.
r = fvtk.ren()
fvtk.add(r, streamlines_actor)

# Save still images for this static example. Or for interactivity use fvtk.show

# use the code snippet below if you want to save the image
fvtk.record(r, n_frames=5, out_path='/Users/support/Documents/code/dipy_optimization/deterministic2.png',
            size=(800, 800))
# if you want to see the image now use the code below
#fvtk.show(r)

"""

print('total time to do streamline computation with naiive for loop: ' + str(end-start))


# In[ ]:



# Initialization of LocalTracking. The computation happens in the next step.
# TODO: determine how large the data set is and what method LocalTracking is using  
start = time.time()

op_tracking = OptimizedLocalTracking(csa_peaks, classifier, seeds, affine, step_size=.5)
#mid = time.time()
# Compute streamlines and store as a list.
op_streamlines = op_tracking.compute_all_streamlines()

end = time.time()

"""
streamlines = []
for seed in seeds:
    seed_lst = []
    seed_lst.append(seed)
    streamlines.append(list(LocalTracking(csa_peaks, classifier, seed_lst, affine, step_size=.5)))
end = time.time()
"""

"""
# Prepare the display objects.
color = line_colors(streamlines)
streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

# Create the 3d display.
r = fvtk.ren()
fvtk.add(r, streamlines_actor)

# Save still images for this static example. Or for interactivity use fvtk.show

# use the code snippet below if you want to save the image
fvtk.record(r, n_frames=5, out_path='/Users/support/Documents/code/dipy_optimization/deterministic2.png',
            size=(800, 800))
# if you want to see the image now use the code below
#fvtk.show(r)

"""

print('total time to do streamline computation with optimized class: ' + str(end-start))


# In[16]:

import os

#class DummySeed():
#    def __init__(self, sd):
#        self.seed = sd
#dummy_seeds = list(DummySeed(s) for s in seeds)


def func(seed):
#    info()
    seed_lst = []
    seed_lst.append(seed)
    return list(LocalTracking(csa_peaks, classifier, seed_lst, affine, step_size=.5))

#def info():
#    print 'process id:', os.getpid()
 

#print len(seeds)
#print multiprocessing.cpu_count()

from dipy.tracking.local import LocalTracking
from dipy.viz import fvtk
from dipy.viz.colormap import line_colors
import time

# Initialization of LocalTracking. The computation happens in the next step.
# TODO: determine how large the data set is and what method LocalTracking is using
# Compute streamlines and store as a list.
start = time.time()

p = multiprocessing.Pool(multiprocessing.cpu_count())
results = p.map(func, seeds)

end = time.time()


print('total time to do streamline computation with optimized for loop: ' + str(end-start))


""""
for item in results:
    streamlines.extend(item)


# Prepare the display objects.
color = line_colors(streamlines)
streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

# Create the 3d display.
r = fvtk.ren()
fvtk.add(r, streamlines_actor)

# Save still images for this static example. Or for interactivity use fvtk.show

# use the code snippet below if you want to save the image
fvtk.record(r, n_frames=1, out_path='/Users/support/Documents/code/dipy_optimization/deterministic.png',
            size=(800, 800))
# if you want to see the image now use the code below
#fvtk.show(r)
"""


# In[ ]:

print len(streamlines)
print len(results)
print len(streamlines[0])
print len(results[0])
for j in range(0, len(streamlines)):
    for i in range(0,len(streamlines[j])):
        print streamlines[j][i]==results[j][i]


# In[ ]:

from dipy.io.trackvis import save_trk
save_trk("CSA_detr.trk", streamlines, affine, labels.shape)


# In[ ]:




# In[ ]:

from dipy.reconst.csdeconv import (ConstrainedSphericalDeconvModel,
                                   auto_response)

response, ratio = auto_response(gtab, data, roi_radius=10, fa_thr=0.7)
csd_model = ConstrainedSphericalDeconvModel(gtab, response, sh_order=6)
csd_fit = csd_model.fit(data, mask=white_matter)


# In[ ]:

from dipy.direction import ProbabilisticDirectionGetter

prob_dg = ProbabilisticDirectionGetter.from_shcoeff(csd_fit.shm_coeff,
                                                    max_angle=30.,
                                                    sphere=default_sphere)


# In[ ]:

classifier = ThresholdTissueClassifier(csa_peaks.gfa, .25)


# In[ ]:

streamlines = LocalTracking(prob_dg, classifier, seeds, affine,
                            step_size=.5, max_cross=1)

# Compute streamlines and store as a list.
streamlines = list(streamlines)

# Prepare the display objects.
color = line_colors(streamlines)
streamlines_actor = fvtk.line(streamlines, line_colors(streamlines))

# Create the 3d display.
r = fvtk.ren()
fvtk.add(r, streamlines_actor)

# Save still images for this static example.
fvtk.record(r, n_frames=1, out_path='probabilistic.png',
            size=(800, 800))


# In[ ]:

save_trk("CSD_prob.trk", streamlines, affine, labels.shape)

