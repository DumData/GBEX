from django.db.models import Field, FileField
from django.core.files.move import file_move_safe
from django.conf import settings
from urllib.parse import unquote
from os import path, makedirs
from .forms import FormResumableFileField
from .widgets import ResumableWidget
from .files import get_chunks_subdir


def safe_media_root():
	if not settings.MEDIA_ROOT.endswith(path.sep):
		media_root = settings.MEDIA_ROOT + path.sep
	else:
		media_root = settings.MEDIA_ROOT
	return media_root


class ResumableFileField(FileField):
	def __init__(self, verbose_name=None, name=None, upload_to='', **kwargs):
		super(ResumableFileField, self).__init__(verbose_name, name, upload_to, **kwargs)

	def pre_save(self, model_instance, add):
		file = Field.pre_save(self, model_instance, add)
		if file and (not file._committed or get_chunks_subdir() in file.name):
			# Commit the file to storage prior to saving the model
			# fpath = file.name.replace(settings.MEDIA_URL, self._safe_media_root())

			# api hack needed due to the way I setup DRF.
			if get_chunks_subdir() not in unquote(file.name):
				fpath = safe_media_root() + get_chunks_subdir() + unquote(file.name)
			else:
				fpath = safe_media_root() + unquote(file.name)

			basename = path.basename(fpath)
			name = self.generate_filename(model_instance, basename)
			new_fpath = file.storage.get_available_name(path.join(self.storage.location, name), max_length=self.max_length)
			basefolder = path.dirname(new_fpath)
			if not file.storage.exists(basefolder):
				makedirs(basefolder)
			file_move_safe(fpath, new_fpath)
			setattr(model_instance, self.name, name)
			file._committed = True
			file.name = name
		return file

	def formfield(self, **kwargs):
		defaults = {
			'form_class': FormResumableFileField,
			'widget': ResumableWidget(attrs={'field_name': self.name})
		}
		kwargs.update(defaults)
		return super(ResumableFileField, self).formfield(**kwargs)
