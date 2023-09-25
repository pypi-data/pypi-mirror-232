from astropy.time import Time
import astropy.units as u
import loupiotes

"""
Some useful functions to work with solar data.
"""

def compute_carrington_longitude (date=None) :
  """
  Compute Carrington longitude of the date passed
  as YYYY-MM-DD.

  Returns
  -------
  tuple
    Tuple with corresponding Carrington rotation
    number and Carrington longitude.
  """
  if date is None :
    date = Time.now ()
  else :
    date = Time (date, scale="utc", format="iso")
  carrington_period = loupiotes.sun_mean_synodic_period
  # Origin of Carrington time.
  # Using what is yielded by 
  # sunpy.coordinates.sun.carrington_rotation_time (1)
  origin = Time ("1853-11-09 21:51:18.538", scale="utc", format="iso")
  diff = date - origin
  carrington_rotation = int (diff.jd / carrington_period) + 1
  fraction = diff.jd / carrington_period - diff.jd // carrington_period
  carrington_longitude = 360 - 360 * fraction
  return carrington_rotation, carrington_longitude
