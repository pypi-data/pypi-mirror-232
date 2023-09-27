import warnings

from django.apps import AppConfig
from django.db import connection


class HuscyApp(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'huscy.data_acquisition_methods.mri'

    class HuscyAppMeta:
        pass

    def ready(self):
        from huscy.project_design.models import DataAcquisitionMethodType

        if 'project_design_dataacquisitionmethodtype' not in connection.introspection.table_names():
            warnings.warn('The migration files of the huscy.project_design app have not yet '
                          'been executed.')
            return

        DataAcquisitionMethodType.objects.get_or_create(
            short_name='mri',
            defaults=dict(
                name='Magnetic resonance imaging',
            ),
        )
