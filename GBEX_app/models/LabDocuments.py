from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete

from GBEX_bigfiles.fields import ResumableFileField
from GBEX_app.helpers import get_upload_path
from .models import BaseOption, GBEXModelBase, default_order, default_widgets

menu_label = "Lab Documents"


class SOPTag(BaseOption):
	pass


class SOP(GBEXModelBase):
	Summary = models.TextField(blank=True, null=True)
	Tags = models.ManyToManyField(SOPTag, blank=True)
	SOP_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	menu_label = menu_label
	order = [*default_order, 'Summary', 'Tags', 'SOP_file']
	symbol = "SOP"
	col_display_func_dict = {
		'Tags': lambda item: ", ".join(ab.name for ab in item.Tags.all()) if item.Tags.all() else "",
	}
	widgets = {
		**default_widgets,
		'Tags': autocomplete.ModelSelect2Multiple(url=reverse_lazy('SOPTag-autocomplete')),
	}
