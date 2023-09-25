import pandas as pd
import numpy as np
import importlib.resources
import loupiotes 
from astropy.io import fits
from astropy.table import Table

'''
Routines to load and manage stored
tables.
'''

def load_limb_darkening_table (name='sing_2010_kepler') :
  '''
  Load one of the stored limb-darkening coefficient table.
  '''
  if name=='sing_2010_kepler' :
    filename = 'sing_2010_kepler.fit'
  else :
    raise Exception ("Unknown table name.")
  with importlib.resources.path (loupiotes.tables, filename) as f :
    hdul = fits.open (f)
    hdu = hdul[1]
    df = Table (data=hdu.data).to_pandas ()
    hdul.close ()

  return df
