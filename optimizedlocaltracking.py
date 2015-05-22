import numpy as np

from .localtrack import local_tracker
from dipy.align import Bunch
from dipy.tracking import utils



import os
import sys

import multiprocessing

"""
# Configure the environment
if 'SPARK_HOME' not in os.environ:
    os.environ['SPARK_HOME'] = '/Users/support/Documents/code/dependencies/spark' # NOTE: set you spark home path here

# Create a variable for our root path
SPARK_HOME = os.environ['SPARK_HOME']

# Add the PySpark/py4j to the Python Path
sys.path.insert(1, os.path.join(SPARK_HOME, "python", "build"))
sys.path.insert(1, os.path.join(SPARK_HOME, "python"))

from pyspark import  SparkContext
# Note: you can only run this code once before getting an error if you don't run sc.stop()
sc = SparkContext( 'local', 'pyspark')
"""

# enum TissueClass (tissue_classifier.pxd) is not accessible
# from here. To be changed when minimal cython version > 0.21.
# cython 0.21 - cpdef enum to export values into Python-level namespace
# https://github.com/cython/cython/commit/50133b5a91eea348eddaaad22a606a7fa1c7c457
TissueTypes = Bunch(OUTSIDEIMAGE=-1, INVALIDPOINT=0, TRACKPOINT=1, ENDPOINT=2)

def top_level_hack(O):
    f = O.f
    i = O.i
    return f(i)

class DummyClass():
    def __init__(self, func, inputs):
        self.f = func
        self.i = inputs

