from django.contrib import admin
from .models import usuarios, superuser, arrendatario, propietario, propiedad, documentos

# Register the models.

admin.site.register(usuarios)
admin.site.register(superuser)
admin.site.register(arrendatario)
admin.site.register(propietario)
admin.site.register(propiedad)
admin.site.register(documentos)
