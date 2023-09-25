import numpy as np
import loupiotes.tables
from scipy.interpolate import LinearNDInterpolator
from scipy.integrate import trapezoid
from scipy.special import legendre, gamma, lpmn
import warnings

'''
Compute specific intensities
according to requested tables.
'''

def compute_intensity_non_linear_sing_2010 (mu, coeff) :
  '''
  Eq (3) from Sing 2010.
  '''
  coeff = np.atleast_2d (coeff)
  c1 = - coeff[:,0]*(1-mu**(1/2))
  c2 = - coeff[:,1]*(1-mu)
  c3 = - coeff[:,2]*(1-mu**(3/2))
  c4 = - coeff[:,3]*(1-mu**2)
  return 1 + c1 + c2 + c3 + c4

def restrict_df (df, teff_min=5000, teff_max=7000,
                  logg_min=3.5, logg_max=5,
                  m_h_min=-0.5, m_h_max=0.5) :
  '''
  Restrict data frame to given range of parameters.
  '''
  df = df.loc[(df['Teff']>teff_min)&(df['Teff']<teff_max)]
  df = df.loc[(df['logg']>logg_min)&(df['logg']<logg_max)]
  df = df.loc[(df['M_H']>m_h_min)&(df['M_H']<m_h_max)]
  return df

def compute_grid (mu, teff_min=5000, teff_max=7000,
                  logg_min=2, logg_max=5,
                  m_h_min=-0.5, m_h_max=0.5,
                  name='sing_2010_kepler') :
  '''
  For a given ``mu = cos theta``, with ``theta`` the latitude,. 
  compute grid of intensity which will allow to perform interpolations.
  '''
  df = loupiotes.tables.load_limb_darkening_table (name=name)
  df = restrict_df (df, teff_min=teff_min, teff_max=teff_max,
                   logg_min=logg_min, logg_max=logg_max,
                   m_h_min=m_h_min, m_h_max=m_h_max)
  coord = df[['Teff', 'logg', 'M_H']].to_numpy ()
  if name=='sing_2010_kepler' :
    coeff = df[['a1', 'a2', 'a3', 'a4']].to_numpy ()
    grid = compute_intensity_non_linear_sing_2010 (mu, coeff) 
  return coord, grid

def compute_grid_coeff (teff_min=5000, teff_max=7000,
                        logg_min=2, logg_max=5,
                        m_h_min=-0.5, m_h_max=0.5,
                        name='sing_2010_kepler', law='quadratic') :
  '''
  Compute grid of limb-darkening coefficients which will allow 
  to perform interpolations.
  '''
  df = loupiotes.tables.load_limb_darkening_table (name=name)
  df = restrict_df (df, teff_min=teff_min, teff_max=teff_max,
                   logg_min=logg_min, logg_max=logg_max,
                   m_h_min=m_h_min, m_h_max=m_h_max)
  coord = df[['Teff', 'logg', 'M_H']].to_numpy ()
  if name=='sing_2010_kepler' :
    if law=='linear' :
       coeff = df[['u']].to_numpy ()
    if law=='quadratic' :
       coeff = df[['a', 'b']].to_numpy ()
    if law=='non-linear' :
       coeff = df[['a1', 'a2', 'a3', 'a4']].to_numpy ()
  return coord, coeff

def interpolate_I (coord, grid, teff=5770, logg=4.3, m_h=0) :
  '''
  Interpolate the intensity value on the 3D grid.
  '''
  interp = LinearNDInterpolator(coord, grid)
  I = interp (np.array ([teff, logg, m_h]))[0]
  return I

