import numpy



def Dimensions(image):
	""" This function finds the image dimensions.
		Args:
			image: The image to analyze.
		Returns:
			Width (int), Height (int), #Channels (int), Are the channels first (bool)?
	"""

	if len(image.shape) == 2: # Gray level images.
		shape = image.shape
		channels = 1
		width = shape[1]
		height = shape[0]
		first = True
	elif image.shape[0] < image.shape[1] and image.shape[0] < image.shape[2]: # channel first
		shape = image.shape
		channels = shape[0]
		width = shape[2]
		height = shape[1]
		first = True
	elif image.shape[2] < image.shape[0] and image.shape[2] < image.shape[1]: # channel last
		shape = image.shape
		channels = shape[2]
		width = shape[1]
		height = shape[0]
		first = False
	else:
		raise Exception("Dimensions not found.")

	return width, height, channels, first



def AddMoveChannels(image, First: bool=True):
	"""
	This method places the color channel in the required position. If the image's dimensions is 2, then a color channel
	is added.
	:param image: The image to modify (if necessary).
	:param First: Where to place the channels? If True, the channels will be placed in first position, last otherwise.
	:return: The image with the channels moved/added (if necessary).
	"""
	w, h, channels, f = Dimensions(image)
	if len(image.shape) == 2:
		if First:
			return image[numpy.newaxis, :, :]
		else:
			return image[:, :, numpy.newaxis]
	elif len(image.shape) == 3:
		if First:
			if f:
				return image
			else:
				return numpy.moveaxis(image, -1, 0)
		else:
			if f:
				return numpy.moveaxis(image, 0, -1)
			else:
				return image
	else:
		raise Exception("Image dimension is not 2 or 3: " + len(image.shape))



def isBig(array) -> bool:
	if isinstance(array, numpy.ndarray):
		if array.dtype == numpy.int8 or array.dtype == numpy.uint8:
			mult = 1
		elif array.dtype == numpy.int16 or array.dtype == numpy.uint16:
			mult = 2
		elif array.dtype == numpy.int32 or array.dtype == numpy.uint32 or array.dtype == numpy.floatt32:
			mult = 4
		elif array.dtype == numpy.int64 or array.dtype == numpy.uint64 or array.dtype == numpy.float64:
			mult = 8
		length = array.size * mult
	else:
		if array.mode in {'L', 'P'}:
			mult = 1
		elif array.mode == 'I;16':
			mult = 2
		elif array.mode == 'RGB':
			mult = 3
		elif array.mode in {'RGBA', 'I', 'F'}:
			mult = 1
		length = array.size[0] * array.size[1] * mult
	return False if length <= 4294967295 else True
