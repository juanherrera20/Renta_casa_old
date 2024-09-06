from django.contrib import admin
from .models import usuarios, superuser, arrendatario, propietario, inmueble, Documentos, tareas, Imagenes, DocsPersonas

# Register the models.

admin.site.register(usuarios)
admin.site.register(superuser)
admin.site.register(arrendatario)
admin.site.register(propietario)
admin.site.register(inmueble)
admin.site.register(Documentos)
admin.site.register(tareas)
admin.site.register(Imagenes)
admin.site.register(DocsPersonas)