def get_limb_darkening_coeff (teff=5770, logg=4.3, m_h=0,
                              teff_min=4000, teff_max=7000,
                              logg_min=2, logg_max=5,
                              m_h_min=-1, m_h_max=1,
                              name='sing_2010_kepler', law='quadratic') :
  '''
  Get interpolated limb-darkening coefficients for a given set of parameters.
  '''
  coord, grid = compute_grid_coeff (teff_min=teff_min, teff_max=teff_max,
                                    logg_min=logg_min, logg_max=logg_max,
                                    m_h_min=m_h_min, m_h_max=m_h_max,
                                    name=name, law=law)
  coeffs = interpolate_I (coord, grid, teff=teff, logg=logg, m_h=m_h)
  return coeffs

def get_teff_gradient (coord, grid, teff=5770, logg=4.3, m_h=0) :
  '''
  Compute gradient vector as a function of Teff.
  '''
  a_teff = np.unique (coord[:,0])
  a_logg = np.full (a_teff.size, logg)
  a_m_h = np.full (a_teff.size, m_h)
  interp = LinearNDInterpolator(coord, grid)
  a_I = interp (np.c_[a_teff, a_logg, a_m_h])
  a_dI_dlnTeff = np.gradient (a_I, np.log (a_teff))
  return a_teff, a_I, a_dI_dlnTeff

def interpolate_dI_dlnTeff (coord, grid, teff=5770, logg=4.3, m_h=0) :
  '''
  Interpolate a vector to get the
  intensity variation for a given logg and M_H
  as a function of effective temperature.
  '''
  a_teff, _, a_dI_dlnTeff = get_teff_gradient (coord, grid,
                                       teff=teff, logg=logg, m_h=m_h) 
  dI_dlnTeff = np.interp (teff, a_teff, a_dI_dlnTeff)
  return dI_dlnTeff

def get_logg_gradient (coord, grid, teff=5770, logg=4.3, m_h=0) :
  '''
  Compute gradient vector as a function of logg.
  '''
  a_logg = np.unique (coord[:,1])
  a_teff = np.full (a_logg.size, teff)
  a_m_h = np.full (a_logg.size, m_h)
  interp = LinearNDInterpolator(coord, grid)
  a_I = interp (np.c_[a_teff, a_logg, a_m_h])
  a_dI_dlng = np.gradient (a_I, np.log (10**a_logg))
  return a_logg, a_I, a_dI_dlng

def interpolate_dI_dlng (coord, grid, teff=5770, logg=4.3, m_h=0) :
  '''
  Interpolate a vector to get the
  intensity variation for a given Teff and M_H
  as a function of surface gravity.
  '''
  a_logg, _, a_dI_dlng = get_logg_gradient (coord, grid,
                             teff=teff, logg=logg, m_h=m_h)
  dI_dlng = np.interp (logg, a_logg, a_dI_dlng)

  return dI_dlng

def compute_intensity_component (mu, teff=5770, logg=4.3, m_h=0,
                                 teff_min=5000, teff_max=7000,
                                 logg_min=2, logg_max=5,
                                 m_h_min=-0.5, m_h_max=0.5,
                                 name='sing_2010_kepler',
                                 only_I=False) :
  '''
  Compute the three intensity parameter, I (and dI_dlnTeff and dI_dlng
  if ``only_I`` is ``False``).
  for a given ``teff`` and ``logg``.
  '''
  coord, grid = compute_grid (mu, teff_min=teff_min, teff_max=teff_max,
                              logg_min=logg_min, logg_max=logg_max,
                              m_h_min=m_h_min, m_h_max=m_h_max)
  I = interpolate_I (coord, grid)
  if only_I :
    return I
  else :
    dI_dlnTeff = interpolate_dI_dlnTeff (coord, grid)
    dI_dlng = interpolate_dI_dlng (coord, grid)
    return I, dI_dlnTeff, dI_dlng

