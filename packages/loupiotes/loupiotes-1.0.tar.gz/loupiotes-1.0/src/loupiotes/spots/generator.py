import numpy as np
import loupiotes
import warnings

'''
A set of parameter generator to use
with the SpotModel class.
'''

def random_filling_factor (reduced_dim=(18,18), 
                           distribution='normal',
                           rng=None, seed=None,
                           scale=0.1, max_factor=None,
                           Q=1, boost_std=3) :
  '''
  Draw filling factors from the grid with a probabilistic
  distribution (between 0 and 1).
  '''
  if max_factor is None :
    max_factor = 1 / (1+Q)
  if (1 + Q) * max_factor > 1 :
    max_factor = 1 / (1+Q)
    warnings.warn ("(1+Q)*max_factor cannot be larger than 1, max_factor set to 1/(1+Q)") 
  if rng is None :
      rng = np.random.default_rng(seed)
  if distribution=='uniform' :
    filling_factors = max_factor * rng.uniform (size=reduced_dim)
  elif distribution=='normal' :
    filling_factors = rng.normal (loc=0, scale=scale,
                                  size=reduced_dim)
    filling_factors = np.abs (filling_factors)
    filling_factors[filling_factors>max_factor] = max_factor
  elif distribution=='boosted' :
    filling_factors = rng.normal (loc=0, scale=scale,
                                  size=reduced_dim)
    filling_factors = np.abs (filling_factors)
    filling_factors[filling_factors>boost_std*scale] = max_factor
  else :
    raise Exception ("Unknown distribution.")
  return filling_factors

def gaussian_noise_lc (timestamps, seed=None, distribution='normal', 
                       std=0.01, scale=0.05, large_dim=(180,180),
                       reduced_dim=(18,18), inclination=90, Q=1, 
                       return_object=False, boost_std=3, ppm=False,
                       zero_mean=False, use_numba=False, 
                       omega=2.6e-6, cs=1, cf0=1,
                       limb_darkening_coeff=None) :
  '''
  Generate a light curve with Gaussian noise
  from a SpotModel object. By default, the light curve is 
  normalised in ppm. 

  Returns
  -------
    Returns noisy light curve, observation uncertainty
    (computed as ``std``, renormalised if necessary) 
    and noise free light curves and, if ``return_object`` 
    is set to ``True``, the Spot Model object that was 
    used to generate them.
  '''
  rng = np.random.default_rng(seed)
  filling_factors = random_filling_factor (reduced_dim=reduced_dim, 
                                           distribution=distribution,
                                           rng=rng, scale=scale, 
                                           boost_std=boost_std, Q=Q)
  spotmodel = loupiotes.spots.SpotModel (large_dim=large_dim,
                              reduced_dim=reduced_dim, inclination=inclination,
                              filling_factors=filling_factors, Q=Q, cs=cs, cf0=cf0,
                              limb_darkening_coeff=limb_darkening_coeff, omega=omega)
  noise_free = spotmodel.generateLightCurve (timestamps, zero_mean=zero_mean,
                                             use_numba=use_numba)
  # Creating Gaussian noise
  noise = rng.normal(size=timestamps.size, scale=std)
  lc = noise_free + noise
  if ppm :
    lc, err_obs, noise_free = lc*1e6, std*1e6, noise_free*1e6
  else :
    err_obs = std
  # Bounding the synthetic data with error to the spotmodel
  spotmodel.lc_obs = lc
  spotmodel.err_obs = err_obs

  if return_object :
    return lc, err_obs, noise_free, spotmodel
  else :
    return lc, err_obs, noise_free
