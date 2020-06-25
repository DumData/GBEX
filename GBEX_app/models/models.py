from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete


# Profile model for storing user settings
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	table_settings = JSONField()


default_order = ['id', 'name', 'responsible']
default_widgets = {'Responsible': autocomplete.ModelSelect2(url=reverse_lazy('User-autocomplete')), }


# Base model to capture shared fields
class GBEXModelBase(models.Model):
	name = models.TextField(unique=True)
	responsible = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)
	edited = models.DateTimeField(auto_now=True)
	archived = models.BooleanField(default=False)

	order = default_order
	symbol = ""
	col_display_func_dict = {}
	widgets = default_widgets
	GBEX_Page = True

	def __str__(self):
		return self.name

	class Meta:
		abstract = True
		ordering = ['id']


class BaseOption(models.Model):
	name = models.TextField(unique=True)
	created = models.DateTimeField(auto_now_add=True)

	GBEX_Option = True

	def __str__(self):
		return self.name

	class Meta:
		abstract = True
		ordering = ['name']


