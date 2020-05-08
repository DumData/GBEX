from django.apps import apps
from openpyxl import Workbook

print("running init scripts")
# ------------------------------------------------------
print("Creating bulk template")
template_wb = Workbook()
first_sheet = True
for model in apps.get_app_config('GBEX_app').get_models():
	if hasattr(model, "GBEX_Page"):
		if first_sheet:
			sheet = template_wb.active
			sheet.title = model.__name__
			first_sheet = False
		else:
			sheet = template_wb.create_sheet(model.__name__)
		sheet.append([x for x in model.order if x not in ['id'] and 'file' not in x.lower()])
template_wb.save("static/bulk_template.xlsx")
print("Bulk template script finished")
# ------------------------------------------------------
# Put other init scripts here
# ------------------------------------------------------
print("init scripts finished")
