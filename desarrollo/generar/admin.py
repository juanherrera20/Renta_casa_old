from django.contrib import admin
from .models import usuarios, superuser, arrendatario, propietario, inmueble, documentos, tareas

# Register the models.

admin.site.register(usuarios)
admin.site.register(superuser)
admin.site.register(arrendatario)
admin.site.register(propietario)
admin.site.register(inmueble)
admin.site.register(documentos)
admin.site.register(tareas)