def compute_intensity_latitudinal (nbin=100, teff=5770, logg=4.3, m_h=0,
                                   teff_min=5000, teff_max=7000,
                                   logg_min=2, logg_max=5,
                                   m_h_min=-0.5, m_h_max=0.5,
                                   name='sing_2010_kepler',
                                   only_I=False) :
  '''
  Compute intensity vector as a function of the latitude
  parameter ``mu = cos theta``.
  (the size of the vector is provided by ``nbins``).
  '''  
  mu = np.linspace(0, 1, nbin)
  I, dI_dlnTeff, dI_dlng = np.zeros (nbin), np.zeros (nbin), np.zeros (nbin)
  for ii in range (nbin) :
    aux = compute_intensity_component (mu[ii], teff_min=teff_min, teff_max=teff_max,
                                      logg_min=logg_min, logg_max=logg_max,
                                      m_h_min=m_h_min, m_h_max=m_h_max, only_I=only_I)
    if only_I :
      I[ii] = aux
    else :
      I[ii], dI_dlnTeff[ii], dI_dlng[ii] = aux[0], aux[1], aux[2]
  if only_I :
    return mu, I
  else :
    return mu, I, dI_dlnTeff, dI_dlng

def compute_latitudinal_gradient (mu, I) :
  '''
  Compute latitudinal gradient of I (mu)
  function.
  ''' 
  dI_dmu = np.gradient (I, mu)
  return dI_dmu

def compute_b_l_integral (mu, I, l=0) :
  '''
  Compute ``b_l`` integral (see Dziembowski 1977) 
  taking into account Legendre polynomial
  and latitudinal variation of parameter computed with
  ``compute_intensity_latitudinal``.
  '''
  P_l = legendre (l)
  y = mu * I * P_l (mu)
  b_l = trapezoid (y, x=mu) 
  return b_l

def compute_u_l_integral (mu, I, l=0) :
  '''
  Compute ``u_l`` integral (see Dziembowski 1977) 
  taking into account Legendre polynomial
  and latitudinal variation of parameter computed with
  ``compute_intensity_latitudinal``.
  '''
  P_l = legendre (l)
  y = mu**2 * I * P_l (mu)
  u_l = trapezoid (y, x=mu) 
  return u_l

def compute_V_l_ballot_2011 (mu, I, l=0) :
  '''
  Compute Eq. 7 from Ballot et al. 2011.
  '''
  integral = compute_b_l_integral (mu, I, l=l)
  V_l = np.sqrt (np.pi * (2*l+1)) * integral
  return V_l

def reduced_frequency (nu, r=1, mass=1) :
  '''
  Compute reduced frequency.
  '''
  nu = nu*1e-6
  rstar, mstar = r * loupiotes.Rsun, mass*loupiotes.Msun 
  omega = np.sqrt (4*np.pi**2*nu**2*rstar**3 / (loupiotes.Gravity_constant * mstar))
  return omega

def unreduce_frequency (omega, r=1, mass=1) :
  '''
  Compute reduced frequency.
  '''
  rstar, mstar = r * loupiotes.Rsun, mass*loupiotes.Msun 
  nu = np.sqrt (omega**2 * loupiotes.Gravity_constant * mstar / (4*np.pi**2*rstar**3))
  nu = nu*1e6
  return nu

def compute_displacement (nu, velocity=1.5e-1, r=1) :
  '''
  Compute relative displacement deltaR/R.
  '''
  rstar = r * loupiotes.Rsun
  dr_r = velocity / (2*np.pi*nu*1e-6*rstar)
  return dr_r

def compute_vr (nu, dr_r, r=1) :
  '''
  Compute relative displacement deltaR/R.
  '''
  rstar = r * loupiotes.Rsun
  vr = 2*np.pi*nu*1e-6*rstar*dr_r
  return vr

def compute_c_l_integral (mu, I, l=1) :
  '''
  Compute c_l integral defined in Berthomieu & Provost 1990.
  '''
  if l==0 :
    return 0.
  dI_dmu = compute_latitudinal_gradient (mu, I)
  P_l = legendre (l)
  P_l_1 = legendre (l-1)
  y = (I + mu*dI_dmu) * (P_l_1 (mu) - mu*P_l (mu))
  integral = trapezoid (y, x=mu)
  c_l = l * integral

  return c_l 

