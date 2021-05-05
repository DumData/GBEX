import os
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.text import get_valid_filename


class ResumableFile:
	def __init__(self, storage, kwargs):
		self.storage = storage
		self.kwargs = kwargs
		self.chunk_suffix = "_part_"

	@property
	def chunk_exists(self):
		"""Checks if the requested chunk exists."""
		return self.storage.exists(self.current_chunk_name) and self.storage.size(self.current_chunk_name) == int(self.kwargs.get('resumableCurrentChunkSize'))

	@property
	def chunk_names(self):
		"""Iterates over all stored chunks."""
		return [f for f in sorted(self.storage.listdir('')[1]) if f.startswith(f'{self.filename}{self.chunk_suffix}')]

	@property
	def current_chunk_name(self):
		return f"{self.filename}{self.chunk_suffix}{self.kwargs.get('resumableChunkNumber').zfill(9)}"

	def chunks(self):
		"""Iterates over all stored chunks."""
		files = sorted(self.storage.listdir('')[1])
		for f in files:
			if f.startswith(f'{self.filename}{self.chunk_suffix}'):
				yield self.storage.open(f, 'rb').read()

	def delete_chunks(self):
		[self.storage.delete(chunk) for chunk in self.chunk_names]

	@property
	def file(self):
		"""Gets the complete file."""
		if not self.is_complete:
			raise Exception('Chunk(s) still missing')
		return self

	@property
	def filename(self):
		"""Gets the filename."""
		filename = get_valid_filename(self.kwargs.get('resumableFilename'))
		return f"{self.kwargs.get('resumableTotalSize')}_{filename}"

	@property
	def is_complete(self):
		"""Checks if all chunks are already stored."""
		return int(self.kwargs.get('resumableTotalSize')) == self.size

	def process_chunk(self, file):
		if self.storage.exists(self.current_chunk_name):
			self.storage.delete(self.current_chunk_name)
		self.storage.save(self.current_chunk_name, file)

	@property
	def size(self):
		"""Gets chunks size."""
		return sum([self.storage.size(chunk) for chunk in self.chunk_names])


def ensure_dir(f):
	d = os.path.dirname(f)
	os.makedirs(d, exist_ok=True)


def get_chunks_subdir():
	return getattr(settings, 'RESUMABLE_SUBDIR', 'resumable_chunks/')


def get_storage(request):
	"""
	Looks at the ADMIN_RESUMABLE_STORAGE setting and returns
	an instance of the storage class specified.

	Defaults to django.core.files.storage.FileSystemStorage.

	Any custom storage class used here must either be a subclass of
	django.core.files.storage.FileSystemStorage, or accept a location
	init parameter.
	"""
	chunks_upload_to = get_chunks_subdir()
	location = os.path.join(settings.MEDIA_ROOT, chunks_upload_to)
	url_path = urljoin(settings.MEDIA_URL, chunks_upload_to)
	ensure_dir(location)
	storage_class_name = getattr(
		settings,
		'RESUMABLE_STORAGE',
		'django.core.files.storage.FileSystemStorage'
	)
	return get_storage_class(storage_class_name)(location=location, base_url=url_path)
