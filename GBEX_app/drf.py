from functools import partial

from django.apps import apps
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User

from rest_framework import serializers, viewsets, permissions

from GBEX_bigfiles.drf import ResumableDRFFileField
from GBEX_bigfiles.fields import ResumableFileField
from .helpers import get_free_id


GBEX_API_ViewSets = []

# Iterate through all GBEX_app models and create a DRF serializer and viewset
# Special care is taken on the "ResumableFileFields and a default is added to "name" fields
for model in apps.get_app_config('GBEX_app').get_models():
	file_fields = [x.name for x in model._meta.fields if isinstance(x, ResumableFileField)]
	name_dict = {}
	if "name" in [x.name for x in model._meta.fields]:
		name_dict["name"] = serializers.CharField(default=partial(get_free_id, model))

	serial = type(f"{model.__name__}Serializer", (serializers.ModelSerializer, ), {
		**{x: ResumableDRFFileField(required=False, allow_empty_file=True, allow_null=True) for x in file_fields},
		**name_dict,
		"Meta": type(f"{model.__name__}Serializer.Meta", (), {"model": model, "fields": "__all__"})
	})
	viewset = type(f"{model.__name__}ViewSet", (viewsets.ModelViewSet,), {
		"queryset": model.objects.all(),
		"serializer_class": serial,
		"permission_classes": [permissions.IsAuthenticated],
		"filter_fields": '__all__',
		#"filterset_fields": [x.name for x in model._meta.fields if not (isinstance(x, ResumableFileField) or isinstance(x, JSONField))]  # by default filters dont work with resumablefilefield nor JSONfields
	})
	GBEX_API_ViewSets.append((model.__name__, viewset))

# also add the User model
model = User
serial = type(f"{model.__name__}Serializer", (serializers.ModelSerializer, ), {
		"Meta": type(f"{model.__name__}Serializer.Meta", (), {"model": model, "fields": "__all__"})
	})
viewset = type(f"{model.__name__}ViewSet", (viewsets.ModelViewSet,), {
	"queryset": model.objects.all(),
	"serializer_class": serial,
	"permission_classes": [permissions.IsAuthenticated],
	"filter_fields": '__all__',
})
GBEX_API_ViewSets.append((model.__name__, viewset))
