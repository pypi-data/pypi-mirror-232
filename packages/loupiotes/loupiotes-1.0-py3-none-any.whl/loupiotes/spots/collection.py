import numpy as np
import warnings
try :
  import arviz as az
except ImportError :
  pass
import cartopy
import matplotlib as mpl
import matplotlib.pyplot as plt
import cloudpickle
from scipy import signal
import loupiotes
from astropy.time import Time
import astropy.units as u
from tqdm import tqdm
from pathos.pools import ProcessPool
from scipy.integrate import trapz

'''
Define the ``SpotCollection`` class, which
allows to analyse together the results from 
an ensemble of SpotModel obtained from the 
same star.
'''

class SpotCollection :
  '''
  ``SpotCollection`` object. 
  '''

  def __init__ (self, spotmodels=None, target_name=None) :
    '''
    ``SpotCollection`` is initiated from a list of ``SpotModel`` provided
    by the user. Each observation in each spot model should have a unique
    timestamp.

    Parameters
    ----------
    
    spotmodels : list
      list of spotmodels used to build the collection.
      Optional, default ``None``. If timestamps is provided for 
      each spot model, the list is reordered
      according to the start times of their light curves.

    target_name : str
      Name of the considered target. Optional, default ``None``.

    '''

    self.spotmodels = spotmodels 
    self.n_models = len (spotmodels)
    self.target_name = target_name

    self.timestamps = None
    self.lc = None

    self.LongitudinalDistribution = None
    self.LatitudinalDistribution = None

    self.dynamic_longitudes = None
    self.DynamicDistribution = None

    self.large_dim = spotmodels[0].large_dim 
    for model in spotmodels :
      if np.any (model.large_dim != self.large_dim) :
        warnings.warn ("Some models have different dimensions !") 
    self.longitudes = spotmodels[0].longitudes
    self.colatitudes = spotmodels[0].colatitudes

    self.hasTimestamps = True
    self.start_time = np.zeros (self.n_models)
    for ii in range (self.n_models) :
      if spotmodels[ii].timestamps is not None :
        self.start_time[ii] = spotmodels[ii].timestamps[0]
      else :
        self.hasTimestamps = False    
      
    if self.hasTimestamps :
      indices = np.argsort (self.start_time)
      spotmodels[:] = [spotmodels[ii] for ii in indices]
      self.start_time = self.start_time[indices]

    self.LongitudinalDistribution = None
    self.LatitudinalDistribution = None
    self.LongitudinalCorrelation = None

  def extractSubCollection (self, index_start, index_end) :
    '''
    Return a ``Collection`` including only ``index_start``th
    to ``index_end-1``th spot models.
    Note that no copy of the spotmodels will be performed
    so any memory manipulation of them will also affect
    the original ``Collection``.

    Returns
    -------
    Collection
      The extracted sub collection.
    '''
    collection = SpotCollection (spotmodels=self.spotmodels[index_start:index_end],
                                 target_name=self.target_name)
    return collection

  def hasDivergence (self) :
    '''
    Check if spot models of the collection have 
    divergence and return the indices list corresponding
    to the ``collection.spotmodels`` elements that exhibit
    divergence. Therefore, if the function returns an empty 
    list, this means that no model from the ``Collection`` 
    has divergences.

    Returns
    -------
    List
      List of index of ``SpotModels`` with HMC divergences.
    ''' 
    divergent = []
    for ii, model in enumerate (self.spotmodels) :
      if model.hasDivergence () :
        divergent.append (ii)
    return divergent
  
  def computeLightCurve (self, step=1, shift_max=False,
                         offset=0) :
    '''
    Compute light curve from the ones provided by each 
    spot model.

    Returns
    -------
    tuple of arrays
      Tuple of arrays with the timestamps, the spot-model
      light curve, the observed light curve and corresponding
      uncertainties.
    ''' 
    list_stamps, list_lc, list_obs, list_err = [], [], [], []
    for ii in range (0, self.n_models, step) :
      model = self.spotmodels[ii]
      # Checking that the model has an observed light curve set
      if model.lc_obs is not None :
        list_stamps.append (model.timestamps)
        if shift_max :
          shift = 1 - np.amax (model.lc_obs)
          list_lc.append (model.lc - shift) 
          list_obs.append (model.lc_obs - shift) 
        else :
          list_lc.append (model.lc) 
          list_obs.append (model.lc_obs) 
        if type (model.err_obs) in [np.float_, float, np.int_, int] :
          err_obs = np.full (model.lc_obs.size, model.err_obs)
        else :
          err_obs = model.err_obs
        list_err.append (err_obs) 
    # Concatenating the lists
    self.timestamps = np.concatenate (list_stamps)
    self.lc = np.concatenate (list_lc)
    self.lc_obs = np.concatenate (list_obs)
    self.err_obs = np.concatenate (list_err)
    indices = np.argsort (self.timestamps)
    self.timestamps, self.lc = self.timestamps[indices], self.lc[indices]
    self.lc_obs, self.err_obs = self.lc_obs[indices], self.err_obs[indices]
    # Adding the offset
    self.lc_obs += offset
    self.lc += offset
    return self.timestamps, self.lc, self.lc_obs, self.err_obs

  def plotLightCurve (self, plot_obs=True, ppm=False,
                      xlabel=None, ylabel=None, 
                      figsize=(8,4), marker='none', lw=2,
                      show_errorbars=True, markersize=3, 
                      shift_max=False, step=1, offset=0, 
                      zero_time_origin=True, date_origin=None, 
                      **kwargs) :
    """
    Plot the ``Collection`` light curve.

    Parameters
    ----------
    plot_obs : bool
        Plot observed light curve together with spot-model light
        curve.
    ppm : bool
        If set to ``True``, choose a scale in part-per-million.
    xlabel : str
        Label of the x-axis.
    ylabel : str
        Label of the y-axis.
    figsize : tuple
        Figure size.
    marker : str
        Marker to use for the observed light curve.
    lw : float
        Linewidth of the spot model light curve.
    show_errorbars : bool
        Whether to show (or not) observation error bar.
    markersize : float
        Marker size.
    kwargs : dict
        Keyword arguments of ``matplotlib.pyplot.subplots``.

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    """
    if self.lc is None :
      self.computeLightCurve (step=step, shift_max=shift_max,
                              offset=offset)
    if ppm :
      factor = 1e6
    else :
      factor = 1
    if ylabel is None :
      if ppm :
        ylabel='Flux (ppm)'
      else :
        ylabel='Flux (normalised)'
    fig, ax = plt.subplots (1, 1, figsize=figsize, **kwargs)
    t = self.timestamps/86400
    if zero_time_origin :
      t -= t[0]
    if date_origin is not None :
      stamps = Time (date_origin) + (t-t[0]) * u.day
      t = stamps.jyear
      xlabel = "Date (year)"
    else :
      xlabel = "Time (day)"

    ax.plot (t, self.lc*factor, color='darkorange', marker=marker, lw=lw)
    if plot_obs :
      if show_errorbars :
        yerr = self.err_obs*factor
      else :
        yerr = None
      ax.errorbar (t, self.lc_obs*factor, yerr=yerr,
                   marker='.', color='black', markerfacecolor='black',
                   capsize=4, zorder=-1, linestyle='none', 
                   markersize=markersize)
    ax.set_xlabel (xlabel)
    ax.set_ylabel (ylabel)
    fig.tight_layout ()
    return fig

  def computeLongitudinalDistribution (self, min_theta=0, max_theta=180,
                                       correct_visibility=True, rolling=False,
                                       win_size_time=3, win_size_lon=21,
                                       win_type_time='triang', win_type_lon='triang',
                                       correction_factor=1, progress=False,
                                       parallelise=False, nodes=8) :
    """
    Compute temporal grid for longitudinally projected distribution.

    Parameters
    ----------
    min_theta : float
        Minimum co-latitude to consider for the projected 
        distribution.
    max_theta : float
        Maximum co-latitude to consider for the projected 
        distribution.
    correct_visibility : bool
        Whether to correct or not visibility, following Lanza
        et al. 2007.
    rolling : bool
        Whether to apply or not a rolling window on the 
        projected distribution.
    win_size_time : int
        Number of time elements to consider in the time direction
        of the rolling window.
    win_size_lon : int
        Number of longitude elements to consider in the longitude direction
        of the rolling window.
    win_type_time : str
        Rolling window type in the time direction.
    win_type_lon : str
        Rolling window type in the longitude direction.
    correction_factor : float
      Correction factor to apply on the distribution. Might be useful 
      to renormalise filling factor distribution when
      analysing pure spots model (Q=0) with arbitrary contrast factors. 

    Returns
    -------
    ndarray
      The computed longitudinal distribution.
    """
    # resetting the correlation index
    self.LongitudinalCorrelation = None
    self.LongitudinalDistribution = np.zeros ((self.n_models, self.large_dim[1])) 
    if parallelise :
      with ProcessPool (nodes=nodes) as p :
        p.restart ()
        chunksize = self.n_models // nodes
        results = list(tqdm (p.imap (_wrapper_parallel_longitudinal, 
                              self.spotmodels, 
                              [min_theta]*self.n_models, 
                              [max_theta]*self.n_models,
                              [correct_visibility]*self.n_models, 
                              [correction_factor]*self.n_models,
                              chunksize=chunksize), 
                              total=self.n_models))
        for ii, (model, distribution) in enumerate (results) :
          self.spotmodels[ii] = model
          self.LongitudinalDistribution[ii,:] = distribution
        p.close ()
    else :
      for ii, model in tqdm (enumerate (self.spotmodels), 
                             disable=not progress, total=self.n_models) :
        self.LongitudinalDistribution[ii,:] = model.computeLongitudinalDistribution (min_theta=min_theta, 
                                                                                     max_theta=max_theta,
                                                                    correct_visibility=correct_visibility,
                                                                    correction_factor=correction_factor)
    if rolling :
      # Convolution along longitudes
      self.LongitudinalDistribution = rolling_mean_2d (self.LongitudinalDistribution, 
                                                    win_size=win_size_lon, win_type=win_type_lon, 
                                                    axis=1, periodic=True)  
      # Convolution along time
      self.LongitudinalDistribution = rolling_mean_2d (self.LongitudinalDistribution, 
                                                    win_size=win_size_time, win_type=win_type_time, 
                                                    axis=0)  
    return self.LongitudinalDistribution


  def computeLatitudinalDistribution (self) :
    '''
    Compute temporal grid for latitudinally projected distribution.

    Returns
    -------
    ndarray
      The 2D-grid with latitudinally projected distribution of 
      filling factors.
    '''
    self.LatitudinalDistribution = np.zeros ((self.n_models, self.large_dim[0])) 
    for ii, model in enumerate (self.spotmodels) :
      self.LatitudinalDistribution[ii,:] = model.computeLatitudinalDistribution ()
    return self.LatitudinalDistribution

  def plotLongitudinalDistribution (self, figsize=(6,6), cmap='Greys', shading='nearest',
                                    vmin=None, vmax=None, time_xaxis=True, colorbar=True,
                                    contourf_plot=False, show_contour=False, extend=True,
                                    limit_extent=60, brightness_map=False, normalise=False,
                                    levels=None, cbar_scinotation=False, percentage=False, 
                                    shift_longitude=None, date_origin=None, 
                                    time_ticks=None, lon_label=None, dynamic=False,
                                    **kwargs) :
    """
    Plot longitudinal distribution of the model collection.

    Parameters
    ----------
    figsize : tuple
        figsize
    cmap : string or colormap instance
        cmap
    shading : str
        shading to use for the figure
    vmin : float
        Minimal value for the colormap. 
    vmax :
        Maximal value for the colormap.
    time_xaxis : bool
        If set to ``True``, the time axis will be the x-axis,
        otherwise the y-axis.
    colorbar : bool
        Set to ``True`` to show the colorbar.
    contourf_plot : bool
        If set to ``True``, will create a contour-filled plot.
    show_contour : bool
        Show correlation contour computed with ``matplotlib.pyplot.contour``.
    shift_longitude : float
        Shift longitude of the plotted map of the given quantity, with
        respect to the reference value of the ``Collection``.
    kwargs : dict
        Keyword arguments to be passed to ``matplotlib.pyplot.contour``
    date_origin : str
        Time stamp of the first plotted element, under the format 
        ``YYYY-MM-DD``. If this option is chosen, the time axis units
        will be years.

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    """
    # computing the little offset necessary to put the plot 
    # exactly on a 0,360 extent
    dphi = (self.longitudes[0,1]-self.longitudes[0,0])*180/np.pi

    longitudes = self.longitudes[0,:]
    if dynamic :
      if self.DynamicDistribution is None :
        raise Exception ("You must compute dynamic distribution first !")
      LongitudinalDistribution = self.DynamicDistribution
    else :
      if self.LongitudinalDistribution is None :
        raise Exception ("You must compute longitudinal distribution first !")
      LongitudinalDistribution = self.LongitudinalDistribution
    if shift_longitude is not None :
      shift_index = int (shift_longitude / dphi)
      LongitudinalDistribution = np.roll (LongitudinalDistribution, 
                                          shift_index, axis=1)

    # Implementing extension option to better visualise
    # the periodic shape of the map
    if extend :
      limit_1, limit_2 = 2*np.pi - (limit_extent/180*np.pi), limit_extent/180*np.pi
      LongitudinalDistribution = np.concatenate ((LongitudinalDistribution[:,self.longitudes[0,:]>=limit_1], 
                                                  LongitudinalDistribution, 
                                                  LongitudinalDistribution[:,self.longitudes[0,:]<=limit_2]),
                                                  axis=1)
      longitudes = np.linspace (-limit_2, 2*np.pi+limit_2, LongitudinalDistribution.shape[1], endpoint=False)

    fig, ax = plt.subplots (1, 1, figsize=figsize)
    # Setting time vector 
    t = (self.start_time-self.start_time[0])/86400
    if date_origin is not None :
      stamps = Time (date_origin) + t * u.day
      t = stamps.jyear
      time_label = "Date (year)"
    else :
      time_label = "Time (day)"

    if lon_label is None :
      lon_label = r'$\phi$ ($^o$)'

    if time_xaxis :
      X, Y = t, longitudes*180/np.pi + dphi/2
      C = LongitudinalDistribution.T
      ax.set_xlabel (time_label)
      ax.set_ylabel (lon_label)
      if brightness_map :
        # Normalise each stamp by its max
        for ii in range (C.shape[1]) :
          max_value = np.amax (C[:,ii])
          if max_value != 0 :
            C[:,ii] /= max_value
      if normalise :
        # Normalise each stamp by 
        # total covered area
        for ii in range (C.shape[1]) :
          norm = np.sum (C[:,ii])
          if norm != 0 :
            C[:,ii] /= norm
    else : 
      X, Y = longitudes*180/np.pi + dphi/2, t
      C = LongitudinalDistribution
      ax.set_ylabel (time_label)
      ax.set_xlabel (lon_label)
      if brightness_map :
        # Normalise each stamp by its max
        for ii in range (C.shape[0]) :
          max_value = np.amax (C[ii,:])
          if max_value != 0 :
            C[ii,:] = C[ii,:] / max_value
      if normalise :
        # Normalise each stamp by its 
        # total covered area
        for ii in range (C.shape[0]) :
          norm = np.sum (C[ii,:])
          if norm != 0 :
            C[ii,:] = C[ii,:] / norm

    if brightness_map :
      if levels is None :
        levels = [0.1*ii for ii in range (11)]
    elif percentage :
      C *= 100

    if contourf_plot :
      im = ax.contourf (X, Y, C,
                       cmap=cmap, levels=levels,
                       extend="both")
    else :
      im = ax.pcolormesh (X, Y, C,
                          shading=shading, cmap=cmap,
                          vmin=vmin, vmax=vmax)
    if show_contour :
      ax.contour (X, Y, C, levels=levels, **kwargs)
    if colorbar :
      if cbar_scinotation :
        formatter = mpl.ticker.LogFormatterSciNotation ()
      else :
        formatter = None
      cbar = plt.colorbar (im, format=formatter)
      if not brightness_map :
        if percentage :
          cbar.set_label (r'$f_s$ (%)')
        else :
          cbar.set_label (r'$f_s$')
    if time_xaxis :
      ax.set_yticks ([0, 90, 180, 270, 360])
      if time_ticks is not None :
        ax.set_xticks (time_ticks)
      if extend :
        ax.hlines ((0, 360), X[0], X[-1], ls='-.', lw=1, color='black')
    else :
      ax.set_xticks ([0, 90, 180, 270, 360])
      if time_ticks is not None :
        ax.set_yticks (time_ticks)
      if extend :
        ax.vlines ((0, 360), Y[0], Y[-1], ls='-.', lw=1, color='black')
    return fig

  def plotLatitudinalDistribution (self, figsize=(6,6), cmap='Greys',
                                   vmin=None, vmax=None, shading='nearest') :
    '''
    Plot latitudinal distribution of the model collection.

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    '''
    if self.LatitudinalDistribution is None :
      self.computeLatitudinalDistribution () 
    fig, ax = plt.subplots (1, 1, figsize=figsize)
    im = ax.pcolormesh ((self.start_time-self.start_time[0])/86400,
                         self.colatitudes[:,0]*180/np.pi,
                         self.LatitudinalDistribution.T,
                         shading=shading, cmap=cmap,
                         vmin=vmin, vmax=vmax)
    cbar = plt.colorbar (im)
    cbar.set_label (r'$f_s$')
    ax.set_yticks ([0, 30, 60, 90, 120, 150, 180])
    ax.set_ylim (180, 0)
    ax.set_xlabel ('Time (day)')
    ax.set_ylabel (r'$\theta$ ($^o$)')
    return fig

  def plotMeanLongitudinalDistribution (self, figsize=(6,6), 
                                        lw=2, color='darkorange',
                                        percentage=True, ylim=None,
                                        xlabel=None, shift_longitude=None,
                                        dynamic=False, threshold=None,
                                        metric="mean", use_norm_for_threshold=False) :
    '''
    Plot mean longitudinal distribution of the model collection.

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    '''
    if dynamic :
      if self.DynamicDistribution is None :
        raise Exception ("You must compute dynamic distribution first !")
      LongitudinalDistribution = np.copy (self.DynamicDistribution)
    else :
      if self.LongitudinalDistribution is None :
        raise Exception ("You must compute longitudinal distribution first !")
      LongitudinalDistribution = np.copy (self.LongitudinalDistribution)
    if percentage :
      factor = 100
      ylabel = r'$f_s$ (%)'
    else :
      factor = 1
      ylabel = r'$f_s$'
    if threshold is not None :
      if use_norm_for_threshold :
        for ii in range (LongitudinalDistribution.shape[0]) :
          normalising_term = np.sum (LongitudinalDistribution[ii,:])
          if normalising_term!= 0 :
            cond = LongitudinalDistribution[ii,:] / normalising_term > threshold
            LongitudinalDistribution[ii,~cond] = 0
      else :
        LongitudinalDistribution[LongitudinalDistribution<threshold] = 0

    X = 180/np.pi*self.spotmodels[0].longitudes[0,:]
    if metric=="mean" :
      Y = np.mean (LongitudinalDistribution*factor, axis=0)
    elif metric=="sum" :
      Y = np.sum (LongitudinalDistribution*factor, axis=0)
    if shift_longitude is not None :
      X = (X + shift_longitude) % 360
      indices = np.argsort (X)
      X, Y = X[indices], Y[indices]

    fig, ax = plt.subplots (1, 1, figsize=figsize)
    ax.plot (X, Y,  
             color=color, lw=lw)
    ax.set_xticks ([0, 90, 180, 270, 360])
    if xlabel is None :
      xlabel = r'$\phi$ ($^o$)'
    ax.set_xlabel (xlabel)
    ax.set_ylabel (ylabel)
    ax.set_xlim (0, 360)
    if ylim is not None :
      ax.set_ylim (ylim)
    return fig
  
  def plotMeanLatitudinalDistribution (self, figsize=(6,6), 
                                       lw=2, color='darkorange',
                                       percentage=True, ylim=None) :
    '''
    Plot mean latitudinal distribution of the model collection.

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    '''
    if self.LatitudinalDistribution is None :
      self.computeLatitudinalDistribution () 
    if percentage :
      factor = 100
      ylabel = r'$f_s$ (%)'
    else :
      factor = 1
      ylabel = r'$f_s$'
    ax.plot (180/np.pi*self.spotmodels[0].latitudes[:,0], 
             np.mean (self.LatitudinalDistribution, axis=0)*factor,
             color=color, lw=lw)
    ax.set_xticks ([0, 30, 60, 90, 120, 150, 180])
    ax.set_xlabel (r'$\theta$ ($^o$)')
    ax.set_ylabel (ylabel)
    ax.set_xlim (0, 180)
    if ylim is not None :
      ax.set_ylim (ylim)
    return fig

  def computeLongitudinalCorrelation (self, mode='same',
                                      step=1, set_threshold=False,
                                      std=1, normalise_max=False, 
                                      normalise_std=True, rolling=False,
                                      win_size_time=3, win_size_lon=21,
                                      win_type_time='triang', win_type_lon='triang') :
    """
    Compute correlation of longitudinal distribution.

    Parameters
    ----------
    mode : str
      mode to use to compute the correlation (see ``scipy.signal.correlate2d`` 
      documentation), must be ``same`` or ``full. Optional, default ``same``.
    step : int
        Slicing interval on which correlations will be computed.
    set_threshold :
        set_threshold
    std :
        std
    normalise_max : bool
        If set to ``True``, each correlation row will be normalised
        by its maximal value.
    normalise_std : bool
        If set to ``True``, each correlation row will be normalised
        by the standard deviation product of the distributions that
        were used to compute it. If this set to ``True``, the function
        will automatically set ``normalise_max`` to ``False``.
    rolling :
        rolling
    win_size_time :
        win_size_time
    win_size_lon :
        win_size_lon
    win_type_time :
        win_type_time
    win_type_lon :
        win_type_lon

    Returns
    -------
    tuple of arrays
      Tuple of arrays with, in the following order, correlation time reference
      vector (in days), longitudinal coordinates for correlation (in degrees), 2D
      (time, longitude) correlation map, longitude of max correlation at each time
      reference (in degrees), corresponding max correlation and migration rate
      computed from longitude of max correlation (see Lanza et al. 2019), in
      degree/day.
    """
    if self.LongitudinalDistribution is None :
      raise Exception ("You must first compute the longitudinal distribution of the collection !")
    self.LongitudinalCorrelation = []
    for ii in range (1, self.LongitudinalDistribution.shape[0], step) :
      cc = cross_correlation_periodic (self.LongitudinalDistribution[ii-1,:],
                                       self.LongitudinalDistribution[ii,:],
                                       mode=mode, set_threshold=set_threshold,
                                       std=std, normalise_max=normalise_max,
                                       normalise_std=normalise_std) 
      self.LongitudinalCorrelation.append (cc)
    self.LongitudinalCorrelation = np.array (self.LongitudinalCorrelation)
    if rolling :
      # Convolution along longitudes
      self.LongitudinalCorrelation = rolling_mean_2d (self.LongitudinalCorrelation, 
                                                    win_size=win_size_lon, win_type=win_type_lon, 
                                                    axis=1, periodic=True)  
      # Convolution along time
      self.LongitudinalCorrelation = rolling_mean_2d (self.LongitudinalCorrelation, 
                                                    win_size=win_size_time, win_type=win_type_time, 
                                                    axis=0)  
    dphi = (self.longitudes[0,1]-self.longitudes[0,0])*180/np.pi
    if mode=='full' :
      self.LongitudinalCorrelationCoords = np.linspace (-360+dphi, 360-dphi, 
                                           self.LongitudinalCorrelation.shape[1])
    elif mode=='same' :
      self.LongitudinalCorrelationCoords = np.linspace (-180+dphi, 180, 
                                           self.LongitudinalCorrelation.shape[1])
    self.LongitudinalCorrelationTime = self.start_time[1::step]/86400 

    # Computing longitude of max correlation
    self.MaxCorrelation = np.amax (self.LongitudinalCorrelation, axis=1)
    indices = np.argmax (self.LongitudinalCorrelation, axis=1)
    self.LongitudeMaxCorrelation = np.array (
         [self.LongitudinalCorrelationCoords[ii] for ii in indices]
         ) 
    self.Migration = np.gradient (self.LongitudeMaxCorrelation,
                                  self.LongitudinalCorrelationTime) 
    
    return (self.LongitudinalCorrelationTime, 
            self.LongitudinalCorrelationCoords, 
            self.LongitudinalCorrelation,
            self.LongitudeMaxCorrelation,
            self.MaxCorrelation,
            self.Migration)

  def plotLongitudinalCorrelation (self, figsize=(6,6), cmap='plasma', shading='nearest',
                                   vmin=None, vmax=None, time_xaxis=True, colorbar=True,
                                   contourf_plot=False, show_contour=False,
                                   normalise_max=False, normalise_std=False, 
                                   levels=None, cmap_contour='cividis_r', 
                                   zeroline=True, **kwargs) :
    """
    Plot longitudinal correlation of the model collection.

    Parameters
    ----------
    figsize : tuple
        figsize
    cmap : string or colormap instance
        cmap
    shading : str
        shading to use for the figure
    vmin : float
        Minimal value for the colormap. 
    vmax :
        Maximal value for the colormap.
    time_xaxis : bool
        If set to ``True``, the time axis will be the x-axis,
        otherwise the y-axis.
    colorbar : bool
        Set to ``True`` to show the colorbar.
    contourf_plot : bool
        If set to ``True``, will create a contour-filled plot.
    show_contour : bool
        Show correlation contour computed with ``matplotlib.pyplot.contour``.
    normalise_max : bool
        If set to ``True``, each correlation row will be normalised
        by its maximal value.
    levels : array-like
        Levels to use for the contour-filled and contour drawings.
    cmap_contour : str or colormap instance
        Color map to use for the contours.
    kwargs : dict
        Keyword arguments to be passed to ``matplotlib.pyplot.contour``

    Returns
    -------
    matplotlib.pyplot.figure
      The plotted figure.
    """
    if self.LongitudinalCorrelation is None :
      raise Exception ("You must compute longitudinal correlation first !")
    fig, ax = plt.subplots (1, 1, figsize=figsize)
    # computing the little offset necessary to put the plot 
    # exactly on a 0,360 extent
    dphi = (self.longitudes[0,1]-self.longitudes[0,0])*180/np.pi
    if normalise_max :
      norm = self.MaxCorrelation.reshape (-1, 1)
    else :
      norm = 1
    origin = self.LongitudinalCorrelationTime[0]
    if time_xaxis :
      X, Y = (self.LongitudinalCorrelationTime - origin,
              self.LongitudinalCorrelationCoords + dphi/2)
      C = self.LongitudinalCorrelation.T / norm.T
      ax.set_xlabel ('Time (day)')
      ax.set_ylabel (r'$\phi$ ($^o$)')
    else : 
      X, Y = (self.LongitudinalCorrelationCoords + dphi/2,
             self.LongitudinalCorrelationTime - origin)
      C = self.LongitudinalCorrelation / norm
      ax.set_ylabel ('Time (day)')
      ax.set_xlabel (r'$\phi$ ($^o$)')
    if contourf_plot :
      if normalise_max and levels is None :
        levels = [0., 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 1]
      im = ax.contourf (X, Y, C, levels=levels,
                       cmap=cmap, extend="both")
    else :
      im = ax.pcolormesh (X, Y, C,
                          shading=shading, cmap=cmap,
                          vmin=vmin, vmax=vmax)
    if show_contour :
      ax.contour (X, Y, C, levels=levels,
                  cmap=cmap_contour, **kwargs)
    if colorbar :
      cbar = plt.colorbar (im)
      if normalise_max :
        cbar.set_label (r'Cross correlation (normalised)')
      else :
        cbar.set_label (r'Cross correlation')
    # fastly checking if we have a ``full`` or ``same``
    # cross correlation mode
    if np.amin (self.LongitudinalCorrelationCoords<0) :
      ticks = [-270, -180, -90, 0, 90, 180, 270]
    else :
      ticks = [-120, -60, 0, 60, 120]
    if time_xaxis :
      ax.set_yticks (ticks)
    else :
      ax.set_xticks (ticks)
    if zeroline :
      ax.axvline (0, color='grey', 
                  lw=2, ls=(0, (1, 1, 1, 1, 1, 7, 5, 7)))
    return fig

  def plotMaxCorrelation (self, figsize=(6,4), 
                         color='darkorange', mec='black',
                         marker='o', refsize=300, ms=5,
                         **kwargs) :
    '''
    Plot max correlation value as a function of time.
    '''
    if self.LongitudinalCorrelation is None :
      raise Exception ("You must compute longitudinal correlation first !")
    fig, ax = plt.subplots (1, 1, figsize=figsize)
    ax.plot (self.LongitudinalCorrelationTime - self.LongitudinalCorrelationTime[0], 
             self.MaxCorrelation, 
             color=color, marker=marker, ms=ms, 
             mec=mec, **kwargs)
    ax.set_xlabel ("Time (day)") 
    ax.set_ylabel ("Max correlation")
    return fig
    
  def plotMigrationRate (self, figsize=(6,6), 
                         color='darkorange', edgecolor='black',
                         marker='o', refsize=300) :
    '''
    Plot spots migration rate as the lag derivative,
    as derived by Lanza et al. 2019.
    '''
    if self.LongitudinalCorrelation is None :
      raise Exception ("You must compute longitudinal correlation first !")
    fig, ax = plt.subplots (1, 1, figsize=figsize)
    ax.scatter (self.LongitudinalCorrelationTime - self.LongitudinalCorrelationTime[0], 
                self.Migration,
                color=color, marker=marker, 
                s=refsize**(self.MaxCorrelation/np.amax (self.MaxCorrelation)), 
                edgecolor=edgecolor)
    ax.set_xlabel ("Time (day)") 
    ax.set_ylabel ("Lag derivative ($^o$/day)")
    return fig

  def computeLongitudinalShift (self, mean_latitude, 
                                omega_eq=None, omega_diff=None,
                                omega_ref=None) :
    """
    Compute longitudinal shift assuming mean latitude spot clustering
    and a simple differential rotation profile 
    ``omega_eq + omega_diff*sin (mean_latitude)**2``. Note that rotation
    frequencies must be provided in rad/s. If not provided, ``omega_eq``,
    ``omega_diff`` and ``omega_ref`` are set to solar values. 
    """
    if omega_eq is None :
      omega_eq = 2*np.pi / (24.47 * 86400) 
    if omega_ref is None :
      omega_ref = 2*np.pi / (25.38 * 86400)
    if omega_diff is None :
      omega_diff = - np.pi * 3.40 / (180*86400) 
    to_integrate = omega_eq + omega_diff*np.sin (mean_latitude*np.pi/180)**2 - omega_ref
    longitude_shift = np.zeros (self.start_time.size)
    for ii in range (self.start_time.size) :
        longitude_shift[ii] = trapz (to_integrate[:ii+1], self.start_time[:ii+1])
    return longitude_shift

  def computeDynamicLongitudes (self, longitude_shift) :
    """
    Compute dynamic longitude with respect to an input longitude
    shift.

    Parameters
    ----------
    longitude_shift : ndarray
      Must have length ``self.start_time.shape[0]``
    """
    longitudes_ref = np.tile (self.longitudes[0,:], (self.start_time.size, 1))
    self.dynamic_longitudes = longitudes_ref + longitude_shift.reshape (-1, 1)
    self.dynamic_longitudes = self.dynamic_longitudes % (2*np.pi)
    return self.dynamic_longitudes

  def computeDynamicDistribution (self, longitude_shift, rolling=False,
                                  win_size_time=3, win_size_lon=21,
                                  win_type_time='triang', win_type_lon='triang',) :
    """
    Compute new longitudinal distribution according to dynamic correction
    for longitudes.
    """
    if self.LongitudinalDistribution is None :
      raise Exception ("You must first compute the longitudinal distribution of the collection !")
    self.computeDynamicLongitudes (longitude_shift)
    self.DynamicDistribution = np.zeros (self.LongitudinalDistribution.shape)
    for ii, distribution in enumerate (self.LongitudinalDistribution) : 
      new_dist, _ = np.histogram (self.dynamic_longitudes[ii,:],
                                  range=(0,2*np.pi), weights=distribution,
                                  bins=self.DynamicDistribution.shape[1])
      self.DynamicDistribution[ii,:] = new_dist
    if rolling :
      # Convolution along longitudes
      self.DynamicDistribution = rolling_mean_2d (self.DynamicDistribution,
                                                  win_size=win_size_lon, win_type=win_type_lon,
                                                  axis=1, periodic=True)
      # Convolution along time
      self.DynamicDistribution = rolling_mean_2d (self.DynamicDistribution,
                                                  win_size=win_size_time, win_type=win_type_time,
                                                  axis=0)
    return self.DynamicDistribution

  def searchActiveLongitudes (self, shift_longitude=None, threshold=None,
                             scan_shift_up=30, scan_shift_low=30,
                             lon_low_start=0, rebin=10, step=1) :
    """
    Compute longitudes with maximal spotted area 
    along time direction, assuming the existence of two
    active longitude separated by approximately 180 degrees.
    Note that this function is experimental and might produce
    unexpected results.

    Returns
    -------
    tuple of array
      Tuple with the longitude with maximal spotted area,
      the longitude with maximal spotted area between 0
      and 180 degree, and the longitude with maximal spotted
      area between 180 and 360 degrees.
    """
    if self.LongitudinalDistribution is None :
      raise Exception ("You must compute longitudinal distribution first !")
    distribution = np.copy (self.LongitudinalDistribution)
    distribution = distribution[::step,:]
    longitudes = np.copy (self.longitudes[0,:]) * 180/np.pi
    # Rebinning
    distribution = np.mean (distribution.reshape (-1, distribution.shape[1]//rebin, rebin),
                            axis=-1)
    longitudes = np.mean (longitudes.reshape (longitudes.shape[0]//rebin, rebin), axis=-1)
    # Normalising for each time stamp in the time series
    distribution /= distribution.sum (axis=1, keepdims=True)

    if shift_longitude is not None :
      longitudes = (longitudes + shift_longitude) % 360
      indices = np.argsort (longitudes)
      longitudes, distribution = longitudes[indices], distribution[:,indices]

    if threshold is None :
      threshold = 2 / (distribution.shape[1])

    increment_1, increment_2 = 0, 0
    n_elt = distribution.shape[0]
    lon_max_1, lon_max_2 = np.zeros (n_elt), np.zeros (n_elt)
    significant_1, significant_2 = np.zeros (n_elt), np.zeros (n_elt)
    area_1, area_2 = np.zeros (n_elt), np.zeros (n_elt)
    lon_low = lon_low_start
    lon_up = lon_low + 180 
    lon_low_360 = lon_low % 360
    lon_up_360 = lon_up % 360

    # Tracking the migration in one longitudinal hemisphere
    for ii in range (n_elt) :
        if lon_up_360 > lon_low_360 :
            cond = (longitudes>=lon_low_360)&(longitudes<=lon_up_360)
        else :
            cond = (longitudes>=lon_low_360)|(longitudes<=lon_up_360)
        ind_active_1 = np.argmax (distribution[ii,cond])
        area_active_1 = distribution[ii,cond][ind_active_1]
        
        #Looking for active longitude on the opposite hemisphere
        ind_active_2 = np.argmax (distribution[ii,~cond])
        area_active_2 = distribution[ii,~cond][ind_active_2]
        
        # Dealing with first active longitude
        lon_active_1 = longitudes[cond][ind_active_1]
        if lon_active_1 < lon_low_360 :
            # Means we finished turning around and came back
            # to longitude origin
            increment_1 = lon_up//360
        else :
            increment_1 = lon_low//360
        if area_active_1 > threshold :
            significant_1[ii] = 1
        else :
            significant_1[ii] = 0
        
        lon_max_1[ii] = lon_active_1 + increment_1*360
        area_1[ii] = area_active_1
       
        #Dealing with second active longitude
        lon_active_2 = longitudes[~cond][ind_active_2]
        if lon_active_2 < lon_up_360 :
            # Means we have finished turning for the complementary
            # longitude
            increment_2 = lon_low//360 + 1 
        else :
            increment_2 = lon_up//360
        if area_active_2 > threshold :
            significant_2[ii] = 1
        else :
            significant_2[ii] = 0
        lon_max_2[ii] = lon_active_2 + increment_2*360
        area_2[ii] = area_active_2
        
        # Moving the field where we look
        aux_low, aux_up = lon_low, lon_up
        lon_low = np.minimum (lon_low + scan_shift_low, 
                              lon_active_1 + increment_1*360)
        lon_up = np.minimum (lon_up + scan_shift_up,
                             lon_active_2 + increment_2*360)
        lon_low_360 = lon_low%360
        lon_up_360 = lon_up%360

    return (lon_max_1, area_1, significant_1, 
           lon_max_2, area_2, significant_2)

  def plotActiveLongitudes (self, figsize=(8,4), date_origin=None,
                            phase=False, step=1, shift_longitude=None, 
                            threshold=None, scan_shift_up=30, 
                            scan_shift_low=30, lon_low_start=0,
                            rebin=10, modulo=None) :
    '''
    Plot active longitudes found with ``self.searchActiveLongitudes``.
    '''
    (lon_max_1, area_1, significant_1, 
     lon_max_2, area_2, significant_2) = self.searchActiveLongitudes (shift_longitude=shift_longitude, 
                                           threshold=threshold, scan_shift_up=scan_shift_up, 
                                           scan_shift_low=scan_shift_low, lon_low_start=lon_low_start,
                                           rebin=rebin, step=step) 
    fig, ax = plt.subplots (1, 1, figsize=figsize)
    t = (self.start_time-self.start_time[0])/86400
    if date_origin is not None :
      stamps = Time (date_origin) + t * u.day
      t = stamps.jyear
      xlabel = "Date (year)"
    else :
      xlabel = "Time (day)"
    if phase :
      factor = 1/360
      ylabel = "Phase"
    else :
      factor = 1
      ylabel = r"Longitude ($^o$)"

    Y1 = lon_max_1*factor 
    Y2 = lon_max_2*factor 
    if modulo is not None :
      Y1 = Y1%modulo
      Y2 = Y2%modulo

    ax.scatter (t[::step], Y1, 
                color="red", s=100)
    ax.scatter (t[::step], Y2, 
                color="royalblue", s=100)

    ax.set_xlabel (xlabel)
    ax.set_ylabel (ylabel)
    return fig

def rolling_mean_2d (x, win_size=4, win_type='boxcar', axis=0,
                     periodic=False) :
  '''
  Compute rolling mean with chosen window type on 
  provided array.
  '''
  if axis==0 :
    win = signal.get_window(win_type, win_size).reshape (win_size, -1)
  if axis==1 :
    win = signal.get_window(win_type, win_size).reshape (-1, win_size)
  if periodic :
    averaged = signal.convolve2d(x,  win, 
                                 mode='same', boundary='wrap') / win.sum ()
  else :
    averaged = signal.fftconvolve(x,  win, 
                                  mode='same', axes=None) / win.sum ()
  return averaged

def cross_correlation_periodic (a, b, mode='full', normalise_max=False,
                                normalise_std=True, set_threshold=False, 
                                std=3, boundary='wrap', fillvalue=0) :
  '''
  2d periodic cross-correlation of two arrays.
  '''
  if normalise_max and normalise_std :
    warnings.warn ("""Both choice of normalisation set to True, return  
                      will be normalised according to normalise_std
                      method.""")
  if set_threshold :
    # The threshold is set to try to get a correlation
    # that is less "noisy"
    a = np.copy (a)
    b = np.copy (b)
    # We copy the arrays in order not to do cell operations
    # on the reference memory.
      
    threshold = np.minimum (np.mean (a) + std*np.std (a),
                            np.mean (b) + std*np.std (b))
    a[a<threshold] = 0
    b[b<threshold] = 0
  # The arrays are reshaped because the function only take 2d-arrays
  cc = signal.correlate2d (a.reshape(1,-1) - np.mean(a), 
                           b.reshape(1,-1) - np.mean (b), 
                           mode=mode, boundary=boundary, 
                           fillvalue=fillvalue)[0]
  if normalise_std :
    cc /= np.maximum (a.size, b.size) * np.std (a) * np.std (b)
  elif normalise_max :
    cc /= np.amax (cc)
  return cc

def _wrapper_parallel_longitudinal (model, min_theta, max_theta,
                                    correct_visibility, correction_factor) :
  """
  Wrapper to compute in parallel longitudinal distributions
  of spotmodels.
  """
  longitudinal_distribution = model.computeLongitudinalDistribution (min_theta=min_theta,
                                                          max_theta=max_theta,
                                                          correct_visibility=correct_visibility,
                                                          correction_factor=correction_factor)
  return model, longitudinal_distribution
  
  


