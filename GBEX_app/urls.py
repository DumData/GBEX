from django.urls import path
from django.forms import modelform_factory
from django.contrib.auth.models import User
from django.apps import apps

from GBEX_app.forms import CreateForm
from GBEX_app.views import GBEXindex, BulkUpdateView, BulkUploadView, GBEXList, GBEXAutocomplete, ExcelExportView, \
	ArchiveView, GBEXUpdateView, GBEXCreateView
from itertools import chain


def url_gen(model, kind):
	mnl = model.__name__  # save the model name, because we will use it a lot

	# If this is a GBEX_Option, then just return an Autocomplete path
	if kind == 'GBEX_Option':
		return [path(f'{mnl}/autocomplete/', GBEXAutocomplete.as_view(model=model, search_fields=["name"], create_field='name'), name=f'{mnl}-autocomplete'),]

	# If its not an Option, then its either a Page or a Batch which largely shares paths
	fields = [x.name for x in model._meta.get_fields() if x.name in model.order and x.name not in model.col_read_only]
	form_class = modelform_factory(model, form=CreateForm, fields=fields, widgets=model.widgets)

	if kind == 'GBEX_Page':
		path_prefix = f"{mnl}"
	elif kind == 'GBEX_Batch':  # a batch needs to know its parents pk value
		path_prefix = f"{mnl}/<parent_pk>"
	else:
		raise ValueError(f"kind == '{kind}' not supported")

	return [
		path(f'{path_prefix}/', GBEXList.as_view(model=model), name=f'list_{mnl}'),
		path(f'{path_prefix}/update/<pk>/<column>', GBEXUpdateView.as_view(model=model, widgets=model.widgets)),
		path(f'{path_prefix}/bulkupdate/<column>/<rids>', BulkUpdateView.as_view(model=model, widgets=model.widgets)),
		path(f'{path_prefix}/bulkupload/', BulkUploadView.as_view()),
		path(f'{path_prefix}/exportexcel/', ExcelExportView.as_view(model=model), name=f'export_{mnl}'),
		path(f'{path_prefix}/exportexcel/<rids>', ExcelExportView.as_view(model=model), name=f'export_{mnl}'),
		path(f'{path_prefix}/archive/<rids>', ArchiveView.as_view(model=model), name=f'archive_{mnl}'),
		path(f'{path_prefix}/create', GBEXCreateView.as_view(model=model, form_class=form_class), name=f'create_{mnl}'),
		path(f'{path_prefix}/autocomplete/', GBEXAutocomplete.as_view(model=model, search_fields=["name"]), name=f'{mnl}-autocomplete'),
	]


urlpatterns = [
	path('', GBEXindex.as_view(), name='GBEXindex'),
	path('User/autocomplete/', GBEXAutocomplete.as_view(model=User, search_fields=["username", "first_name", "last_name"]), name='User-autocomplete'),
] + list(chain.from_iterable([url_gen(model, getattr(model, "model_kind")) for model in apps.get_app_config('GBEX_app').get_models() if hasattr(model, "model_kind")]))
