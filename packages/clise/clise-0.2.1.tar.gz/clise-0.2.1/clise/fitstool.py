
if 'clise' in __file__:
	import clise.tabletool as tt
	import clise.rabbit as rb
else:
	import tabletool as tt
	import rabbit as rb

import numpy as np
import re
import math as m
from os		import path
from pathlib	import Path
from astropy.io	import fits
from functools    import wraps
from collections  import OrderedDict

def read_multiple_images_deco_(func):

	# turning this into an iterator would be better
	@wraps(func)
	def read_multiple_images(*args, infile=None, 
		hdu=0, tagid='',  outfile=None,
		include=None, exclude=None,
		recursive_search=True, **kwpars):

		if infile is None: exit()

		infiles = rb.search_infile(infile, tagid=tagid, 
				    include=include, exclude=exclude,
				    recursive_search=recursive_search, 
				    onlylist=False)

		nfiles = len(infiles)

		w2r = OrderedDict() # what to read

		w2w = outfile
		if outfile is not None:
			w2w = OrderedDict()

		for key in infiles:
			val = infiles[key]
			cfile = val['name']

			if type(hdu) is list:  
				# check all the blocks
				if len(hdu) == 0:
					hdul = fits.open(cfile)
					hdus = []
					for id, chdu in enumerate(hdul):
						# skip table
						htype = type(chdu).__name__
						if 'Table' in htype: continue

						# skip empty block
						if type(chdu.data).__name__ == 'NoneType': 
							continue
						hdus.append(chdu.name)
					hdul.close()
				else:
					hdus = hdu
					nimages = nimages + len(hdu)

				# everything like images
			else:
				hdus = [hdu]
			w2r[cfile] = hdus
			if outfile is not None:
				# not taking full advantage of rabbit.py features
				# better way to do this
				w2w[cfile] = rb.apply_tag(outfile, infiles[key]['tag'])

		# print(w2r)
		if outfile is not None:
			kwpars['outfile'] = w2w
		return func(*args, infile=w2r, **kwpars)

	return read_multiple_images

def read_multiple_images_deco(func):

	# turning this into an iterator would be better
	@wraps(func)
	def read_multiple_images(*args, infile=None, 
		hdu=0, tagid='',  outfile=None, id=None,
		include=None, exclude=None,
            start=0, stop=None, 
		recursive_search=True, **kwpars):

		if infile is None: 
			print("No infile. exiting...")
			exit()

		infiles = rb.search_infile(infile, tagid=tagid, 
				    include=include, exclude=exclude,
				    recursive_search=recursive_search, 
				    onlylist=False)

		nfiles = len(infiles)

		w2r = [] # what to read

		for key in infiles:
			val = infiles[key]
			cfile = val['name']
			new = OrderedDict()
			new['infile'] = cfile
			new['tag'] = val['tag']
			if id is not None:
				new['id'] = rb.apply_tag(id, val['tag'])
			if outfile is not None:
				# not taking full advantage of rabbit.py features
				# better way to do this
				new['outfile'] = rb.apply_tag(outfile, val['tag'])

			if type(hdu) is list:  
				# check all the blocks
				if len(hdu) == 0:
					hdul = fits.open(cfile)
					for id, chdu in enumerate(hdul):
						# skip table
						htype = type(chdu).__name__
						if 'Table' in htype: continue

						# skip empty block
						if type(chdu.data).__name__ == 'NoneType': 
							continue
						new['hdu']  = chdu.name
						w2r.append(new)
					hdul.close()
				else:
					for chdu in hdu:
						new['hdu']  = chdu
						w2r.append(new)

				# everything like images
			else:
				new['hdu']  = hdu
				w2r.append(new)

		if outfile is not None:
			kwpars['outfile'] = outfile

		infile=[]
		for idx, each in enumerate(w2r):
			if idx < start: continue
			if stop is not None: 
				if idx > stop: continue
			infile.append(each)

		return func(*args, infile=infile, **kwpars)

	return read_multiple_images