def compute_v_l_integral (mu, I, l=1) :
  '''
  Compute v_l integral defined in Berthomieu & Provost 1990.
  '''
  if l==0:
    return 0.
  dI_dmu = compute_latitudinal_gradient (mu, I)
  P_l = legendre (l)
  P_l_1 = legendre (l-1)
  y = I * mu * (P_l_1 (mu) - mu*P_l (mu))
  integral = trapezoid (y, x=mu)
  v_l = l * integral

  return v_l 

def compute_normalisation_factor_berthomieu_provost_1990 (l=1, m=0) :
  '''
  Compute normalisation factor included in A_n_l_m term.
  '''
  num = (2*l + 1) * gamma (l - m + 1)
  den = 4 * np.pi * gamma (l + m + 1)
  a_l_m = np.sqrt (num / den)
  return a_l_m

def compute_amplitude_factor_berthomieu_provost_1990 (nu, velocity=1.5e-1, r=1,
                                                      l=1, m=0) :
  '''
  Compute the amplitude factor A_n_l_m following the prescription 
  from Berthomieu & Provost 1990. 
  '''
  dr_R = compute_displacement (nu, velocity=velocity, r=r)
  a_l_m = compute_normalisation_factor_berthomieu_provost_1990 (l=l, m=m)
  A_n_l_m = dr_R * a_l_m 
  return A_n_l_m

def compute_G_xs_ad_function (nu, r=1, mass=1, l=1, nabla_ad=0.4) :
  '''
  Compute G_xs function in its adiabatic formulation.
  We assume here a displacement ``xi_r=1``.
  '''
  omega = reduced_frequency (nu, r=r, mass=mass)
  G_xs = 4 * nabla_ad * (l*(l+1)/omega**2 - 4 - omega**2)

  return G_xs

def compute_variability_factor_berthomieu_provost_1990 (nu, r=1, mass=1, l=1, nabla_ad=0.4, 
                                                        nbin=90, teff=5770, logg=4.43, m_h=0,
                                                        teff_min=5000, teff_max=7000,
                                                        logg_min=2, logg_max=5,
                                                        m_h_min=-0.5, m_h_max=0.5,
                                                        name='sing_2010_kepler') :
  '''
  Compute the variability factor following the prescription of Eq. 19
  from Berthomieu & Provost 1990. 
  This factor should be multiplied by an amplitude factor A_n_l_m
  which is a function of radial displacement, degree and azimutal 
  number.
  Note that and additional renormalisation by ``\int_0^1 I (mu) mu dmu``
  is made here. 
  '''

  mu, I = compute_intensity_latitudinal (nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                    teff_min=teff_min, teff_max=teff_max,
                                    logg_min=logg_min, logg_max=logg_max,
                                    m_h_min=m_h_min, m_h_max=m_h_max,
                                    name=name, only_I=True)
  omega = reduced_frequency (nu, r=r, mass=mass)
  G_xs = 4 * nabla_ad * (l*(l+1)/omega**2 - 4 - omega**2)
  b_l = compute_b_l_integral (mu, I, l=l)
  b_0 = compute_b_l_integral (mu, I, l=0)
  c_l = compute_c_l_integral (mu, I, l=l) 
  variability_factor = G_xs * b_l + 2 * b_l - c_l 
  variability_factor /= b_0

  return variability_factor

def compute_cancellation_frequency (l=1, nabla_ad=0.4, 
                                    nbin=90, teff=5770, logg=4.43, m_h=0,
                                    teff_min=5000, teff_max=7000,
                                    logg_min=2, logg_max=5,
                                    m_h_min=-0.5, m_h_max=0.5,
                                    name='sing_2010_kepler') :
  '''
  Compute the squared cancellation frequencies that arises from Eq. 19
  from Berthomieu & Provost 1990. 
  Note that and additional renormalisation by ``\int_0^1 I (mu) mu dmu``
  is made here. 
  '''

  mu, I = compute_intensity_latitudinal (nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                    teff_min=teff_min, teff_max=teff_max,
                                    logg_min=logg_min, logg_max=logg_max,
                                    m_h_min=m_h_min, m_h_max=m_h_max,
                                    name=name, only_I=True)
  b_l = compute_b_l_integral (mu, I, l=l)
  c_l = compute_c_l_integral (mu, I, l=l) 
 
  B = 4 + (c_l-2*b_l) / (4*nabla_ad*b_l) 
  delta = B**2 + 4*l*(l+1)

  # only this root is real
  omega_c = np.sqrt (0.5 * (-B + np.sqrt (delta)))  

  return omega_c 

