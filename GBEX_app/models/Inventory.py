from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete

from GBEX_bigfiles.fields import ResumableFileField
from GBEX_app.helpers import get_upload_path

from .models import BaseOption, GBEXModelBase, default_order, default_widgets


class InventoryItem(GBEXModelBase):
	Usage = models.TextField(blank=True, null=True)
	Location = models.TextField(blank=True, null=True)

	menu_label = "Inventory"

	class Meta:
		abstract = True


class Primers(InventoryItem):
	Sequence = models.TextField(blank=True, null=True)

	order = [*default_order, "Usage", "Sequence", "Location"]
	symbol = "PR"


class AntibioticOption(BaseOption):
	pass


class Plasmid(InventoryItem):
	CommonName = models.TextField(blank=True, null=True)
	Genotype = models.TextField(blank=True, null=True)
	Antibiotic = models.ManyToManyField(AntibioticOption, blank=True)
	Genbank_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	order = [*default_order, 'CommonName', 'Usage', 'Antibiotic', 'Genbank_file', 'Location']
	symbol = "PL"

	col_display_func_dict = {
		'Antibiotic': lambda item: ", ".join(ab.name for ab in item.Antibiotic.all()) if item.Antibiotic.all() else "",
	}
	widgets = {
		**default_widgets,
		'Antibiotic': autocomplete.ModelSelect2Multiple(url=reverse_lazy('AntibioticOption-autocomplete')),
	}


class SpeciesOption(BaseOption):
	pass


class VendorOption(BaseOption):
	pass


class Strain(InventoryItem):
	CommonName = models.TextField(blank=True, null=True)
	Species = models.ForeignKey(SpeciesOption, on_delete=models.PROTECT)
	Subtype = models.TextField(blank=True, null=True)
	Antibiotic = models.ManyToManyField(AntibioticOption, blank=True)
	Genotype = models.TextField(blank=True, null=True)
	Vendor = models.ForeignKey(VendorOption, blank=True, null=True, on_delete=models.PROTECT)
	CatalogNo = models.TextField(blank=True, null=True)
	TubesLeft = models.PositiveIntegerField(blank=True, null=True)
	TubeVolume = models.PositiveIntegerField(blank=True, null=True)
	Plasmids = models.ManyToManyField(Plasmid, blank=True)
	ParentStrain = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
	Genbank_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	order = [*default_order, 'CommonName', 'Species', 'Subtype', 'Usage', 'ParentStrain', 'Antibiotic', 'Genotype',
			 'Plasmids', 'Genbank_file', 'Vendor', 'CatalogNo', 'TubesLeft', 'TubeVolume', 'Location']
	symbol = "ST"
	col_display_func_dict = {
		'Plasmids': lambda item: ", ".join(ab.name for ab in item.Plasmids.all()) if item.Plasmids.all() else "",
		'Antibiotic': lambda item: ", ".join(ab.name for ab in item.Antibiotic.all()) if item.Antibiotic.all() else "",
	}
	widgets = {
		**default_widgets,
		'Species': autocomplete.ModelSelect2(url=reverse_lazy('SpeciesOption-autocomplete')),
		'Vendor': autocomplete.ModelSelect2(url=reverse_lazy('VendorOption-autocomplete')),
		'ParentStrain': autocomplete.ModelSelect2(url=reverse_lazy('Strain-autocomplete')),
		'Plasmids': autocomplete.ModelSelect2Multiple(url=reverse_lazy('Plasmid-autocomplete')),
		'Antibiotic': autocomplete.ModelSelect2Multiple(url=reverse_lazy('AntibioticOption-autocomplete')),
	}


class CellLine(InventoryItem):
	CommonName = models.TextField(blank=True, null=True)
	Species = models.ForeignKey(SpeciesOption, on_delete=models.PROTECT)
	Genotype = models.TextField(blank=True, null=True)

	order = [*default_order, 'CommonName', 'Usage', 'Species', 'Genotype', 'Location']
	symbol = "CL"

	widgets = {
		**default_widgets,
		'Species': autocomplete.ModelSelect2(url=reverse_lazy('SpeciesOption-autocomplete')),
	}
