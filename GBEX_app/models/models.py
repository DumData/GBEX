from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse_lazy

from dal import autocomplete


# Profile model for storing user settings in a JSON field
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	table_settings = JSONField()

# some defaults for quickly making GBEXModels
default_order = ['id', 'name', 'responsible']
default_widgets = {'Responsible': autocomplete.ModelSelect2(url=reverse_lazy('User-autocomplete')), }


# Base model to capture shared fields
class GBEXModelBase(models.Model):
	name = models.TextField(unique=True)  # All instances need a name. This is typically automatically generated
	responsible = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)  # A user is associated with each object
	# 3 hidden fields that store info on creation/edit date and info on whether this object is archived (not send to frontend)
	created = models.DateTimeField(auto_now_add=True)
	edited = models.DateTimeField(auto_now=True)
	archived = models.BooleanField(default=False)
	batchmodel = ""
	order = default_order  # which order should the fields be displayed in
	symbol = ""  # string for generating name  "symbol" + number
	col_display_func_dict = {}  # custom display functions. Used e.g. for many2many links
	widgets = default_widgets  # custom widgets Used e.g. for autocompletes for foreignkeys
	GBEX_Page = True  # indicate that this is a frontend item
	col_html_string = []  # a list of columns that will be showed as html instead of string
	col_read_only = []  # a list of columns where the GUI will not show an editor

	def __str__(self):
		return self.name

	class Meta:
		abstract = True
		ordering = ['id']


# model for controlled dictionaries. Attached via foreign key
class BaseOption(models.Model):
	name = models.TextField(unique=True)
	created = models.DateTimeField(auto_now_add=True)

	GBEX_Option = True  # used by urls.py to generate autocomplete url

	def __str__(self):
		return self.name

	class Meta:
		abstract = True
		ordering = ['name']


# model for batches. A GBEXModel can have an attached Batch model.
# Each instance of the GBEXModel can have multiple batches.
# These are intended to model multiple real life copies of a GBEXModel.
# E.g. multiple vials with identical content, but different attributes like e.g. experiration date, location, etc.

class AbstractBatch(GBEXModelBase):
	# instanced of this need to have a foreignkey link to a GBEXModel
	# Parent = models.ForeignKey(x, on_delete=models.PROTECT)
	# "batchmodel = thismodel" needs to be set the parent
	GBEX_Page = False

	class Meta:
		abstract = True
