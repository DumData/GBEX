from django.db import models
from django.urls import reverse_lazy, reverse

from dal import autocomplete

from GBEX_bigfiles.fields import ResumableFileField
from GBEX_app.helpers import get_upload_path

from .models import BaseOption, GBEXModelBase, AbstractBatch, default_order, default_widgets, default_readonly

menu_label = "Inventory"


class PlasmidBatch(AbstractBatch):
	Parent = models.ForeignKey("Plasmid", on_delete=models.PROTECT)
	Barcode = models.TextField(blank=True, null=True)
	SequenceVerified = models.BooleanField(default=False)

	menu_label = menu_label
	order = [*default_order, 'Barcode', 'SequenceVerified', 'Parent']
	symbol = "PL_Batch"

	col_read_only = [*default_readonly, 'Parent']


class Plasmid(GBEXModelBase):
	Description = models.TextField(blank=True, null=True)
	Genbank_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	menu_label = menu_label
	order = [*default_order, 'Description', 'Genbank_file', 'Batches']
	symbol = "PL"
	batchmodel = PlasmidBatch
	col_display_func_dict = {
		'Batches': lambda item: f"<a href='{reverse('list_PlasmidBatch', kwargs=dict(parent_pk=item.pk))}'>{item.plasmidbatch_set.filter(archived=False).count()} batches</a>",
		'Genbank_file': lambda item: f"<a href='/downloads/{item.Genbank_file}'>{str(item.Genbank_file).split('/')[-1]}</a>",
	}

	col_html_string = ['Genbank_file', 'Batches']
	col_read_only = [*default_readonly, 'Batches']


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
