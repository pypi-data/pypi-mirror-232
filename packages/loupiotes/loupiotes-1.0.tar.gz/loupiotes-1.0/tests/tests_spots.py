import unittest
import warnings
import importlib.resources
from astropy.io import fits
import numpy as np
import os
import loupiotes
import time
from loupiotes.spots import *
import matplotlib.pyplot as plt
from tqdm import tqdm
import arviz as az


class IOTest (unittest.TestCase) :
 
  def testSaveLoad (self) :
    spotmodel = SpotModel () 
    filename = 'test_outputs/spotmodel_testsave'
    spotmodel.save (filename)
    spotmodel = load_spot_model (filename)

#@unittest.skip 
class UnperturbedTest (unittest.TestCase) :

  def setUp (self) :
    if not os.path.exists ('test_outputs') :
      os.mkdir ('test_outputs')
    self.spotmodel = SpotModel (large_dim=(180,180))
    self.spotmodel_2 = SpotModel (large_dim=(18,18))

  def testExpand (self) :
    a = np.array ([[1, 2],
                   [3, 4]]) 
    large_dim = (4, 6)
    ref = np.array ([[1, 1, 1, 2, 2, 2],
                     [1, 1, 1, 2, 2, 2],
                     [3, 3, 3, 4, 4, 4],
                     [3, 3, 3, 4, 4, 4]])
    expanded = loupiotes.spots.expand (a, large_dim)
    self.assertTrue (np.all (expanded-ref)==0) 

  def testUnperturbedLightCurve (self) :
    timestamps = np.linspace (0, 30*86400, 1000)
    lc = np.zeros (timestamps.size)
    lc_2 = np.zeros (timestamps.size)
    for ii, t in enumerate (timestamps) :
      self.spotmodel.updateVisibility (t)
      self.spotmodel_2.updateVisibility (t)
      lc[ii] = self.spotmodel.computeUnperturbedFlux () 
      lc_2[ii] = self.spotmodel_2.computeUnperturbedFlux () 
    fig, ax = plt.subplots (1, 1)
    ax.plot (timestamps/86400, lc, color='black', label='{}'.format (self.spotmodel.large_dim))
    ax.plot (timestamps/86400, lc_2, color='darkorange', label='{}'.format (self.spotmodel_2.large_dim))
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    ax.legend ()
    plt.savefig ('test_outputs/unperturbed_lc.png', dpi=300)

#@unittest.skip
class FFTest (unittest.TestCase) :

  def setUp (self) :
    if not os.path.exists ('test_outputs') :
      os.mkdir ('test_outputs')
    filling_factors = random_filling_factor () 
    self.spotmodel = SpotModel (large_dim=(180,180),
                                filling_factors=filling_factors)

  #@unittest.skip 
  def testLightCurve_1 (self) :
    timestamps = np.linspace (0, 300*86400, 1000)
    lc_u = np.zeros (timestamps.size)
    lc = np.zeros (timestamps.size)
    for ii, t in enumerate (timestamps) :
      self.spotmodel.updateVisibility (t)
      lc_u[ii] = self.spotmodel.computeUnperturbedFlux () 
      lc[ii] = self.spotmodel.computeObservedFlux () 
    fig, ax = plt.subplots (1, 1)
    ax.plot (timestamps/86400, lc_u, color='black', label='Unperturbed')
    ax.plot (timestamps/86400, lc, color='darkorange', label='Observed')
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    ax.legend ()
    plt.savefig ('test_outputs/fftest_lc_1.png', dpi=300)

  #@unittest.skip
  def testLightCurve_2 (self) :
    timestamps = np.linspace (0, 300*86400, 1000)
    lc = self.spotmodel.generateLightCurve (timestamps, use_numba=True)
    fig, ax = plt.subplots (1, 1)
    ax.plot (timestamps/86400, lc, color='darkorange', label='Observed')
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    ax.legend ()
    plt.savefig ('test_outputs/fftest_lc_2.png', dpi=300)

  #@unittest.skip 
  def testLightCurveImplementations (self) :
    timestamps = np.linspace (0, 300*86400, 100)
    lc_1 = self.spotmodel.generateLightCurve (timestamps, use_numba=True)
    lc_2 = self.spotmodel.generateLightCurve (timestamps, use_numba=False)
    self.assertTrue (np.all (np.abs (lc_1-lc_2)<1e-6))

  def testLightCurveSpeed (self) :
    timestamps = np.linspace (0, 300*86400, 100)
    start_time = time.time () 
    lc = self.spotmodel.generateLightCurve (timestamps, use_numba=True)
    elapsed = time.time () - start_time
    print ('Light curve computed with numba in {:.2f} s'.format (elapsed))
    start_time = time.time () 
    lc = self.spotmodel.generateLightCurve (timestamps, use_numba=False)
    elapsed = time.time () - start_time
    print ('Light curve computed without numba in {:.2f} s'.format (elapsed))

  #@unittest.skip 
  def testGaussianNoiseLC (self) :
    timestamps = np.linspace (0, 300*86400, 1000)
    lc, err_obs, noise_free = gaussian_noise_lc (timestamps, seed=1348942, std=0.05)
    fig, ax = plt.subplots (1, 1)
    ax.plot (timestamps/86400, lc, color='black')
    ax.plot (timestamps/86400, noise_free, color='darkorange')
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    plt.savefig ('test_outputs/fftest_noise.png', dpi=300)

