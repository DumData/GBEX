from rest_framework import serializers
from os.path import exists
from .files import get_chunks_subdir
from .fields import safe_media_root


def check_file_exists(value):
	if value.name is None:
		raise serializers.ValidationError
	fpath = safe_media_root() + get_chunks_subdir() + value.name
	if not exists(fpath):
		raise serializers.ValidationError


class ResumableDRFFileField(serializers.FileField):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.validators.append(check_file_exists)

	def to_representation(self, value):
		if not value:
			return None
		request = self.context.get('request', None)
		if request is not None:
			return request.build_absolute_uri(f"/downloads/{value.name}")
		return value.name
