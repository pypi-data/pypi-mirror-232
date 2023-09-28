
# from os		import path, makedirs, chdir, getcwd, getenv, mkdir

import numpy as np
import re
import math as m
from os		import path
from pathlib	import Path
from astropy.io	import fits

from astropy.table import QTable
from collections  import OrderedDict


if 'clise' in __file__:
	import clise.tabletool as tt
	import clise.rabbit  as rb
else:
	import tabletool as tt
	import rabbit  as rb

def new_ext(filename, new):
	return re.sub(r'\.[^\.]+$', '.' + new, filename)

def raw2fits(infile, outfile=None, size=None, dtype='int16', 
		 clobber=True, verbose=0, dry=False):
	""" raw images to fits """

	infile_ = str(Path(infile).expanduser())
	if not path.isfile(infile_):
		print("No file named", infile)
		return

	if outfile is None:
		outfile=new_ext(infile_, 'fits.gz')

	if size is None:
		print("No size given")
		return

		# instat = Path(infile_).stat()
		# insize = instat.st_size
		# xsize = m.sqrt(insize)

	if verbose >0:
		print(infile, infile_, outfile, size, dtype)
		
	if dry:
		print('dry run')
		return

	img = np.fromfile(infile_,dtype=dtype, sep='')
	img = img.reshape(size)

	hdu = fits.PrimaryHDU(img)
	hdu.writeto(outfile, overwrite=clobber)

def mraw2fits(infile, outfile=None, size=None, dtype='int16', 
		sumfile=None, id=None,
		crop=None, ftype=None,
		clobber=True, verbose=0, dry=False,
		tagid='', 
		include=None, exclude=None,
		start=0, stop=None, 
		recursive_search=True):
	""" raw images to fits """

	# if outfile is None:
	# 	outfile=new_ext(infile, 'fits.gz')

	if size is None:
		print("No size given")
		return

		# instat = Path(infile_).stat()
		# insize = instat.st_size
		# xsize = m.sqrt(insize)

	infiles = rb.search_infile(infile, tagid=tagid, 
				    include=include, exclude=exclude,
				    recursive_search=recursive_search, onlylist=False)

	if verbose >0:
		print(infile,  outfile, size, dtype)

	if outfile is not None:
		if crop is None:
			images= np.ndarray((len(infiles), size[0], size[1]))
		else:
			images= np.ndarray((len(infiles), crop[1]-crop[0], crop[3]-crop[2]))

	idxs    = []
	ids     = []
	means   = []
	stds    = []
	medians = []
	mins    = []
	maxs    = []

	# import plottool as pt
	for idx, key in enumerate(infiles):
		if idx < start: continue
		if stop is not None: 
			if idx > stop: continue

		infile_ = str(Path(infiles[key]['name']).expanduser())
		if verbose >1:
			print(infile__, infile_)
		if not path.isfile(infile_):
			print("No file named", infile__)
			continue
			
		ftype_ = ftype
		if ftype_ is None:
			if   bool(re.search(r'\.fits(|\.gz)$', infile_)):
				ftype_ = "fits"

		if ftype_ is None:
			img = np.fromfile(infile_,dtype=dtype, sep='')
			img = img.reshape(size)
		else:
			if ftype_ == "fits":
				img = fits.getdata(infile_, ext=0)

		if crop is not None:
			img = img[crop[0]:crop[1],crop[2]:crop[3]]
		if outfile is not None:
			images[idx, :,:] = img

		if id is not None:
			# ids.append(infiles[key]['tag'][id])
			# ids.append(int(rb.apply_tag(id, infiles[key]['tag'])))
			val = rb.apply_tag(id, infiles[key]['tag'])
			try:
				val = float(val)
			except:
				pass
			ids.append(val)
		else:
			ids.append(infiles[key]['id'])

		idxs    .append(idx)
		means   .append(np.mean  (img))
		stds    .append(np.std   (img))
		medians .append(np.median(img))
		mins    .append(np.min   (img))
		maxs    .append(np.max   (img))

		# pt.embed()

	if dry:
		print('dry run')
		return

	if outfile is not None:
		hdu  = fits.PrimaryHDU(images) 
		hdul = fits.HDUList([hdu])
		hdul.writeto(outfile, overwrite=clobber)

	if sumfile is not None:
		table = [idxs, ids, means, stds, medians, mins, maxs]
		names = ["index", "id", "mean", "std", "median", "min", "max"]
		header = OrderedDict()
		data   = QTable(table, names=names, meta=header)
		data.write(sumfile, overwrite=True)
		# tt.to_fits(sumfile, data, overwrite=True)
		# tt.to_csv_or_fits(sumfile, data, overwrite=True)

