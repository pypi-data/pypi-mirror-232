import numpy as np
import os
import h5py
import warnings
try :
  import pymc as pm
  import pytensor
  import pytensor.tensor as pt
  import arviz as az
except ImportError :
  warnings.warn ("Module pymc, arviz and/or pytensor not found, MCMC function for spot modelling will not be available.") 
try :
  import jax
  from pymc.sampling.jax import sample_numpyro_nuts
  import tensorflow_probability.substrates.jax as tfp
  jax.scipy.special.erfcx = tfp.math.erfcx
except ImportError :
  warnings.warn ("JAX and/or Tensorflow not found, GPU sampler will not be available.") 
import numba
import cartopy
from scipy.optimize import minimize, Bounds
import matplotlib as mpl
import matplotlib.pyplot as plt
import cloudpickle
import loupiotes

'''
Define the class SpotModel and related
functions.
'''

def load_from_hdf5 (filename, load_netcdf=True,
                    netcdf_file=None) :
  '''
  Load spotmodel stored in an hdf5 file.

  Parameters
  ----------
  filename : str or Path instance
    path of the hdf5 file to read.

  load_netcdf : bool
    whether to load the netcdf file with the ``idata``
    from a sampling. If no file is found, the function
    will issue a warning.
 
  Returns 
  -------
  SpotModel
    The loaded spotmodel instance.
  '''
  f = h5py.File(filename, 'r')
  grp = f["spotmodel"]

  # checking if this a multichannel spotmodel
  if type (grp.attrs["cs"]) not in [int, np.int_, float, np.float_] :
    multichannel = True
  else :
    multichannel = False
       
  if not multichannel :
    spotmodel = SpotModel (large_dim=grp.attrs["large_dim"], 
                          reduced_dim=grp.attrs["reduced_dim"],
                          inclination=grp.attrs["inclination"], 
                          t0=grp.attrs["t0"],
                          omega=grp["omega"][()], 
                          filling_factors=grp["filling_factors"][()],
                          limb_darkening_coeff=grp.attrs["limb_darkening_coeff"], 
                          Q=grp.attrs["Q"],
                          cf0=grp.attrs["cf0"], 
                          cs=grp.attrs["cs"],
                          )
  else :
    spotmodel = loupiotes.spots.SpotModelMultiChannel (large_dim=grp.attrs["large_dim"], 
                          reduced_dim=grp.attrs["reduced_dim"],
                          inclination=grp.attrs["inclination"], 
                          t0=grp.attrs["t0"],
                          omega=grp["omega"][()], 
                          filling_factors=grp["filling_factors"][()],
                          limb_darkening_coeff=grp.attrs["limb_darkening_coeff"], 
                          Q=grp.attrs["Q"],
                          cf0=grp.attrs["cf0"], 
                          cs=grp.attrs["cs"],
                          id_channel=grp.attrs["id_channel"]
                          )

  if spotmodel.__version__ != loupiotes.__version__ :
    warnings.warn ("The loaded SpotModel was created with another version of loupiotes, some unexpected issues might occur.")

  if load_netcdf :
    if netcdf_file is None :
      netcdf_file = os.path.splitext (filename)[0] + ".netcdf"
    if not os.path.exists (netcdf_file) :
      warnings.warn ("netcdf file does not exists, idata will not be loaded.")
    else :
      spotmodel.idata = az.from_netcdf (netcdf_file)


  if "timestamps" in grp.keys () :
    spotmodel.timestamps = grp["timestamps"][()]
  if "lc" in grp.keys () :
    spotmodel.lc = grp["lc"][()]
  if "lc_obs" in grp.keys () :
    spotmodel.lc_obs = grp["lc_obs"][()]
  if "err_obs" in grp.keys () :
    spotmodel.err_obs = grp["err_obs"][()]

  return spotmodel

def load_spot_model (filename, reset_additional_properties=True) :
  '''
  Load an existing ``SpotModel`` from a pickled file. 

  Parameters
  ----------
  
  filename : str or Path instance
    filename of the spotmodel to load.

  reset_additional_properties : bool
  '''
  with open (filename, 'rb') as f :
     spotmodel = cloudpickle.load (f)
  if spotmodel.__version__ != loupiotes.__version__ :
    warnings.warn ("The loaded SpotModel was created with another version of loupiotes, some unexpected issues might occur.")
  if reset_additional_properties :
    spotmodel.resetAdditionalProperties ()
  return spotmodel

def expand (reduced, large_dim) :
  '''
  Expand the elements of a reduced grid (``numpy`` array) 
  to a large grid. 
  '''
  reduced_dim = reduced.shape 
  if large_dim[0]%reduced_dim[0]!=0 or large_dim[1]%reduced_dim[1]!=0 :
    raise Exception ("Dimensions are not consistent.")
  f0, f1 = large_dim[0]//reduced_dim[0], large_dim[1]//reduced_dim[1]
  expanded = np.repeat (reduced, f0, axis=0)
  expanded = np.repeat (expanded, f1, axis=1)

  return expanded

