import numpy as np
import warnings
try :
  import pymc as pm
  import pytensor
  import pytensor.tensor as pt
  import arviz as az
except ImportError :
  pass
try :
  import jax
  from pymc.sampling.jax import sample_numpyro_nuts
  import tensorflow_probability.substrates.jax as tfp
  jax.scipy.special.erfcx = tfp.math.erfcx
except ImportError :
  pass
from .spotmodel import *

class SpotModelMultiChannel (SpotModel) :
  '''
  A subclass of spotmodels that allow analysing 
  simultaneously multiwavelength observations.
  '''
  def __init__ (self, large_dim=(180,180), reduced_dim=(18,18),
                inclination=90, t0=0, omega=2.6e-6, filling_factors=None,
                limb_darkening_coeff=None, Q=0, cf0=[1,1], cs=[1,1],
                id_channel=None) :
    '''
    Initialise the ``SpotModelMultiChannel`` object.
    '''
    super ().__init__ (large_dim=large_dim, reduced_dim=reduced_dim,
                inclination=inclination, t0=t0, omega=omega, filling_factors=filling_factors,
                limb_darkening_coeff=None, Q=Q, cf0=1, cs=1)
    self.cs = np.array (cs)
    self.n_channels = self.cs.size
    # Overriding facular contrast when necessary
    if type (cf0) in (int, float) :
      self.cf0 = np.full (self.n_channels, cf0) 
    elif self.n_channels!=len (cf0) :
      raise Exception ("You must provide the same number of contrast parameters for spots and faculae.")
    else :
      self.cf0 = np.array (cf0)
    # Setting limb-darkening coefficients
    if limb_darkening_coeff is None :
      # Using auto-generated value of the standard spotmodel
      aux = np.array (self.limb_darkening_coeff)
      self.limb_darkening_coeff = np.repeat (aux.reshape (-1, aux.size),
                                                     self.n_channels, axis=0) 
    elif len (np.array (limb_darkening_coeff).shape)==1 :
      aux = np.array (limb_darkening_coeff)
      self.limb_darkening_coeff = np.repeat (aux.reshape (-1, aux.size),
                                             self.n_channels, axis=0) 
    elif np.array (limb_darkening_coeff).shape[0]!=self.n_channels:
      raise Exception ("You must provide a limb-darkening parameter array with size consistent with the number of channels")
    else :
      self.limb_darkening_coeff = np.array (limb_darkening_coeff)
    if id_channel is None :
      self.id_channel = np.arange (self.n_channels)
    elif np.array (id_channel).shape[0]!=self.n_channels:
      raise Exception ("You must provide a id_channel with size consistent with the number of channels")
    else :
      self.id_channel = np.array (id_channel) 
    self.lc = [None for ii in range (self.n_channels)]
    self.lcTensor = [None for ii in range (self.n_channels)]

    # Auxiliary parameter useful to compute light curves fast
    # (For some reason the "__" syntax makes them inaccessible even
    # here when initialised through the SpotModel parent class)
    self.__cos_i_cos_theta = np.cos (self.inclination) * np.cos (self.colatitudes)
    self.__sin_i_sin_theta = np.sin (self.inclination) * np.sin (self.colatitudes)

    # Compute the initial values of the grids 
    self.updateVisibilityChannel (self.t0)
    self.computeUnperturbedFlux ()
    self.computeObservedFlux ()

  def computeUnperturbedChannel (self, channel=0) :
    '''
    Compute the unperturbed flux grid taking into account
    limb-darkening effects (using a quadratic law) for
    a given channel. 

    Returns
    -------
    ndarray
      A view of the unperturbed grid in the chosen channel.
    '''
    aux = 1 - self.mu
    self.Unperturbed = 1 - self.limb_darkening_coeff[channel,0] * aux - \
                       self.limb_darkening_coeff[channel,1] * aux**2
    self.Unperturbed = self.Unperturbed * self.area * self.mu * self.visibility
    return self.Unperturbed


  def computeFluxGridChannel (self, channel=0) :
    '''
    Compute the flux grid from the unperturbed reference,
    taking into account spot and facula coverage of a given
    channel. The corresponding flux grid is saved as the
    ``FluxGrid`` attribute of the model and will therefore
    override the previous computed flux grid.

    Returns
    -------
    ndarray
      A view of the updated flux grid.
    '''
    aux = 1 + (self.cf0[channel] * self.Q * (1-self.mu) - self.cs[channel]) * self.FillingFactors
    self.FluxGrid = aux * self.Unperturbed
    return self.FluxGrid

  def updateVisibilityChannel (self, t, channel=0) :
    '''
    Update arrays at a time t for channel ``channel``.

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
    unperturbed = self.computeUnperturbedChannel (channel=channel)
    fluxgrid = self.computeFluxGridChannel (channel=channel)
    return self.mu, self.visibility, unperturbed, fluxgrid


  def generateLightCurveMultiChannel (self, timestamps, use_pymc=False, 
                                      zero_mean=False, channel=0) :
    '''
    Generate multi-wavelength light curves.
    '''
    self.timestamps = timestamps
    if use_pymc :
      self.lcTensor[channel] = _generate_lightcurve_pymc_multi_channel (self.timestamps, self.large_dim,
                            self.__cos_i_cos_theta, self.__sin_i_sin_theta,
                            self.longitudes, self.omegaPyMC, self.t0,
                            self.limb_darkening_coeff, self.area,
                            self.FillingFactorsExpandedPyMC,
                            self.cf0PyMC, self.QPyMC, self.cs,
                            zero_mean=zero_mean, channel=channel)
      return self.lcTensor[channel]
    else :
      lc = np.zeros (timestamps.size)
      for ii, t in enumerate (timestamps) :
        self.updateVisibilityChannel (t, channel=channel)
        lc[ii] = self.computeObservedFlux ()
        if zero_mean :
          lc -= np.mean (lc)
      self.lc[channel] = lc
      return self.lc[channel]

  def explore_distribution (self, timestamps, lc_data, err_data=1,
                            prior_distribution_filling_factors='Uniform',
                            prior_omega='TruncatedNormal',
                            sigma=0.1, active_latitude=False, beta=1,
                            upper_active_latitude=60, filename=None,
                            maximum_entropy=False, lambda_me=1,
                            new_sampling=True, lower_filling_factors=None,
                            sample_omega=False, sigma_omega=None, ppm=True,
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
      List of arrays, each one containing the observed values in
      one channel. 

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
    if len (lc_data) != self.n_channels :
      raise Exception ("An observed light curve per channel must be provided.")

    if not new_sampling and self.SamplingPerformed:
      self.update_from_idata (sample_omega=sample_omega,
                              active_latitude=active_latitude,
                              summary_metric=summary_metric,
                              zero_mean=zero_mean)
      return self.idata
      
    if type (err_data) in [int, float] :
          err_data = np.full (self.n_channels, err_data)

    if ppm :
      for ii in range (self.n_channels) : 
        lc_data[ii], err_data[ii] = lc_data[ii]*1e-6, err_data[ii]*1e-6
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
        self.cf0PyMC = pm.Uniform ('cf0', dims=self.cf0.shape, lower=lower_cf0,
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
                                                             shape=(self.reduced_dim))
      elif prior_distribution_filling_factors=='Uniform' :
        initval = np.full (self.reduced_dim, lower_filling_factors+1e-32)
        self.FillingFactorsReducedPyMC = pm.Uniform ('filling_factors', lower=lower_filling_factors,
                                                     upper=upper_filling_factors,
                                                     shape=(self.reduced_dim), initval=initval)
      else :
        raise Exception ("Unknown requested distribution for prior_distribution_filling_factors.")
      self.FillingFactorsExpandedPyMC = expand_tensor (self.FillingFactorsReducedPyMC,
                                                       self.reduced_dim, self.large_dim)
      # Light curves 
      for ii in range (self.n_channels) :
        lc = self.generateLightCurveMultiChannel (timestamps, use_pymc=True,
                                                  zero_mean=zero_mean, channel=ii)
        _ = pm.Normal("Y_obs_channel_{}".format(ii), 
                      mu=lc, sigma=err_data[ii], observed=lc_data[ii])

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
                                zero_mean=zero_mean, multi_channel=True)
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
        # TODO The function below needs to be updated
        # to account for the multidimensionality of the data
        self.update_from_idata (sample_omega=sample_omega,
                                sample_Q=sample_Q, sample_cf0=sample_cf0,
                                active_latitude=active_latitude,
                                summary_metric=summary_metric,
                                zero_mean=zero_mean)

      # The lcTensor attribute uses a lot of memory and
      # is not useful after sampling, therefore it seems
      # better to directly release the attribute here.
      self.lcTensor = [None for ii in range (self.n_channels)]

      # Attaching the data to the object
      self.timestamps = timestamps
      self.lc_obs, self.err_obs = lc_data, err_data

    if use_map :
      return result
    else :
      return self.idata

  def precomputeBroadcast (self, channel=0) :
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
                    self.limb_darkening_coeff[channel], self.area,
                    )
    self.BroadcastPrecomputed = True


  
def _generate_lightcurve_pymc_multi_channel (timestamps, large_dim, cos_i_cos_theta, sin_i_sin_theta,
                                             longitudes, omega, t0, limb_darkening_coeff,
                                             area, filling_factors, cf0, Q, cs, channel=0,
                                             zero_mean=True) :
  '''
  Tensorial expression of one channel of the multi_wavelength 
  light curve that will be used by pyMC. 

  Returns
  -------
  pytensor object
    The ``pytensor`` object needed to evaluate the light curve
    in the corresponding ``channel``.
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
    unperturbed = (1 - limb_darkening_coeff[channel,0] * (1-mu) -
                   limb_darkening_coeff[channel,1] * (1-mu)**2) * area * mu * visibility
    # Creating the final tensors
    perturbed = (1 + (cf0[channel] * Q * (1-mu) - cs[channel]) * filling_factors) * unperturbed
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
    for channel in range (cs.size) : 
      lc = pt.sum (
                  (1 + (cf0[channel] * Q * (1-mu) - cs[channel]) * filling_factors) *
                  (1 - limb_darkening_coeff[0] * (1-mu) -
                  limb_darkening_coeff[channel,1] * (1-mu)**2) * area * mu,
                  axis=(1,2)) / pt.sum (
                   (1 - limb_darkening_coeff[channel,0] * (1-mu) -
                  limb_darkening_coeff[channel,1] * (1-mu)**2) * area * mu,
                  axis=(1,2),
                   )
  if zero_mean :
      lc -= pt.mean (lc)
  return lc