class OptimizedLocalTracking(object):
    """A streamline generator for local tracking methods"""
    """ 
    This class has the same functionality as LocakTracking except 
    it has an additional method which generates the streamlines in 
    bulk using pyspark
    """

    @staticmethod
    def _get_voxel_size(affine):
        """Computes the voxel sizes of an image from the affine.

        Checks that the affine does not have any shear because local_tracker
        assumes that the data is sampled on a regular grid.

        """
        lin = affine[:3, :3]
        dotlin = np.dot(lin.T, lin)
        # Check that the affine is well behaved
        if not np.allclose(np.triu(dotlin, 1), 0.):
            msg = ("The affine provided seems to contain shearing, data must "
                   "be acquired or interpolated on a regular grid to be used "
                   "with `LocalTracking`.")
            raise ValueError(msg)
        return np.sqrt(dotlin.diagonal())

    def __init__(self, direction_getter, tissue_classifier, seeds, affine,
                 step_size, max_cross=None, maxlen=500, fixedstep=True,
                 return_all=True):
        """Creates streamlines by using local fiber-tracking.

        Parameters
        ----------
        direction_getter : instance of DirectionGetter
            Used to get directions for fiber tracking.
        tissue_classifier : instance of TissueClassifier
            Identifies endpoints and invalid points to inform tracking.
        seeds : array (N, 3)
            Points to seed the tracking. Seed points should be given in point
            space of the track (see ``affine``).
        affine : array (4, 4)
            Coordinate space for the streamline point with respect to voxel
            indices of input data. This affine can contain scaling, rotational,
            and translational components but should not contain any shearing.
            An identity matrix can be used to generate streamlines in "voxel
            coordinates" as long as isotropic voxels were used to acquire the
            data.
        step_size : float
            Step size used for tracking.
        max_cross : int or None
            The maximum number of direction to track from each seed in crossing
            voxels. By default all initial directions are tracked.
        maxlen : int
            Maximum number of steps to track from seed. Used to prevent
            infinite loops.
        fixedstep : bool
            If true, a fixed stepsize is used, otherwise a variable step size
            is used.
        return_all : bool
            If true, return all generated streamlines, otherwise only
            streamlines reaching end points or exiting the image.
        """
        self.direction_getter = direction_getter
        self.tissue_classifier = tissue_classifier
        self.seeds = seeds
        if affine.shape != (4, 4):
            raise ValueError("affine should be a (4, 4) array.")
        self.affine = affine
        self._voxel_size = self._get_voxel_size(affine)
        self.step_size = step_size
        self.fixed = fixedstep
        self.max_cross = max_cross
        self.maxlen = maxlen
        self.return_all = return_all

    def __iter__(self):
        # Make tracks, move them to point space and return
        track = self._generate_streamlines()
        return utils.move_streamlines(track, self.affine)

    def _generate_streamlines(self):
        """A streamline generator"""
        N = self.maxlen
        dg = self.direction_getter
        tc = self.tissue_classifier
        ss = self.step_size
        fixed = self.fixed
        max_cross = self.max_cross
        vs = self._voxel_size

        # Get inverse transform (lin/offset) for seeds
        inv_A = np.linalg.inv(self.affine)
        lin = inv_A[:3, :3]
        offset = inv_A[:3, 3]

        F = np.empty((N + 1, 3), dtype=float)
        B = F.copy()
        for s in self.seeds:
            s = np.dot(lin, s) + offset
            directions = dg.initial_direction(s)
            directions = directions[:max_cross]
            for first_step in directions:
                stepsF, tissue_class = local_tracker(dg, tc, s, first_step,
                                                     vs, F, ss, fixed)
                if not (self.return_all or
                        tissue_class == TissueTypes.ENDPOINT or
                        tissue_class == TissueTypes.OUTSIDEIMAGE):
                    continue
                first_step = -first_step
                stepsB, tissue_class = local_tracker(dg, tc, s, first_step,
                                                     vs, B, ss, fixed)
                if not (self.return_all or
                        tissue_class == TissueTypes.ENDPOINT or
                        tissue_class == TissueTypes.OUTSIDEIMAGE):
                    continue

                if stepsB == 1:
                    streamline = F[:stepsF].copy()
                else:
                    parts = (B[stepsB-1:0:-1], F[:stepsF])
                    streamline = np.concatenate(parts, axis=0)
                yield streamline


    def compute_all_streamlines(self):
        """computes all streamlines using Pool in Python multiprocessing library"""
        N = self.maxlen
        dg = self.direction_getter
        tc = self.tissue_classifier
        ss = self.step_size
        fixed = self.fixed
        max_cross = self.max_cross
        vs = self._voxel_size

        # Get inverse transform (lin/offset) for seeds
        inv_A = np.linalg.inv(self.affine)
        lin = inv_A[:3, :3]
        offset = inv_A[:3, 3]

        F = np.empty((N + 1, 3), dtype=float)
        B = F.copy()
        
        def streamline_computation(s):
            """
            Helper function for parallelizing the computation of streamlines
            """
            s = np.dot(lin, s) + offset
            directions = dg.initial_direction(s)
            directions = directions[:max_cross]
            for first_step in directions:
                stepsF, tissue_class = local_tracker(dg, tc, s, first_step,
                                                     vs, F, ss, fixed)
                if not (self.return_all or
                        tissue_class == TissueTypes.ENDPOINT or
                        tissue_class == TissueTypes.OUTSIDEIMAGE):
                    continue
                first_step = -first_step
                stepsB, tissue_class = local_tracker(dg, tc, s, first_step,
                                                     vs, B, ss, fixed)
                if not (self.return_all or
                        tissue_class == TissueTypes.ENDPOINT or
                        tissue_class == TissueTypes.OUTSIDEIMAGE):
                    continue
        
                if stepsB == 1:
                    streamline = F[:stepsF].copy()
                else:
                    parts = (B[stepsB-1:0:-1], F[:stepsF])
                    streamline = np.concatenate(parts, axis=0)
                return streamline
                

        
        allTheOs = []
        for s in self.seeds:
            allTheOs.append(DummyClass(streamline_computation,s))
        
        p = multiprocessing.Pool(multiprocessing.cpu_count())
        streamlines = p.map(streamline_computation, self.seeds) 
        return streamlines
        
        
