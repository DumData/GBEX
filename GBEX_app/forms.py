from django.forms import ModelForm, IntegerField, FileField, Form, ChoiceField, RadioSelect


class CreateForm(ModelForm):
	duplicater = IntegerField(min_value=1, initial=1, label="Number of new items")


class BulkUploadForm(Form):
	upload_type = ChoiceField(
		label="Upload mode:", widget=RadioSelect,
		choices=(
			('edit', 'edit existing objects (will not create new objects. Will give error if name doesnt exist)',),
			('create', 'create new objects (will not edit existing objects. Will give error if name already exists)',),)
	)
	file = FileField()
