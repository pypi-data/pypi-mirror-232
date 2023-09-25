import unittest
import warnings
import importlib.resources
from astropy.io import fits
import numpy as np
import os
import loupiotes
from loupiotes import *
import matplotlib.pyplot as plt

class MainTest (unittest.TestCase) :

  def setUp (self) :
    if not os.path.exists ('test_outputs') :
      os.mkdir ('test_outputs')
    return

  @unittest.skip
  def testLoadTables (self) :
    df = loupiotes.tables.load_limb_darkening_table (name='sing_2010_kepler')
    df = restrict_df (df)

  @unittest.skip
  def testInterpolation (self, show=True) :
     coord, grid = compute_grid (0)
     I = interpolate_I (coord, grid)
     dI_dlnTeff = interpolate_dI_dlnTeff (coord, grid)
     dI_dlng = interpolate_dI_dlng (coord, grid)
     print (I, dI_dlnTeff, dI_dlng)
     a_teff, a_I, a_dI_dlnTeff = get_teff_gradient (coord, grid)
     if show :
       fig, (ax1, ax2) = plt.subplots (1, 2, figsize=(8,4))
       ax1.plot (a_teff, a_I, '-x', color='black')
       ax2.plot (a_teff, a_dI_dlnTeff, '-x', color='black')
       plt.savefig ('test_outputs/grad_teff.png')
     a_logg, a_I, a_dI_dlng = get_logg_gradient (coord, grid)
     if show :
       fig, (ax1, ax2) = plt.subplots (1, 2, figsize=(8,4))
       ax1.plot (a_logg, a_I, '-x', color='black')
       ax2.plot (a_logg, a_dI_dlng, '-x', color='black')
       plt.savefig ('test_outputs/grad_logg.png')

  @unittest.skip
  def testIntensityMap (self) :
     mu, a1, a2, a3 = compute_intensity_latitudinal (nbin=30)
     I_0_1 = compute_integral (mu, a1)
     I_0_2 = compute_integral (mu, a2)
     I_0_3 = compute_integral (mu, a3)
     V_0, V_1, V_2, V_3, V_4 = (compute_V_l_ballot_2011 (mu, a1, l=0),
                           compute_V_l_ballot_2011 (mu, a1, l=1), 
                           compute_V_l_ballot_2011 (mu, a1, l=2), 
                           compute_V_l_ballot_2011 (mu, a1, l=3),
                           compute_V_l_ballot_2011 (mu, a1, l=4))
     V_l = np.array ([V_0, V_1, V_2, V_3, V_4])
     print (V_0)
     print ((V_l/V_0)**2)

  @unittest.skip
  def testVariabilityTownsend (self) :
     l = 3
     V_l = compute_variability_factor_townsend_2003 (3000, nbin=30, l=l)
     V_0 = compute_variability_factor_townsend_2003 (3000, nbin=30, l=0)
     dr_r = compute_displacement (3000)
     print ("Townsend 2003 formalism, l = {}".format(l))
     print (V_0, V_l, dr_r, V_l*dr_r*1e6, V_0*dr_r*1e6, (V_l / V_0)**2)

  @unittest.skip
  def testVariabilityBerthomieuProvost (self) :
     l = 1
     V_l = compute_variability_factor_berthomieu_provost_1990 (3000, nbin=30, l=l)
     dF_F = compute_dF_F_berthomieu_provost_1990 (3000, nbin=30, l=l)
     dF_F_0 = compute_dF_F_berthomieu_provost_1990 (3000, nbin=30, l=0)
     dr_R = compute_dr_R_berthomieu_provost_1990 (3000, nbin=30, l=l)
     print ("Berthomieu & Provost 1990 formalism, l = {}".format(l))
     print (dF_F_0*1e6, dF_F*1e6, (dF_F/dF_F_0)**2)

  @unittest.skip
  def testCancellationFrequencyProvost (self) :
     omega_c = compute_cancellation_frequency (l=1)
     nu_c = unreduce_frequency (omega_c, r=1, mass=1)
     print (omega_c)
     print (nu_c)

  @unittest.skip
  def test_Gfunction (self) :
     nu = np.linspace (10, 150, 100)
     l = 1
     G_xs = compute_G_xs_ad_function (nu, r=1, mass=1, l=1, nabla_ad=0.4)
     dF_F = compute_dF_F_berthomieu_provost_1990 (nu, nbin=30, l=l)
     fig, (ax1, ax2) = plt.subplots (2, 1, figsize=(8,8))
     ax1.plot (nu, np.abs (G_xs), color='black')
     ax1.set_xlabel (r'$\nu$ ($\mu$Hz)')
     ax1.set_ylabel (r'$|G|$')
     ax1.set_yscale ('log')
     ax2.plot (nu, np.abs (dF_F), color='black')
     ax2.set_xlabel (r'$\nu$ ($\mu$Hz)')
     ax2.set_ylabel (r'$|dF/F|$')
     ax2.set_yscale ('log')
     plt.savefig ('test_outputs/G_dF_F_function.png', dpi=300)
     mu, I = compute_intensity_latitudinal (nbin=30, only_I=True)
     b_l = compute_b_l_integral (mu, I, l=l)
     c_l = compute_c_l_integral (mu, I, l=l)  
     print (2*b_l - c_l)

  @unittest.skip
  def testVobsBerthomieuProvosti_pmodes (self) :
     Vobs_0 = compute_Vobs_berthomieu_provost_1990 (3000, nbin=30, l=0)
     Vobs_1 = compute_Vobs_berthomieu_provost_1990 (3000, nbin=30, l=1)
     Vobs_2 = compute_Vobs_berthomieu_provost_1990 (3000, nbin=30, l=2)
     Vobs_3 = compute_Vobs_berthomieu_provost_1990 (3000, nbin=30, l=3)
     Vobs_4 = compute_Vobs_berthomieu_provost_1990 (3000, nbin=30, l=4)
     print (Vobs_0, Vobs_1, Vobs_2, Vobs_3, Vobs_4)
     print ((Vobs_1/Vobs_0)**2, 
            (Vobs_2/Vobs_0)**2,
            (Vobs_3/Vobs_0)**2,
            (Vobs_4/Vobs_0)**2)      

  def testVobsBerthomieuProvost_gmodes (self) :
     Vobs_1 = compute_Vobs_berthomieu_provost_1990 (50, nbin=30, l=1)
     Vobs_2 = compute_Vobs_berthomieu_provost_1990 (50, nbin=30, l=2)
     Vobs_3 = compute_Vobs_berthomieu_provost_1990 (50, nbin=30, l=3)
     Vobs_4 = compute_Vobs_berthomieu_provost_1990 (50, nbin=30, l=4)
     P_1_1 = observer_factor (l=1, m=1, theta_0=90)
     P_2_0 = observer_factor (l=2, m=0, theta_0=90)
     P_3_1 = observer_factor (l=3, m=1, theta_0=90)
     P_4_0 = observer_factor (l=4, m=0, theta_0=90)
     print (Vobs_1, Vobs_2, Vobs_3, Vobs_4)
     print (P_1_1, P_2_0, P_3_1, P_4_0)
     print (Vobs_1*P_1_1, Vobs_2*P_2_0, Vobs_3*P_3_1, Vobs_4*P_4_0)

if __name__ == '__main__' :
  print ('Testing loupiotes v{}, located at {}'.format (loupiotes.__version__, loupiotes.__file__))
  unittest.main(verbosity=2)