#@unittest.skip 
class FitTest (unittest.TestCase) :

  #@unittest.skip
  def testGenerator (self) :
    reduced_dim = (18,18)
    large_dim = (180,180)
    timestamps = np.linspace (0, 90*86400, 100)
    distribution = 'uniform'
    lc_to_fit, err_obs, noise_free, spotmodel_ref = gaussian_noise_lc (timestamps, reduced_dim=reduced_dim,
                                                              seed=13489, std=0.01, scale=0.01,
                                                              large_dim=large_dim, boost_std=2.,
                                                              distribution=distribution,
                                                              return_object=True)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False,
                            filename='test_outputs/fluxgrid_ref.png', dpi=300)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False, projection='mercator',
                            filename='test_outputs/fluxgrid_ref_projected.png', dpi=300)
    # Changing inclination 
    lc_to_fit, err_obs, noise_free, spotmodel_ref = gaussian_noise_lc (timestamps, reduced_dim=reduced_dim,
                                                              seed=13489, std=0.01, inclination=45,
                                                              large_dim=large_dim, distribution=distribution,
                                                              return_object=True)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False, plot_unperturbed=True,
                            filename='test_outputs/fluxgrid_unperturbed_inclined.png', dpi=300)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False,
                            filename='test_outputs/fluxgrid_ref_inclined.png', dpi=300)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False, projection='mercator',
                            filename='test_outputs/fluxgrid_ref_inclined_projected.png', dpi=300)
    spotmodel_ref.plotGrid (figsize=(6,6),
                            show=False, vmin=0, vmax=0.5,
                            filename='test_outputs/filling_factors_inclined_ref.png', dpi=300)
    spotmodel_ref.plotGrid (figsize=(6,6), vmin=0, vmax=0.5,
                            show=False, projection='mercator',
                            filename='test_outputs/filling_factors_inclined_projected_ref.png', dpi=300)

  def testLCTensor (self) :
    large_dim, reduced_dim = (180, 180), (18,18)
    err_data, scale = 0.001, 0.01
    distribution = 'boosted'
    timestamps = np.linspace (0, 30*86400, 50)
    seed = 1348942
    lc_data, err_obs, noise_free, spotmodel_ref = gaussian_noise_lc (timestamps, large_dim=large_dim,
                                                              reduced_dim=reduced_dim,
                                                              seed=seed, std=err_data, scale=scale,
                                                              distribution=distribution, boost_std=2,
                                                              return_object=True)
    ff = random_filling_factor (reduced_dim=reduced_dim,
                           distribution=distribution,
                           seed=seed, boost_std=2, 
                           scale=scale)
    spotmodel = SpotModel (reduced_dim=reduced_dim, large_dim=large_dim)
    lc_eval = spotmodel._eval_lc_tensor (timestamps, noise_free, err_data=err_data,
                                         filling_factors_to_eval=ff, 
                                         filename='test_outputs/lctensor_test.png',
                                         sample_omega=True)
    self.assertTrue (np.all (np.abs (lc_eval-noise_free*1e-6)<1e-6))

  @unittest.skip 
  def testMCMC (self) :
    inclination, Q = 45, 0.1
    large_dim, reduced_dim = (18, 18), (6,6) 
    #large_dim, reduced_dim = (72, 72), (18,18) 
    err_data, scale = 0.001, 0.01  
    distribution = 'boosted'
    timestamps = np.linspace (0, 30*86400, 50)
    prior = 'Uniform'
    lc_to_fit, err_obs, noise_free, spotmodel_ref = gaussian_noise_lc (timestamps, large_dim=large_dim,
                                                              reduced_dim=reduced_dim, 
                                                              seed=1389437942, std=err_data, scale=scale, 
                                                              distribution=distribution, boost_std=2,  
                                                              return_object=True, inclination=inclination,
                                                              Q=Q)
    spotmodel_ref.plotFluxGrid (figsize=(6,6),
                            show=False,
                            filename='test_outputs/fluxgrid_final_mcmc_ref.png', dpi=300)
    spotmodel_ref.plotGrid (figsize=(6,6),
                            show=False, 
                            filename='test_outputs/filling_factors__mcmc_ref.png', dpi=300)
    spotmodel_ref.plotGrid (figsize=(6,6), 
                            show=False, projection='mercator',
                            filename='test_outputs/filling_factors_projected__mcmc_ref.png', dpi=300)
    fig, ax = plt.subplots (1, 1)
    ax.errorbar (timestamps/86400, lc_to_fit, yerr=err_data,
                 fmt='o', color='black', markerfacecolor='none', 
                 markeredgecolor='black', capsize=4,
                 zorder=-1)
    ax.plot (timestamps/86400, noise_free, color='blue')
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    plt.savefig ('test_outputs/lc_mcmc_ref.png', dpi=300)
    spotmodel = SpotModel (reduced_dim=reduced_dim, large_dim=large_dim,
                           inclination=inclination, Q=Q)
    idata = spotmodel.explore_distribution (timestamps, lc_to_fit, err_data=err_data,
                                            sigma=0.1, draws=1000, tune=1000, 
                                            maximum_entropy=True, lambda_me=10,
                                            prior_distribution_filling_factors=prior,
                                            filename='test_outputs/mcmc_distribution_arviz_prior_{}_{}_{}_{}_{}'.format (
                                            prior, *large_dim, *reduced_dim))
    fig, ax = plt.subplots (1, 1)
    ax.errorbar (timestamps/86400, lc_to_fit, yerr=err_data,
                 fmt='o', color='black', markerfacecolor='none', 
                 markeredgecolor='black', capsize=4,
                 zorder=-1)
    ax.plot (timestamps/86400, noise_free, color='blue')
    ax.plot (timestamps/86400, spotmodel.lc, color='darkorange')
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel ('Flux (arbitrary units)')
    plt.savefig ('test_outputs/mcmc_fit.png', dpi=300)
    spotmodel.plotFluxGrid (figsize=(6,6),
                            show=False,
                            filename='test_outputs/fluxgrid_final_mcmc.png', dpi=300)
    spotmodel.plotGrid (figsize=(6,6),
                        show=False,  
                        filename='test_outputs/filling_factors_mcmc.png', dpi=300)
    spotmodel.plotGrid (figsize=(6,6), 
                        show=False, projection='mercator',
                        filename='test_outputs/filling_factors_projected_mcmc.png', dpi=300)

if __name__ == '__main__' :
  print ('Testing loupiotes v{}, located at {}'.format (loupiotes.__version__, loupiotes.__file__))
  unittest.main(verbosity=2)

