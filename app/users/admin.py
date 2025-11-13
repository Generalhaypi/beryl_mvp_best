from django.contrib import admin
from .models import *

# Enregistrement automatique des modèles de l'app dans l'interface admin
for model_name, model in list(globals().items()):
    try:
        if hasattr(model, '_meta'):
            admin.site.register(model)
    except Exception:
        pass
