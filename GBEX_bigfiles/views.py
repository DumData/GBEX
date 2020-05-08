from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from sendfile.core import sendfile

from .files import ResumableFile, get_storage
from django.views.decorators.csrf import csrf_exempt
from GBEX_app.helpers import validate_user, get_upload_path


@csrf_exempt
def resumable_upload(request):
	validate_user(request)

	storage = get_storage(request)
	if request.method == 'POST':
		chunk = request.FILES.get('file')
		r = ResumableFile(storage, request.POST)
		if not r.chunk_exists:
			r.process_chunk(chunk)
		if r.is_complete:
			actual_filename = storage.save(r.filename, r.file)
			r.delete_chunks()
			return HttpResponse(storage.url(actual_filename), status=201)
		return HttpResponse('chunk uploaded')
	elif request.method == 'GET':
		r = ResumableFile(storage, request.GET)
		if not r.chunk_exists:
			return HttpResponse('chunk not found', status=404)
		if r.is_complete:
			actual_filename = storage.save(r.filename, r.file)
			r.delete_chunks()
			return HttpResponse(storage.url(actual_filename), status=201)
		return HttpResponse('chunk exists', status=200)


def download_file(request, model, inst_name, filename):
	validate_user(request)  # check if its a authenticated user/token
	model_object = apps.get_model(app_label="GBEX_app", model_name=model)
	model_filter = model_object.objects.filter(name=inst_name)
	if model_filter.exists():
		model_inst = model_filter[0]
		file_path = get_upload_path(model_inst, filename)
		full_file_path = settings.SENDFILE_ROOT + "/" + file_path
		return sendfile(request, full_file_path, attachment=True)
	else:
		raise ObjectDoesNotExist()
