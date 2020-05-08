from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete

from GBEX_bigfiles.fields import ResumableFileField
from GBEX_app.helpers import get_upload_path

from .models import BaseOption, GBEXModelBase, default_order, default_widgets

menu_label = "Inventory"


class Plasmid(GBEXModelBase):
	Description = models.TextField(blank=True, null=True)
	Genbank_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)
	menu_label = menu_label
	order = [*default_order, 'Description', 'Genbank_file']
	symbol = "PL"


class SpeciesOption(BaseOption):
	pass


class Strain(GBEXModelBase):
	Species = models.ForeignKey(SpeciesOption, on_delete=models.PROTECT)
	Subtype = models.TextField(blank=True, null=True)
	Description = models.TextField(blank=True, null=True)
	Plasmids = models.ManyToManyField(Plasmid, blank=True)
	ParentStrain = models.ForeignKey("self", null=True, on_delete=models.PROTECT)
	Genbank_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	menu_label = menu_label
	order = [*default_order, 'Species', 'Subtype', 'Description', 'Plasmids', 'Genbank_file']
	symbol = "ST"
	col_display_func_dict = {
		'Plasmids': lambda item: ", ".join(ab.name for ab in item.Plasmids.all()) if item.Plasmids.all() else "",
	}
	widgets = {
		**default_widgets,
		'Species': autocomplete.ModelSelect2(url=reverse_lazy('SpeciesOption-autocomplete')),
		'Plasmids': autocomplete.ModelSelect2Multiple(url=reverse_lazy('Plasmid-autocomplete')),
	}
