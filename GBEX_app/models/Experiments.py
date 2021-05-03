from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete

from GBEX_bigfiles.fields import ResumableFileField
from GBEX_app.helpers import get_upload_path

from .models import GBEXModelBase, default_order, default_widgets
from .Inventory import Strain

menu_label = "Experiments"


ReactorVessel = [
	('5L', '5L'),
	('1L', '1L'),
]


class Fermentation(GBEXModelBase):
	RunDate = models.DateTimeField(null=True, blank=True)
	Strain = models.ForeignKey(Strain, on_delete=models.PROTECT, null=True, blank=True)
	ReactorVessel = models.CharField(choices=ReactorVessel, blank=True, null=True, max_length=10)
	Data_file = ResumableFileField(blank=True, null=True, upload_to=get_upload_path, max_length=500)

	menu_label = menu_label
	order = [*default_order, 'RunDate', 'Strain', 'ReactorVessel', 'Data_file']
	symbol = "FE"
	widgets = {
		**default_widgets,
		'Strain': autocomplete.ModelSelect2(url=reverse_lazy('Strain-autocomplete')),
	}
