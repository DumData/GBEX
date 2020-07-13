from django.urls import path, re_path, reverse_lazy
from django.forms import modelform_factory
from django.contrib.auth.models import User
from django.apps import apps

from GBEX_app.forms import CreateForm
from GBEX_app.views import GBEXindex, BulkUpdateView, BulkUploadView, GBEXList, GBEXAutocomplete, ExcelExportView, \
	ArchiveView, GBEXUpdateView, GBEXCreateView, GBEXBatchList
from itertools import chain


def url_gen(model, kind):
	mnl = model.__name__
	if kind == 'GBEX_Option':
		return [path(f'{mnl}/autocomplete/', GBEXAutocomplete.as_view(model=model, search_fields=["name"], create_field='name'), name=f'{mnl}-autocomplete'),]
	elif kind == 'GBEX_Page':
		fields = [x.name for x in model._meta.get_fields() if x.name in model.order[2:]] #model.order[2:]
		form_class = modelform_factory(model, form=CreateForm, fields=fields, widgets=model.widgets)

		return [
			path(f'{mnl}/', GBEXList.as_view(model=model), name=f'list_{mnl}'),
			path(f'{mnl}/update/<pk>/<column>', GBEXUpdateView.as_view(model=model, widgets=model.widgets)),
			path(f'{mnl}/bulkupdate/<column>/<rids>', BulkUpdateView.as_view(model=model, widgets=model.widgets)),
			path(f'{mnl}/bulkupload/', BulkUploadView.as_view()),
			re_path(f'{mnl}/exportexcel/(?P<rids>.*)$', ExcelExportView.as_view(model=model),name=f'export_{mnl}'),
			re_path(f'{mnl}/archive/(?P<rids>.*)$', ArchiveView.as_view(model=model), name=f'archive_{mnl}'),
			path(f'{mnl}/create', GBEXCreateView.as_view(model=model, success_url=reverse_lazy(f'list_{mnl}'), form_class=form_class), name=f'create_{mnl}'),
			path(f'{mnl}/autocomplete/', GBEXAutocomplete.as_view(model=model, search_fields=["name"]), name=f'{mnl}-autocomplete'),
		]
	elif kind == 'GBEX_Batch':
		print("not implemented")
		mnl = "Plasmid"
		return [path(f'{mnl}/batch/<pk>', GBEXBatchList.as_view(model=model.batchmodel), name=f'batch_{mnl}'),]
	else:
		raise ValueError(f"kind == '{kind}' not supported")


urlpatterns = [
	path('', GBEXindex.as_view(), name='GBEXindex'),
	path('User/autocomplete/', GBEXAutocomplete.as_view(model=User, search_fields=["username", "first_name", "last_name"]), name='User-autocomplete'),
] + list(chain.from_iterable([url_gen(model, getattr(model, "model_kind")) for model in apps.get_app_config('GBEX_app').get_models() if hasattr(model, "model_kind")]))