def compute_vobs_variability_factor_berthomieu_provost_1990 (nu, r=1, mass=1, l=1, nabla_ad=0.4, 
                                                        nbin=90, teff=5770, logg=4.43, m_h=0,
                                                        teff_min=5000, teff_max=7000,
                                                        logg_min=2, logg_max=5,
                                                        m_h_min=-0.5, m_h_max=0.5,
                                                        name='sing_2010_kepler') :
  '''
  Compute the Vobs variability factor following the prescription of Eq. 21
  from Berthomieu & Provost 1990. 
  This factor should be multiplied by an amplitude factor A_n_l_m
  which is a function of radial displacement, degree and azimutal 
  number.
  Note that and additional renormalisation by ``\int_0^1 I (mu) mu dmu``
  is made here. 
  '''

  mu, I = compute_intensity_latitudinal (nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                    teff_min=teff_min, teff_max=teff_max,
                                    logg_min=logg_min, logg_max=logg_max,
                                    m_h_min=m_h_min, m_h_max=m_h_max,
                                    name=name, only_I=True)
  u_l = compute_u_l_integral (mu, I, l=l)
  v_l = compute_v_l_integral (mu, I, l=l)
  omega = reduced_frequency (nu, r=r, mass=mass)
  variability_factor = omega * (u_l + v_l / omega**2) 

  return variability_factor

def compute_dF_F_berthomieu_provost_1990 (nu, velocity=1.5e-1, r=1, 
                                          mass=1, l=1, m=0, nabla_ad=0.4, 
                                          nbin=90, teff=5770, logg=4.43, m_h=0,
                                          teff_min=5000, teff_max=7000,
                                          logg_min=2, logg_max=5,
                                          m_h_min=-0.5, m_h_max=0.5,
                                          name='sing_2010_kepler') :
   '''
   Compute flux variation amplitude according to Berthomieu & Provost 1990.
   '''

   var = compute_variability_factor_berthomieu_provost_1990 (nu, r=r, mass=mass, l=l, nabla_ad=nabla_ad,
                                                            nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                                            teff_min=teff_min, teff_max=teff_max,
                                                            logg_min=logg_min, logg_max=logg_max,
                                                            m_h_min=m_h_min, m_h_max=m_h_max,
                                                            name=name)
   A_n_l_m = compute_amplitude_factor_berthomieu_provost_1990 (nu, velocity=velocity, r=r,
                                                               l=l, m=m)
   dF_F = A_n_l_m * var
   return dF_F

def compute_Vobs_berthomieu_provost_1990 (nu, velocity=1.5e-1, r=1, 
                                          mass=1, l=1, m=0, nabla_ad=0.4, 
                                          nbin=90, teff=5770, logg=4.43, m_h=0,
                                          teff_min=5000, teff_max=7000,
                                          logg_min=2, logg_max=5,
                                          m_h_min=-0.5, m_h_max=0.5,
                                          name='sing_2010_kepler') :
   '''
   Compute ``Vobs`` amplitude according to Berthomieu & Provost 1990.
   Note that, on the contrary of the Berthomieu & Provost formalism,
   ``Vobs`` is dimensioned.
   '''

   warnings.warn ('The Vobs result should be used with caution, I am not sure of the used renormalisation.')

   var = compute_vobs_variability_factor_berthomieu_provost_1990 (nu, r=r, mass=mass, l=l, nabla_ad=nabla_ad,
                                                            nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                                            teff_min=teff_min, teff_max=teff_max,
                                                            logg_min=logg_min, logg_max=logg_max,
                                                            m_h_min=m_h_min, m_h_max=m_h_max,
                                                            name=name)
   A_n_l_m = compute_amplitude_factor_berthomieu_provost_1990 (nu, velocity=velocity, r=r,
                                                               l=l, m=m)
   Vobs = A_n_l_m * var
   # Compute dimensioning factor 
   Omega_g = (loupiotes.Gravity_constant * mass * loupiotes.Msun / (loupiotes.Rsun*r)**3)**(1/2)
   rstar = r * loupiotes.Rsun
   Vobs = Vobs * rstar * Omega_g 
   return Vobs

