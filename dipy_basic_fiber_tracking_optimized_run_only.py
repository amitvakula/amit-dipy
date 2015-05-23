
# coding: utf-8

# In[1]:



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