def reduce (expanded, reduced_dim) :
  '''
  Reduce the elements of an expanded grid (``numpy`` array) 
  to a their original dimension. 
  '''
  large_dim = expanded.shape 
  if large_dim[0]%reduced_dim[0]!=0 or large_dim[1]%reduced_dim[1]!=0 :
    raise Exception ("Dimensions are not consistent.")
  reduced = expanded[::large_dim[0]//reduced_dim[0],::large_dim[1]//reduced_dim[1]]

  return reduced

def expand_tensor (reduced, reduced_dim, large_dim) :
  '''
  Expand the elements of a reduced grid (``pytensor`` tensor) 
  to a large grid. 
  '''
  if large_dim[0]%reduced_dim[0]!=0 or large_dim[1]%reduced_dim[1]!=0 :
    raise Exception ("Dimensions are not consistent.")
  f0, f1 = large_dim[0]//reduced_dim[0], large_dim[1]//reduced_dim[1]
  expanded = pt.repeat (reduced, f0, axis=0)
  expanded = pt.repeat (expanded, f1, axis=1)

  return expanded

class SpotModel :
  '''
  SpotModel object, including all necessary tools
  to generate spot-modelled light curves.
  '''

  def __init__ (self, large_dim=(180,180), reduced_dim=(18,18),
                inclination=90, t0=0, 
                omega=2.6e-6, filling_factors=None,
                limb_darkening_coeff=None, Q=0,
                cf0=1, cs=1, initialise_grid=True) :
    '''
    Parameters
    ----------
    
    large_dim: tuple
      Dimension of the large grids of the spot model. First element of the 
      tuple is the number of latitudinal nodes, second element
      the number of longitudinal nodes. 
      Optional, default ``(180,180)``.

    reduced_dim: tuple
      Dimension of the reduced grids (used to set parameters in common for the
      large grid).  First element of the tuple is the number of latitudinal nodes,
      second element the number of longitudinal nodes.  Optional, default
      ``(180,180)``.  

    inclination : float
      Stellar inclination with respect to the observer (in degrees).
      Optional, default ``90``.

    t0 : float
      Initial time (in days) to consider in the model. 
      Optional, default ``0``.

    omega : float or ndarray
      Stellar angular frequency, in rad/Hz. 
      Can be a float or a 1D-array
      of length ``reduced_dim[0]``. Optional, default ``2.6e-6``
      (solar value)

    filling_factors : ndarray
      Initial filling factors of the model, must be of
      ``reduced_dim`` dimension.
      Optional, default ``None``.

    limb_darkening_coeff : tuple
      Quadratic limb-darkening coefficient, following 
      the formulation of Claret (2000).

    Q : float
      Ratio between the spot and facula filling factors.
      Optional, default ``0``.

    cf0 : float
      Faculae contrast coefficient.

    cs : float
      Spot contrast coefficient.
    '''
    self.__version__ = loupiotes.__version__
    self.t0 = t0
    self.Q, self.cf0, self.cs = Q, cf0, cs
    # Stellar inclination
    self.inclination = np.pi * inclination / 180 

    # Rotation profile
    if type (omega) in [float, np.float_, int, np.int_] :
      self.omega = omega
    elif omega.shape==1 :
      #This is designed to pass a 1d latitudinal vector
      #with the rotation profile
      omega = omega.reshape (omega.size, 1)
      self.omega = expand (omega, large_dim)    
    elif omega.shape==2 :
      #This is designed to pass directly a 2d grid
      #with the rotation profile
      self.omega = omega

    # Limb-darkening coeff
    if limb_darkening_coeff is None :
      # Setting the Kepler 5750K, 4.50 dex value from Sing 2010
      self.limb_darkening_coeff = (0.3985, 0.2586)
    else : 
      self.limb_darkening_coeff = limb_darkening_coeff

    # Grid elements
    self.large_dim = large_dim
    self.reduced_dim = reduced_dim
    if filling_factors is None :
      #Model without spots
      self.FillingFactorsReduced = np.full (reduced_dim, 0)
      self.FillingFactors = np.full (large_dim, 0)
    else :
      self.FillingFactorsReduced = filling_factors
      self.FillingFactors = expand (filling_factors, large_dim)

    self.initialiseGeometry ()
    if initialise_grid :
      self.initialiseGeometry ()

    # Light curve currently stored
    self.timestamps = np.array ([t0*86400])
    self.lc = None
    self.lc_obs, self.err_obs = None, None

    # PyMc inference data object
    self.idata = None
    # Additional properties
    self.resetAdditionalProperties ()

  def initialiseGeometry (self) :
    '''
    Intialise geometric elements of the model.
    '''
    # Initialise coordinates (angle are in radians)
    colatitudes, dtheta = np.linspace (0, np.pi, self.large_dim[0], 
                                       endpoint=False, retstep=True)
    colatitudes += dtheta/2 #avoid having zero-area cells at the poles.
    longitudes, dphi = np.linspace (0, 2*np.pi, self.large_dim[1], 
                                    endpoint=False, retstep=True) 
    self.colatitudes, self.longitudes = np.meshgrid (colatitudes, longitudes,
                                                     indexing='ij') 

    # Reduced dim coordinates
    colatitudes_reduced, dtheta_reduced = np.linspace (0, np.pi, self.reduced_dim[0], 
                                       endpoint=False, retstep=True)
    colatitudes_reduced += dtheta_reduced/2 #avoid having zero-area cells at the poles.
    longitudes_reduced, dphi_reduced = np.linspace (0, 2*np.pi, self.reduced_dim[1], 
                                                    endpoint=False, retstep=True) 
    (self.colatitudesReduced, 
     self.longitudesReduced) = np.meshgrid (colatitudes_reduced, 
                                            longitudes_reduced,
                                            indexing='ij') 

    # Auxiliary parameter useful to compute light curves fast
    self.__cos_i_cos_theta = np.cos (self.inclination) * np.cos (self.colatitudes) 
    self.__sin_i_sin_theta = np.sin (self.inclination) * np.sin (self.colatitudes)

    # Compute area of each element
    self.area = dtheta * np.sin (self.colatitudes) * dphi
    self.areaReduced = dtheta_reduced * np.sin (self.colatitudesReduced) * dphi_reduced

  def initialiseGrid (self) :
    '''
    Intialise grids of the model.
    '''
    # Compute the initial values of the grids 
    self.updateVisibility (self.t0)
    self.computeUnperturbedFlux ()
    self.computeObservedFlux ()

  def resetAdditionalProperties (self) :
    '''
    Reset additional properties.
    This can be useful to ensure that a spotmodel
    for an older variation has every required variable
    names initialised.
    '''
    self.BroadcastPrecomputed = False 
    if self.idata is None :
      self.SamplingPerformed = False
    else :
      self.SamplingPerformed = True
    self.FFLongitudinal = None
    self.FFLatitudinal = None
    self.lcTensor = None
    self.VisibilityFraction = None
    (self.muBroadcast,
     self.visibilityBroadcast,
     self.UnperturbedBroadcast,
     self.UnperturbedSumBroadcast) = None, None, None, None

  def save (self, filename, netcdf_file=None) :
    '''
    Save the model to ``filename`` as pickled file.

    Parameters
    ----------
    filename : str or Path instance
      path of the file to be saved.

    netcdf_file : str or Path instance
      if provided, the ``InferenceData`` object (if
      existing), will also be saved independently under
      this name.
    '''
    if netcdf_file is not None and self.idata is not None :
      self.idata.to_netcdf (netcdf_file)
    with open (filename, 'wb') as f :
      cloudpickle.dump (self, f)

  def to_hdf5 (self, filename, create_netcdf=True,
               override=True) :
    '''
    Save the model to an hdf5 files.

    Parameters
    ----------
    filename : str or Path instance
      path of the hdf5 file where to save the model.

    create_netcdf : bool
      If set to ``True`` and the model has an ``idata``,
      it will be save to a netcdf file with same basename
      as the hdf5 file.
    '''
    # Adding extension if necessary
    if os.path.splitext (filename)[1]=='' :
      filename += ".h5"
    netcdf_file = os.path.splitext (filename)[0] + ".netcdf"

    if override and os.path.exists (filename) :
      # Remove existing files
      os.remove (filename)

    if create_netcdf and self.idata is not None :
      if override and os.path.exists (netcdf_file) :
        # Remove existing files
        os.remove (netcdf_file)
      self.idata.to_netcdf (netcdf_file)
    f = h5py.File(filename, 'x')
    grp = f.create_group ("spotmodel")
   
    # Saving attributes
    grp.attrs['version'] = self.__version__
    grp.attrs['large_dim'] = self.large_dim
    grp.attrs['reduced_dim'] = self.reduced_dim
    grp.attrs['t0'] = self.t0
    grp.attrs['Q'] = self.Q
    grp.attrs['cs'] = self.cs
    grp.attrs['cf0'] = self.cf0
    grp.attrs['inclination'] = 180/np.pi * self.inclination
    grp.attrs['limb_darkening_coeff'] = self.limb_darkening_coeff
    # Checking if it is a multichannel object
    if type (self.cs) not in [int, float] :
      grp.attrs['id_channel'] = self.id_channel

    # Saving datasets
    dset = grp.create_dataset ("omega", 
                               data=self.omega)
    dset = grp.create_dataset ("filling_factors", 
                               data=self.FillingFactorsReduced)
    if self.timestamps is not None :
      dset = grp.create_dataset ("timestamps", 
                                 data=self.timestamps)
    if self.lc is not None :
      dset = grp.create_dataset ("lc", 
                                 data=self.lc)
    if self.lc_obs is not None :
      dset = grp.create_dataset ("lc_obs", 
                                 data=self.lc_obs)
    if self.err_obs is not None :
      dset = grp.create_dataset ("err_obs", 
                                 data=self.err_obs)

    f.close ()

  def computeUnperturbed (self) :
    '''
    Compute the unperturbed flux grid taking into account
    limb-darkening effects (using a quadratic law). 

    Returns
    -------
    ndarray
      A view of the unperturbed grid.
    '''
    aux = 1 - self.mu
    self.Unperturbed = 1 - self.limb_darkening_coeff[0] * aux - self.limb_darkening_coeff[1] * aux**2
    self.Unperturbed = self.Unperturbed * self.area * self.mu * self.visibility
    return self.Unperturbed

  def computeFluxGrid (self) :
    '''
    Compute the flux grid from the unperturbed reference,
    taking into account spot and facula coverage.

    Returns
    -------
    ndarray
      A view of the updated flux grid.
    '''
    aux = 1 + (self.cf0 * self.Q * (1-self.mu) - self.cs) * self.FillingFactors
    self.FluxGrid = aux * self.Unperturbed 
    return self.FluxGrid 

  def computeUnperturbedFlux (self) :
    '''
    Use the grids to compute the scalar 
    unperturbed flux in the current configuration. 

    Returns
    -------
    float
      Computed flux value.
    '''
    self.UnperturbedFlux = np.sum (self.Unperturbed) 
    return self.UnperturbedFlux

  def computeObservedFlux (self) :
    '''
    Use the grids to compute the scalar 
    observed flux in the current configuration. 

    Returns
    -------
    float
      Computed flux value.
    '''
    self.ObservedFlux = np.sum (self.FluxGrid) / np.sum (self.Unperturbed)  
    return self.ObservedFlux
   
  def updateVisibility (self, t) :
    '''
    Update array at a time t.

    Parameters
    ----------
    t : float
      time to consider to update the grids.

    Returns
    -------
    ndarray
      A view of the updated ``mu`` and ``visibility`` grids.
    '''
    aux_1 = np.sin (self.inclination) * np.sin (self.colatitudes)
    aux_1 = aux_1 * np.cos (self.longitudes + self.omega*(t - self.t0))
    aux_2 = np.cos (self.inclination) * np.cos (self.colatitudes)
    self.mu = aux_1 + aux_2 
    self.visibility = np.zeros (self.large_dim) 
    self.visibility[self.mu>=0] = 1
    unperturbed = self.computeUnperturbed ()
    fluxgrid = self.computeFluxGrid ()
    return self.mu, self.visibility, unperturbed, fluxgrid

  def generateLightCurve (self, timestamps, use_numba=True,
                          use_pymc=False, use_broadcast=False,
                          zero_mean=False) :
    '''
    Generate a light curve from the spot model.
    
    After calling this function if ``use_pymc`` is ``False``
    and ``use_broadcast`` is ``False, the grids of the ``SpotModel`` object 
    will be in the state corresponding to ``t=timestamps[-1]``.

    Parameters
    ----------
    timestamps : ndarray
      timestamps (in seconds) of the light curve.

    use_numba : bool
      whether or not to use the ``numba`` implementation of the 
      light curve generation function. Optional, default ``True``.

    use_pymc : bool 
      whether to compute a tensorial expression for the light
      curve rather than returning a light curve array. This is
      mainly aimed at being used wrapped inside the 
      ``explore_distribution`` function. 
      Optional, default ``False``.

    use_broadcast : bool
      Compute the light curve with a ``numpy`` broadcast method
      rather than using an explicit loop of the elements of
      ``timestamps``. ``precomputeBroadcast`` has to be 
      called first by the ``SpotModel`` object. Optional,
      default ``False``. 
 
    zero_mean : bool
      if set to ``True``, the mean of the generated light curve
      will be substracted to ensure that it is zero. Optional,
      default ``True``.

    Returns
    -------
    ndarray or pytensor object
      If ``use_pymc`` is ``False``, returns the generated 1D light curve, 
      as an array which has length ``timestamps.size``. It is also set as 
      the current value of ``self.lc``. Otherwise, return a tensor object
      (see ``pymc`` and ``pytensor`` documentation) that can be used
      to evaluate the light curve profile.
    '''

    self.timestamps = timestamps
    if use_pymc :
       self.lcTensor = _generate_lightcurve_pymc (self.timestamps, self.large_dim, 
                            self.__cos_i_cos_theta, self.__sin_i_sin_theta,
                            self.longitudes, self.omegaPyMC, self.t0, 
                            self.limb_darkening_coeff, self.area, 
                            self.FillingFactorsExpandedPyMC,
                            cf0=self.cf0PyMC, Q=self.QPyMC, cs=self.cs, 
                            zero_mean=zero_mean) 
       return self.lcTensor
    elif use_numba :
      (self.lc, self.mu,
       self.visibility, self.Unperturbed,
       self.FluxGrid) = _generate_lightcurve (self.timestamps, self.large_dim, 
                            self.__cos_i_cos_theta, self.__sin_i_sin_theta,
                            self.longitudes, self.omega, self.t0, 
                            self.limb_darkening_coeff, self.area, self.FillingFactors,
                            cf0=self.cf0, Q=self.Q, cs=self.cs) 
    elif use_broadcast :
       if not self.BroadcastPrecomputed :
         raise Exception ("You have to use precomputeBroadcast before running the use_broadcast option.")
       self.lc = _generate_lightcurve_broadcast (self.muBroadcast, 
                                                 self.visibilityBroadcast, 
                                                 self.UnperturbedBroadcast,
                                                 self.UnperturbedSumBroadcast,
                                                 self.FillingFactors, cf0=self.cf0, 
                                                 Q=self.Q, cs=self.cs)
    else :
      self.lc = np.zeros (timestamps.size)
      for ii, t in enumerate (timestamps) :
        self.updateVisibility (t)
        self.lc[ii] = self.computeObservedFlux ()
      # In this mode, update visibility to initial timestamps
      # for visualisation convenience (especially when using 
      # models with differential rotation).
      self.updateVisibility (timestamps[0])
    if zero_mean :
      self.lc -= np.mean (self.lc)
    return self.lc

  def generateUnperturbedLightCurve (self, timestamps, zero_mean=True,
                                     normalise=True) :
    '''
    Generate unperturbed light curve. This is mainly intended to
    provide a sanity check for grid resolution effects.
    '''
    self.lcUnperturbed = np.zeros (timestamps.size)
    for ii, t in enumerate (timestamps) :
        self.updateVisibility (t)
        self.lcUnperturbed[ii] = self.computeUnperturbedFlux ()
    if normalise :
        self.lcUnperturbed /= np.mean (self.lcUnperturbed)
    if zero_mean :
        self.lcUnperturbed -= np.mean (self.lcUnperturbed)

    return self.lcUnperturbed

  def computeLongitudinalDistribution (self, normalise_max=False,
                                       min_theta=0, max_theta=180,
                                       correct_visibility=True,
                                       correction_factor=1) :
    '''
    Compute longitudinal distribution of filling factors.

    Parameters
    ----------
    correction_factor : float
      Correction factor to apply on the distribution. Might be useful 
      to renormalise filling factor distribution when
      analysing pure spots model (Q=0) with arbitrary contrast factors. 
    '''
    # restricting to latitude between min_theta and max_theta
    if correct_visibility :
      if self.VisibilityFraction is None :
        self.computeVisibilityFraction ()
      ff = self.FillingFactors * self.VisibilityFraction 
    else :
      ff = self.FillingFactors
    cond = (self.colatitudes>min_theta*np.pi/180)&(self.colatitudes<max_theta*np.pi/180)
    self.FFLongitudinal = np.sum (ff[cond[:,0],:]*self.area[cond[:,0],:], axis=0)
    self.FFLongitudinal /= np.sum (self.area[cond[:,0],:], axis=0)

    self.FFLongitudinal *= correction_factor

    if normalise_max :
      self.FFLongitudinal /= np.amax (self.FFLongitudinal)

    return self.FFLongitudinal

  def computeLatitudinalDistribution (self, normalise_max=False,
                                      correct_visibility=True) :
    '''
    Compute latitudinal distribution of filling factors.
    '''
    if correct_visibility :
      if self.VisibilityFraction is None :
        self.computeVisibilityFraction ()
      ff = self.FillingFactors * self.VisibilityFraction 
    else :
      ff = self.FillingFactors
    self.FFLatitudinal = np.sum (ff*self.area, axis=1)
    self.FFLatitudinal /= np.sum (self.area, axis=1)
    if normalise_max :
      self.FFLatitudinal /= np.amax (self.FFLatitudinal)

    return self.FFLatitudinal

  def plotLongitudinalDistribution (self, normalise_max=False,
                                    figsize=(8,4), style='classic',
                                    cmap='gist_heat_r', ax=None,
                                    correct_visibility=True) :
    '''
    Plot longitudinal distribution of filling factors.
    '''
    self.computeLongitudinalDistribution (normalise_max=normalise_max,
                                 correct_visibility=correct_visibility)
    if ax is None :
      fig, ax = plt.subplots (1, 1, figsize=figsize)
    else :
      fig = None
    if style=='classic' :
      ax.plot (180*self.longitudes[0,:]/np.pi, self.FFLongitudinal,
               lw=2, color='darkorange')
      ax.set_ylabel (r"$f_{s,\mathrm{lon}}$")
    elif style=='colorbar' :
      ax.imshow (self.FFLongitudinal.reshape (1, self.large_dim[1]), 
                 aspect='auto', extent=(0, 360, -1, 1), cmap=cmap)
      ax.axes.get_yaxis().set_visible(False)
    ax.set_xlabel (r"$\phi$ ($^o$)")
    ax.set_xticks (range (0, 420, 60))
    return fig

  def plotLatitudinalDistribution (self, normalise_max=False,
                                   figsize=(4,8), style='classic',
                                   cmap='gist_heat_r', ax=None,
                                   correct_visibility=True) :
    '''
    Plot latitudinal distribution of filling factors.
    '''
    self.computeLatitudinalDistribution (normalise_max=normalise_max,
                                    correct_visibility=correct_visibility)
    if ax is None :
      fig, ax = plt.subplots (1, 1, figsize=figsize)
    else :
      fig = None
    if style=='classic' :
      ax.plot (self.FFLatitudinal, 180*self.latitudes[:,0]/np.pi,
               lw=2, color='darkorange')
      ax.set_xlabel (r"$f_{s,\mathrm{lat}}$")
    elif style=='colorbar' :
      ax.imshow (self.FFLatitudinal.reshape (self.large_dim[0], 1), 
                 aspect='auto', extent=(-1, 1, 180, 0), cmap=cmap)
      ax.axes.get_xaxis().set_visible(False)
    ax.set_ylabel (r"$\theta$ ($^o$)")
    ax.set_yticks (range (180, -60, -60))
    return fig

  def plotProjectedDistributions (self, normalise_max=False, figsize=(8,4),
                                  cmap='gist_heat_r', vmin=None, vmax=None,
                                  colorbar=True, correct_visibility=True) :
    '''
    Plot filling factor distributions and corresponding projections
    along latitude and longitudes. 
    '''
    fig, axs = plt.subplots (2, 3, figsize=figsize, 
                             width_ratios=[0.05, 0.9, 0.05],
                             height_ratios=[0.9, 0.1])
    im = axs[0,1].imshow (self.FillingFactors, cmap='binary', vmin=vmin, vmax=vmax,
                          extent=(0,360,180,0), aspect='auto')
    self.plotLatitudinalDistribution (normalise_max=normalise_max, cmap=cmap,
                                      ax=axs[0,0], style='colorbar',
                                      correct_visibility=correct_visibility)
    self.plotLongitudinalDistribution (normalise_max=normalise_max, cmap=cmap,
                                       ax=axs[1,1], style='colorbar',
                                       correct_visibility=correct_visibility)
    if colorbar :
      cbar = plt.colorbar (im, ax=axs[0,1], cax=axs[0,2])
      cbar.set_label (r'$f_s$')
    axs[0,1].set_xticks ([])
    axs[0,1].set_yticks ([])
    axs[1,0].set_visible (False)
    axs[1,2].set_visible (False)
    
    return fig

  def precomputeBroadcast (self) :
    '''
    Precompute arrays that will be necessary to generate light 
    curves in the ``broadcast`` mode.
    '''
    (self.muBroadcast,
     self.visibilityBroadcast,
     self.UnperturbedBroadcast,
     self.UnperturbedSumBroadcast) = precompute_generate_lightcurve_broadcast (
                    self.timestamps, self.large_dim,
                    self.__cos_i_cos_theta, self.__sin_i_sin_theta,
                    self.longitudes, self.omega, self.t0,
                    self.limb_darkening_coeff, self.area,
                    )
    self.BroadcastPrecomputed = True 

  def removeBroadcastedElements (self) :
    '''
    Remove broadcasted elements and set to ``None``
    corresponding variables.
    '''
    (self.muBroadcast,
     self.visibilityBroadcast,
     self.UnperturbedBroadcast,
     self.UnperturbedSumBroadcast) = None, None, None, None
    self.BroadcastPrecomputed = False 

  def computeVisibilityFraction (self) :
    '''
    Compute the visibility correction of surface elements
    for postprocessing, according to Eq. 8 from Lanza et al.
    2007.

    In the current implementation, it assumes that datapoints
    are regularly sampled.
    '''
    # Sanity check in case there is no light curve
    if self.timestamps is not None : 
      self.precomputeBroadcast ()
      self.VisibilityFraction = np.mean (self.muBroadcast*self.visibilityBroadcast, axis=0)
      self.removeBroadcastedElements ()
    else :
      self.VisibilityFraction = 0
    return self.VisibilityFraction
    
  def getLightCurve (self) :
    '''
    Provide stored light curve and corresponding timestamps.

    Returns
    -------
    tuple of arrays
      The timestamps and light curve arrays as a tuple.
    '''
    if self.lc is None :
      raise Exception ("You must generate a light curve first.")
    else :
      return self.timestamps, self.lc

  def plotLightCurve (self, timestamps=None, lc_obs=None,  
                      err_obs=None, plot_obs=True, 
                      ppm=False, unperturbed=False,
                      zero_mean=False, figsize=(8,4), marker='none', lw=2, 
                      xlabel='Time (day)', ylabel=None,
                      show_errorbars=False, color="darkorange",
                      **kwargs) :
    '''
    Plot light curve corresponding to the spot model, as well 
    as the reference observed light curve when ``plot_obs`` is
    ``True``.
    '''
    if ppm :
      factor = 1e6 
    else :
      factor = 1
    if ylabel is None :
      if ppm :
        ylabel='Flux (ppm)'
      else : 
        ylabel='Flux (normalised)'
    if timestamps is None :
      timestamps = self.timestamps
    if timestamps is None :
      raise Exception ("You must generate a light curve first.")
    if unperturbed :
      lc = self.generateUnperturbedLightCurve (timestamps, zero_mean=zero_mean)
    else : 
      lc = self.generateLightCurve (timestamps, use_numba=False, 
                                    zero_mean=zero_mean)
    fig, ax = plt.subplots (1, 1, figsize=figsize, **kwargs)
    ax.plot (timestamps/86400, lc*factor, color=color, 
             marker=marker, lw=lw)
    if not unperturbed and plot_obs :
      if lc_obs is None :
        lc_obs, err_obs = self.lc_obs, self.err_obs
      else :
        lc_obs, err_obs = lc_obs*1e-6, err_obs*1e-6
      if lc_obs is None :
        warnings.warn ("No observed light curve to plot.") 
      else :
        if show_errorbars :
          yerr = err_obs*factor
        else :
          yerr = None
        if zero_mean :
          shift = np.mean (lc_obs)
        else :
          shift = 0 
        ax.errorbar (timestamps/86400, (lc_obs-shift)*factor, yerr=yerr, 
                     fmt='o', color='black', markerfacecolor='none',
                     markeredgecolor='black', capsize=4,
                     zorder=-1)
    ax.set_xlabel (xlabel)
    ax.set_ylabel (ylabel)

    return fig

  def plotFluxGrid (self, figsize=(6,6),
                    cmap='afmhot', show=True,
                    filename=None, dpi=300,
                    projection=None, normscale='linear', 
                    plot_unperturbed=False) :
    '''
    Plot the flux grid as currently observed.

    Parameters
    ----------
    
    figsize : tuple
      ``Figure`` size. Optional, default ``(6,6)``.

    cmap : str or ``Colormap`` instance
      color map to use. Optional, default ``afmhot``.

    show : bool
      whether to call ``plt.show ()``. Optional, default 
      ``True``.

    filename : str or ``Path`` instance
      if provided, the figure will be saved under this name.
      Optional, default ``None``.

    dpi : int
      Optional, default 300.

    projection : str
      should be ``mercator``, ``mollweide`` or ``None``.
      If ``None``, the projection will be ``NearsidePerspective``
      from the ``cartopy`` module.

    plot_unperturbed : bool
      if set to ``True``, the ``Unperturbed`` grid will be plotted
      rather than the ``FluxGrid`` with spots and faculae.
      Optional, default ``False``.

    Returns
    -------
    matplotlib.pyplot.figure
      The ``matplotlib`` figure object used to plot
      the grid.
    '''
    # Remember that FluxGrid are already multiplied
    # by cell area, so this needs to be renormalised.
    fig = plt.figure (figsize=figsize)
    if plot_unperturbed :
      grid = self.Unperturbed / self.area
    else :
      grid = self.FluxGrid / self.area

    if normscale=='log' :
     norm = mpl.colors.LogNorm(vmin=grid[grid!=0].min(), vmax=grid.max())
    else :
     norm = mpl.colors.Normalize()
     
    if projection is None :
      projection = 'nearside_perspective'
    if projection=='mercator' :
      ax = fig.add_subplot (111)
      im = ax.imshow (grid, cmap=cmap, extent=(0,360,180,0), 
                      aspect='auto', norm=norm)
      ax.set_xlabel (r'$\phi$ ($^o$)')
      ax.set_ylabel (r'$\theta$ ($^o$)')
      ax.set_xticks (range (0, 420, 60))
      ax.set_yticks (range (0, 210, 30))
    elif projection=='mollweide' :
      central_longitude = 180/np.pi * np.ravel (self.longitudes)[np.argmax(self.mu)] - 180
      ax = fig.add_subplot (111,
                          projection=cartopy.crs.Mollweide(central_longitude=central_longitude))
      im = ax.imshow (grid, transform=cartopy.crs.PlateCarree(),
                      cmap=cmap, norm=norm)
    elif projection=='nearside_perspective' :
      central_latitude = 90 - 180/np.pi*self.inclination
      central_longitude = 180/np.pi * np.ravel (self.longitudes)[np.argmax(self.mu)] - 180 
      ax = fig.add_subplot (111,
                          projection=cartopy.crs.NearsidePerspective(central_latitude=central_latitude,
                                                                     central_longitude=central_longitude))
      im = ax.imshow (grid, transform=cartopy.crs.PlateCarree(),
                      cmap=cmap, norm=norm)
    else :
      raise Exception ("Unknown requested projection.")
    if show :
      plt.show ()
    if filename is not None :
      plt.savefig (filename, dpi=dpi)

    return fig

  def plotGrid (self, gridname='filling_factors',
                figsize=(6,6), vmin=None, vmax=None,
                cmap='binary', show=True,
                filename=None, dpi=300,
                projection=None, colorbar=True) :
    '''
    Plot the chosen grid in its current state.

    Parameters
    ----------
    
    figsize : tuple
      ``Figure`` size. Optional, default ``(6,6)``.

    vmin : float
      min value to use with the color map. Optional,
      default ``None``.

    vmax : float
      max value to use with the color map. Optional,
      default ``None``.

    cmap : str or ``Colormap`` instance
      color map to use. Optional, default ``binary``.

    show : bool
      whether to call ``plt.show ()``. Optional, default 
      ``True``.

    filename : str or ``Path`` instance
      if provided, the figure will be saved under this name.
      Optional, default ``None``.

    dpi : int
      Optional, default 300.

    projection : str
      should be ``mercator``, ``mollweide`` or ``None``.
      If ``None``, the projection will be ``NearsidePerspective``
      from the ``cartopy`` module.

    colorbar : bool
      whether to show the colorbar on the figure. Optional,
      default ``True``.

    Returns
    -------
    matplotlib.pyplot.figure
      The ``matplotlib`` figure object used to plot
      the grid.
    '''
    if gridname=='filling_factors' :
      grid = self.FillingFactors
      label_cbar = r'$f_s$'
      if vmin is None :
        vmin = 0
      if vmax is None :
        vmax = 1 / (1+self.Q)
    else :
      raise Exception ("Unkown grid or not implemented in the function yet.")
    fig = plt.figure (figsize=figsize)
    if projection is None :
      projection = 'nearside_perspective'
    if projection=='mercator' :
      ax = fig.add_subplot (111)
      im = ax.imshow (grid, cmap=cmap, vmin=vmin, vmax=vmax, 
                      extent=(0,360,180,0), aspect='auto')
      ax.set_xlabel (r'$\phi$ ($^o$)')
      ax.set_ylabel (r'$\theta$ ($^o$)')
      ax.set_xticks (range (0, 420, 60))
      ax.set_yticks (range (0, 210, 30))
    elif projection=='nearside_perspective' :
      central_latitude = 90 - 180/np.pi*self.inclination
      central_longitude = 180/np.pi * np.ravel (self.longitudes)[np.argmax(self.mu)] - 180
      ax = fig.add_subplot (111,
                          projection=cartopy.crs.NearsidePerspective(central_latitude=central_latitude,
                                                                     central_longitude=central_longitude))
      im = ax.imshow (grid, transform=cartopy.crs.PlateCarree(),
                      cmap=cmap, vmin=vmin, vmax=vmax)
    elif projection=='mollweide' :
      central_longitude = 180/np.pi * np.ravel (self.longitudes)[np.argmax(self.mu)] - 180
      ax = fig.add_subplot (111,
                          projection=cartopy.crs.Mollweide(central_longitude=central_longitude))
      im = ax.imshow (grid, transform=cartopy.crs.PlateCarree(),
                      cmap=cmap, vmin=vmin, vmax=vmax)
    else :
      raise Exception ("Unkown requested projection.")
    if colorbar :
      cbar = plt.colorbar (im)
      cbar.set_label (label_cbar)
    if show :
      plt.show ()
    if filename is not None :
      plt.savefig (filename, dpi=dpi)

    return fig

  def explore_distribution (self, timestamps, lc_data, err_data=1,
                            prior_distribution_filling_factors='Uniform', 
                            initval_filling_factors=None,
                            prior_omega='TruncatedNormal',
                            sigma=0.1, active_latitude=False, beta=1, 
                            upper_active_latitude=60, filename=None,
                            maximum_entropy=False, lambda_me=1, 
                            new_sampling=True, lower_filling_factors=None,
                            sample_omega=False, sigma_omega=None, ppm=False,
                            sample_Q=False, lower_Q=0, upper_Q=20, 
                            sample_cf0=False, lower_cf0=0.05, upper_cf0=0.3,
                            summary_metric='mean', nuts_sampler='pymc', 
                            zero_mean=False, use_map=False, maxeval_map=10000, 
                            **kwargs) :
    '''
    Perform a MCMC exploration of the posterior distribution.

    Parameters
    ----------

    timestamps : ndarray
      timestamps of the observation contained in ``lc_data``.

    lc_data : ndarray
      observed values 

    err_data : ndarray or float
      the estimated error on ``lc_data``. Optional, default ``1``.

    prior_distribution_filling_factors : str
      prior distribution to consider for the filling factors
      of the model. Should be ``Uniform`` or ``TruncatedNormal``
      Optional, default ``TruncatedNormal``.

    sigma : float
      if ``prior_distribution_filling_factors`` is ``TruncatedNormal``,
      standard deviation of the related normal distribution.
      Optional, default ``0.01``.

    draws : int
      number of samples to create with the NUTS sampler.
      Optional, default ``1000``.

    tune : int
      number of samples used for the tuning step of the NUTS sampler.
      Optional, default ``1000``.

    filename : str or ``Path`` object
      if provided, the ``InferenceData`` object created by the sampling
      will be saved under ``filename``. Optional, default ``None``.   

    maximum_entropy : bool
      whether to consider or not a maximum entropy problem when sampling
      the posterior. See Lanza 2016. Optional, default ``False``.

    lambda_me : float
      value of the Lagrangian multiplier used in the maximum entropy 
      problem. Optional, default ``1``.

    new_sampling : bool
      if set to False, the function will simply return the existing
      ``idata`` (in the case where no ``idata`` attribute exists, it
      will proceed with the ``PyMC`` sampling).

    lower_filling_factors : float
      lower bounds for the filling factors distribution (whether it is
      ``Uniform`` or ``TruncatedNormal``).

    ppm : bool
      If ``True``, the function will consider that the inputs ``lc_data`` 
      and ``err_data`` normalised in ppm.

    **kwargs :
      Any additional argument provided will be passed to ``pymc.sample``. 

    Returns
    -------
    arviz.InferenceData
      ``InferenceData`` from the pyMC sampling. This object is also accessible
      through the ``idata`` attribute of the ``SpotModel`` object.
    '''
    if not new_sampling and self.SamplingPerformed:
      self.update_from_idata (sample_omega=sample_omega, 
                              active_latitude=active_latitude,
                              summary_metric=summary_metric, 
                              zero_mean=zero_mean)
      return self.idata 

    if ppm :
      lc_data, err_data = lc_data*1e-6, err_data*1e-6

    # Setting default target_accept for pymc.sample
    kwargs.setdefault ('target_accept', 0.9)

    if lower_filling_factors is None :
      if maximum_entropy :
        lower_filling_factors = 1e-6
      else :
        lower_filling_factors = 0

    if lower_filling_factors==0 and maximum_entropy :
      warnings.warn ("Parameter lower_filling_factors should not be 0 when using maximum_entropy, setting it to 1e-6.")
      lower_filling_factors = 1e-6

    sampling_model = pm.Model ()
    with sampling_model:

      # Faculae fraction area
      if sample_Q :
        self.QPyMC = pm.Uniform ('Q', lower=lower_Q, 
                                 upper=upper_Q) 
      else :
        self.QPyMC = self.Q

      # Facular contrast
      if sample_cf0 : 
        self.cf0PyMC = pm.Uniform ('cf0', lower=lower_cf0, 
                                   upper=upper_cf0) 
      else :
        self.cf0PyMC = self.cf0
  
      # Filling factors upper limit
      upper_filling_factors = 1 / (1+self.QPyMC)

      # Rotation frequency sampling
      if sample_omega :
        if sigma_omega is None :
          # Setting a very small sigma over omega if 
          # not provided
          sigma_omega = 1.e-9
        if prior_omega=='Uniform' :
          self.omegaPyMC = pm.Uniform ('omega', lower=self.omega-sigma_omega, 
                                                upper=self.omega+sigma_omega,
                                                initval=self.omega)
        else :
           self.omegaPyMC = pm.TruncatedNormal ('omega', mu=self.omega, sigma=sigma_omega,
                                                lower=0, initval=self.omega)
      else :
        self.omegaPyMC = self.omega

      # Prior distribution filling factors
      if active_latitude :
        upper = upper_active_latitude
        lambda_a = pm.Uniform ('lambda_a', lower=0, 
                                 upper=upper, initval=upper/2)
        latitudesReduced = np.pi/2 - self.colatitudesReduced
        if prior_distribution_filling_factors=='TruncatedNormal' : 
          sigma = pm.Deterministic ('sigma', 
                                    sigma * (1 - 2/np.pi*pt.abs (pt.abs (latitudesReduced) - np.pi/180*lambda_a))**beta)
        elif prior_distribution_filling_factors=='Uniform' :
          upper_filling_factors = pm.Deterministic('upper_filling_factor',
                                                    upper_filling_factors * (1 - 2/np.pi*pt.abs (pt.abs (latitudesReduced) - np.pi/180*lambda_a))**beta)
      if prior_distribution_filling_factors=='TruncatedNormal' :
        self.FillingFactorsReducedPyMC = pm.TruncatedNormal ('filling_factors',
                                                             mu=lower_filling_factors, 
                                                             sigma=sigma, lower=lower_filling_factors, 
                                                             upper=upper_filling_factors, 
                                                             shape=(self.reduced_dim),
                                                             initval=initval_filling_factors) 
      elif prior_distribution_filling_factors=='Uniform' :
        if initval_filling_factors is None : 
          initval_filling_factors = np.full (self.reduced_dim, lower_filling_factors+1e-32)
        self.FillingFactorsReducedPyMC = pm.Uniform ('filling_factors', lower=lower_filling_factors, 
                                                     upper=upper_filling_factors, 
                                                     shape=(self.reduced_dim), 
                                                     initval=initval_filling_factors) 
      else :
        raise Exception ("Unknown requested distribution for prior_distribution_filling_factors.")
      self.FillingFactorsExpandedPyMC = expand_tensor (self.FillingFactorsReducedPyMC, 
                                                       self.reduced_dim, self.large_dim) 
      
      # Light curve 
      lc = self.generateLightCurve (timestamps, use_numba=False, use_pymc=True, 
                                    zero_mean=zero_mean)
      Y_obs = pm.Normal("Y_obs", mu=lc, sigma=err_data, observed=lc_data)

      # Entropy function
      if maximum_entropy :
        lambda_S = _entropy_function_pymc (self.FillingFactorsReducedPyMC,
                                           self.areaReduced,
                                           lambda_me=lambda_me,
                                           m_norm=lower_filling_factors)
        exp_lambda_S = pm.Potential ('lambda_S', lambda_S) 

      if use_map :
        # Perform a simple maximum a posteriori exploration
        # instead of a mcmc sampling
        result = pm.find_MAP (maxeval=maxeval_map)
        # Postprocessing
        self.update_from_map_result (result, sample_omega=sample_omega,
                                sample_Q=sample_Q, sample_cf0=sample_cf0,
                                active_latitude=active_latitude,
                                summary_metric=summary_metric,
                                zero_mean=zero_mean)
      else :
        # Sampling and saving
        if nuts_sampler=='numpyro' :
          self.idata = sample_numpyro_nuts (**kwargs)
        elif nuts_sampler=='pymc' : 
          self.idata = pm.sample (**kwargs)
        else : 
          raise Exception ("Requested NUTS sampler does not exist or is not supported.")
        self.SamplingPerformed = True
        if filename is not None :
          self.idata.to_netcdf (filename)
        # Postprocessing
        self.update_from_idata (sample_omega=sample_omega,
                                sample_Q=sample_Q, sample_cf0=sample_cf0,
                                active_latitude=active_latitude,
                                summary_metric=summary_metric,
                                zero_mean=zero_mean)

      # The lcTensor attribute uses a lot of memory and
      # is not useful after sampling, therefore it seems
      # better to directly release the attribute here.
      self.lcTensor = None

      # Attaching the data to the object
      self.timestamps = timestamps
      self.lc_obs, self.err_obs = lc_data, err_data

    if use_map :
      return result
    else :
      return self.idata

  def update_from_idata (self, sample_omega=False, sample_Q=False,
                         sample_cf0=False, active_latitude=False,
                         summary_metric='mean', zero_mean=False) :
    '''
    Update the state of the Spot model using the sampled Inference
    Data.
    '''
    # Force lcTensor to be None on old model where it was not 
    # automatically the case at the end of the sampling
    self.lcTensor = None
    if not self.SamplingPerformed :
      raise Exception ("You must sample the model first.")
    if summary_metric=='max_proba' :
      (ff_s, omega_s, 
       Q_s, cf0_s, lambda_a_s) = _extract_max_posterior_idata (self.idata, sample_omega=sample_omega,
                                                              sample_Q=sample_Q, sample_cf0=sample_cf0,
                                                              active_latitude=active_latitude)
    else :
      if summary_metric!='mean' :
        warnings.warn ("Unknown metric, selecting mean.")
    (ff_s, omega_s, 
    Q_s, cf0_s, lambda_a_s) = _extract_mean_posterior_idata (self.idata, sample_omega=sample_omega,
                                                               sample_Q=sample_Q, sample_cf0=sample_cf0,
                                                               active_latitude=active_latitude)
    if active_latitude :
      self.lambda_a = lambda_a_s
    if sample_omega :
      self.omega = omega_s 
    if sample_Q :
      self.Q = Q_s 
    if sample_cf0 :
      self.cf0 = cf0_s 
    self.FillingFactorsReduced = ff_s
    self.FillingFactors = expand (self.FillingFactorsReduced,
                                  self.large_dim)
    self.generateLightCurve (self.timestamps, use_numba=False, zero_mean=zero_mean)

  def update_from_map_result (self, map_result, sample_omega=False, sample_Q=False,
                              sample_cf0=False, active_latitude=False,
                              summary_metric='mean', zero_mean=False,
                              multi_channel=False) :
    '''
    Update the state of the Spot model using the result of the MAP
    computation.
    '''
    self.FillingFactorsReduced = map_result["filling_factors"]
    self.FillingFactors = expand (self.FillingFactorsReduced,
                                  self.large_dim)
    if active_latitude :
      self.lambda_a = map_result["lambda_a"]
    if sample_omega :
      self.omega = map_result["omega"]
    if sample_Q :
      self.Q = map_result["Q"]
    if sample_cf0 :
      self.cf0 = map_result["cf0"]
    if not multi_channel :
      self.generateLightCurve (self.timestamps, use_numba=False, zero_mean=zero_mean)
    else :
      # Should be used only for the subclass SpotModelMultiChannel
      for channel in range (self.cs.size) :
        self.generateLightCurveMultiChannel (self.timestamps, zero_mean=zero_mean, 
                                             channel=channel)

  def hasDivergence (self) :
    '''
    Check if the idata corresponding to the sampled model
    has any divergence. 
    '''
    if not self.SamplingPerformed :
      raise Exception ("You must sample the model first.")
    return np.any (self.idata.sample_stats.diverging.to_numpy())

  def removeInferenceData (self) :
    '''
    When this function is called, replace existing ``self.idata``
    by ``None`` and reset ``self.SamplingPerformed`` attribute to
    ``False``. 
    '''
    self.idata = None 
    self.SamplingPerformed = False

  def removelcTensor (self) :
    '''
    When this function is called, replace existing ``self.lcTensor``
    by ``None``.
    '''
    self.lcTensor = None 

  def _eval_lc_tensor (self, timestamps, lc_data=None, err_data=1,
                       filling_factors_to_eval=None, filename=None,
                       sample_omega=True, omega_to_eval=None,
                       show=False, ppm=True) :
    '''
    A sanity check function to be sure that the light curve is correctly
    generated from the tensorial approach.

    Returns
    -------
    ndarray
      An array with the light curve evaluated from the computed ``pytensor`` 
      relation.
    '''
    if ppm :
      lc_data, err_data = lc_data*1e-6, err_data*1e-6

    sampling_model = pm.Model ()
    if filling_factors_to_eval is None :
      filling_factors_to_eval = reduce (self.FillingFactors, self.reduced_dim)
    if omega_to_eval is None :
      omega_to_eval = self.omega

    with sampling_model:
      if sample_omega :
        self.omegaPyMC = pm.Uniform ('omega', lower=self.omega-1e-9, 
                                              upper=self.omega+1e-9,
                                              initval=self.omega)
      else :
        self.omegaPyMC = self.omega
      self.FillingFactorsReducedPyMC = pm.Uniform ('filling_factors', lower=0, upper=1/(1+self.Q), 
                                                   shape=(self.reduced_dim)) 
      self.FillingFactorsExpandedPyMC = expand_tensor (self.FillingFactorsReducedPyMC, 
                                                       self.reduced_dim, self.large_dim) 
      lc = self.generateLightCurve (timestamps, use_numba=False, use_pymc=True)
      param_to_eval = {self.FillingFactorsReducedPyMC: filling_factors_to_eval}
      if sample_omega :
        param_to_eval[self.omegaPyMC] = omega_to_eval
      lc_eval = lc.eval (param_to_eval)

    if filename is not None :
      fig, ax = plt.subplots (1, 1)
      if lc_data is not None :
        ax.scatter (timestamps/86400, lc_data*1e6, 
                    color='darkorange', label='data')
      ax.scatter (timestamps/86400, lc_eval*1e6, facecolor='none', 
                  edgecolor='blue', label='tensor')
      ax.set_xlabel ('Time (day)')
      ax.set_ylabel ('Flux (ppm)')
      ax.legend ()
      plt.savefig (filename, dpi=300)
      if show :
        plt.show ()

    return lc_eval


@numba.njit (cache=True, parallel=True, fastmath=False)
def _generate_lightcurve (timestamps, large_dim, cos_i_cos_theta, sin_i_sin_theta,
                          longitudes, omega, t0, limb_darkening_coeff,
                          area, filling_factors, cf0=1, Q=1, cs=1) :
  '''
  Wrapper to generate a light curve from the spot model
  that can be enhanced with ``numba``.

  Returns
  -------
  tuple of arrays
    A tuple of arrays with the light curve, the ``mu``, ``visibility``
    ``unperturbed`` and ``flux_grid`` arrays (all of these corresponding
    to the last considered time stamp).
  '''
  lc = np.zeros (timestamps.size)
  visibility, mu = np.zeros (large_dim), np.zeros (large_dim) 
  flux_grid = np.zeros (large_dim) 
  for i in range (timestamps.size) :
    mu = sin_i_sin_theta * np.cos (longitudes + omega*(timestamps[i] - t0)) + cos_i_cos_theta 
    for j in range (visibility.shape[0]) :
      for k in range (visibility.shape[1]) :
        if mu[j,k] >=0 :
          visibility[j,k] = 1
        else :
          visibility[j,k] = 0
    unperturbed = (1 - limb_darkening_coeff[0] * (1-mu) - limb_darkening_coeff[1] * (1-mu)**2) * area * mu * visibility
    flux_grid = (1 + (cf0 * Q * (1-mu) - cs) * filling_factors) * unperturbed 
    lc[i] = np.sum (flux_grid) / np.sum (unperturbed) 

  return lc, mu, visibility, unperturbed, flux_grid 


def _generate_lightcurve_pymc (timestamps, large_dim, cos_i_cos_theta, sin_i_sin_theta,
                               longitudes, omega, t0, limb_darkening_coeff,
                               area, filling_factors, cf0=1, Q=1, cs=1,
                               zero_mean=True) :
  '''
  Tensorial expression of the light curve that will be used by pyMC. 

  Returns
  -------
  pytensor object
    The ``pytensor`` object needed to evaluate the light curve.
  '''
  if type (omega)==np.ndarray :
    omega = omega.reshape (1, *large_dim)
  if type (omega)!=pytensor.tensor.TensorVariable :
    # No tensor is created here, only numpy arrays
    visibility = np.zeros ((timestamps.size, *large_dim))
    mu = sin_i_sin_theta.reshape (1, *large_dim) * np.cos (
         longitudes.reshape (1, *large_dim) + omega * 
         (timestamps.reshape (timestamps.size, 1, 1) - t0)
         ) + cos_i_cos_theta.reshape (1, *large_dim) 
    visibility[mu>=0] = 1
    unperturbed = (1 - limb_darkening_coeff[0] * (1-mu) - 
                   limb_darkening_coeff[1] * (1-mu)**2) * area * mu * visibility
    # Creating the final tensors
    perturbed = (1 + (cf0 * Q * (1-mu) - cs) * filling_factors) * unperturbed 
    lc = pt.sum (perturbed, axis=(1,2)) / pt.sum (unperturbed, axis=(1,2)) 
  else :
    # Here mu is a tensor
    mu = pt.maximum (
         sin_i_sin_theta.reshape (1, *large_dim) * np.cos (
         longitudes.reshape (1, *large_dim) + omega * 
         (timestamps.reshape (timestamps.size, 1, 1) - t0)
         ) + cos_i_cos_theta.reshape (1, *large_dim),
         0
         ) 
    # Setting the visibility in a tensor-friendly way
    lc = pt.sum ( 
                (1 + (cf0 * Q * (1-mu) - cs) * filling_factors) *
                (1 - limb_darkening_coeff[0] * (1-mu) - 
                limb_darkening_coeff[1] * (1-mu)**2) * area * mu,
                axis=(1,2)) / pt.sum ( 
                 (1 - limb_darkening_coeff[0] * (1-mu) -
                limb_darkening_coeff[1] * (1-mu)**2) * area * mu, 
                axis=(1,2),
                 )
  if zero_mean :
    lc -= pt.mean (lc)
  return lc 

def _entropy_function_pymc (filling_factors, area, lambda_me=1, m_norm=1e-6) :
  '''
  Compute the tensor for the entropy function described in Lanza et al. 2016. 
  '''
  S = - area * (filling_factors * pt.log (filling_factors/m_norm) +
              (1-filling_factors) * pt.log ((1-filling_factors)/(1-m_norm)) )  
  lambda_S = lambda_me * pt.sum (S)
  return lambda_S

def precompute_generate_lightcurve_broadcast (timestamps, large_dim, cos_i_cos_theta, sin_i_sin_theta,
                                               longitudes, omega, t0, limb_darkening_coeff, area) :
  '''
  Pre-computing step for _generate_lightcurve_broadcast.
  '''
  if type (omega) not in [float, np.float_, int, np.int_] :
    #assuming this is an array
    omega = omega.reshape (1, *large_dim)
  visibility = np.zeros ((timestamps.size, *large_dim))
  mu = sin_i_sin_theta.reshape (1, *large_dim) * np.cos (
       longitudes.reshape (1, *large_dim) + omega * 
       (timestamps.reshape (timestamps.size, 1, 1) - t0)
       ) + cos_i_cos_theta.reshape (1, *large_dim) 
  visibility[mu>=0] = 1
  unperturbed = (1 - limb_darkening_coeff[0] * (1-mu) - limb_darkening_coeff[1] * (1-mu)**2) * area * mu * visibility
  unperturbed_sum = np.sum (unperturbed, axis=1)

  return mu, visibility, unperturbed, unperturbed_sum

def _generate_lightcurve_broadcast (mu, visibility, unperturbed, unperturbed_sum,
                                    filling_factors, cf0=1, Q=1, cs=1) :
  '''
  Light-curve generation procedure taking advantage of the pre-computation
  of some term to minimise the number of operation to perform when running
  an optimisation.
  '''
  perturbed = (1 + (cf0 * Q * (1-mu) - cs) * filling_factors) * unperturbed 
  lc = np.sum (perturbed, axis=(1,2)) / unperturbed_sum
  return lc 

def _extract_max_posterior_idata (idata, sample_omega=False,
                                  sample_Q=False, sample_cf0=False,
                                  active_latitude=False) :
  '''
  Take an ``InferenceData`` object and return the values
  corresponding to the maximal probability of the 
  sampled distribution.
  ''' 
  log_proba = idata.sample_stats.lp.to_numpy ().reshape (-1)
  indexes = np.argmax (log_proba)
  ff = idata.posterior.filling_factors.to_numpy ()
  ff = ff.reshape (-1, ff.shape[2], ff.shape[3])
  ff_max = ff[indexes,:,:]
  if sample_omega :
    omega = idata.posterior.omega.to_numpy ().reshape (-1)
    omega_max = omega[indexes]
  else :
    omega_max = None
  if sample_Q :
    Q = idata.posterior.Q.to_numpy ().reshape (-1)
    Q_max = Q[indexes]
  else :
    Q_max = None
  if sample_cf0 :
    cf0 = idata.posterior.cf0.to_numpy ().reshape (-1)
    cf0_max = cf0[indexes]
  else :
    Q_max = None
  if active_latitude :
    lambda_a = idata.posterior.lambda_a.to_numpy ().reshape (-1)
    lambda_a_max = lambda_a[indexes]
  else :
    lambda_a_max = None 
  return (ff_max, omega_max, Q_max, cf0_max, lambda_a_max)  

def _extract_mean_posterior_idata (idata, sample_omega=False,
                                   sample_Q=False, sample_cf0=False,
                                   active_latitude=False) :
  '''
  Take an ``InferenceData`` object and return the values
  corresponding to the mean value of the 
  sampled distribution.
  ''' 
  if active_latitude :
    lambda_a = idata.posterior['lambda_a'].to_numpy().mean ()
  else :
    lambda_a = None
  if sample_omega :
    omega = idata.posterior['omega'].to_numpy().mean ()
  else :
    omega = None
  if sample_Q :
    Q = idata.posterior['Q'].to_numpy().mean ()
  else :
    Q = None
  if sample_cf0 :
    cf0 = idata.posterior['cf0'].to_numpy().mean ()
  else :
    cf0 = None
  ff = idata.posterior.filling_factors.to_numpy ()
  ff = ff.reshape (-1, ff.shape[2], ff.shape[3]).mean (axis=0)
  return ff, omega, Q, cf0, lambda_a