def compute_dr_R_berthomieu_provost_1990 (nu, dF_F=1e-6, r=1, 
                                          mass=1, l=1, m=0, nabla_ad=0.4, 
                                          nbin=90, teff=5770, logg=4.43, m_h=0,
                                          teff_min=5000, teff_max=7000,
                                          logg_min=2, logg_max=5,
                                          m_h_min=-0.5, m_h_max=0.5,
                                          name='sing_2010_kepler') :
   '''
   Compute radial displacement amplitude according to Berthomieu & Provost 1990.
   '''

   var = compute_variability_factor_berthomieu_provost_1990 (nu, r=r, mass=mass, l=l, nabla_ad=nabla_ad,
                                                            nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                                            teff_min=teff_min, teff_max=teff_max,
                                                            logg_min=logg_min, logg_max=logg_max,
                                                            m_h_min=m_h_min, m_h_max=m_h_max,
                                                            name=name)

   a_l_m = compute_normalisation_factor_berthomieu_provost_1990 (l=l, m=m)
   dr_R = dF_F / (a_l_m * var)

   return dr_R 


def compute_variability_factor_townsend_2003 (nu, r=1, mass=1, l=1, nabla_ad=0.4, 
                                              nbin=90, teff=5770, logg=4.43, m_h=0,
                                              teff_min=5000, teff_max=7000,
                                              logg_min=2, logg_max=5,
                                              m_h_min=-0.5, m_h_max=0.5,
                                              name='sing_2010_kepler') :
   '''
   Compute the variability factor that 
   should be multiplied by the relatived
   displacement deltaR/R to get the flux
   variation.

   Parameters
   ----------
   nu : float
     frequency in muHz.
   '''

   omega = reduced_frequency (nu, r=r, mass=mass)
   mu, I, dI_dlnTeff, dI_dlng = compute_intensity_latitudinal (nbin=nbin, teff=teff, logg=logg, m_h=m_h,
                                                                  teff_min=teff_min, teff_max=teff_max,
                                                                  logg_min=logg_min, logg_max=logg_max,
                                                                  m_h_min=m_h_min, m_h_max=m_h_max,
                                                                  name=name)
   I_0 = compute_b_l_integral (mu, I, l=0)
   I_l = compute_b_l_integral (mu, I, l=l)
   dI_l_dlnTeff = compute_b_l_integral (mu, dI_dlnTeff, l=l)
   dI_l_dlng = compute_b_l_integral (mu, dI_dlng, l=l)
   A1 = (2+l)*(l-1) * I_l 
   A2 = nabla_ad * (l*(l+1)/omega**2 - 4 - omega**2) * dI_l_dlnTeff 
   A3 = - (2 + omega**2) * dI_l_dlng
   factor = (A1 + A2 + A3) / I_0
   return factor

def observer_factor (l=0, m=0, theta_0=90) :
  '''
  Compute the P_l^m (cos theta_0) factor related to the observer 
  inclination angle.
  '''
  mu = np.cos (np.pi*theta_0/180)
  plm_theta_0 = lpmn (m, l, mu)[0][m,l]
  return plm_theta_0
  
