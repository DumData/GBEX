# GBEX - Goodbye Excel: A MetaDataStore and more

### What is this?
This is a system for replacing excel based registration sheets with a web-based database backed solution.  
It uses Django as the backend and a custom REACT based frontend.   
You setup database models and then the system should be able to understand that and create GUI and API access to them.

### Quickstart
docker-compose up -d  
After docker finishes you should create a superuser  
docker exec -ti -u worker gbex_gbex_1 python manage.py createsuperuser  
  
Then you should be able to visit:
   1) Main page: http://localhost
   2) DRF API: http://localhost/api
   3) OpenAPI swagger: http://localhost/swagger
   4) OpenAPI redoc: http://localhost/redoc

### Todos
Move models col_display_func_dict into helpers.field_to_string for many2many fields
Come up with solution to recognize file fields (other than looking for "file" in column name)
Make a custom thing to check on delete whether object is used in Many-to-many relation and if so, prevent deletion