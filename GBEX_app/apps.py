from django.apps import AppConfig
from importlib import import_module
from glob import glob


class GbexAppConfig(AppConfig):
    name = 'GBEX_app'

    def ready(self):
        # import models
        model_files = glob("GBEX_app/models/*.py")
        model_files.remove("GBEX_app/models/__init__.py")
        model_modules = [import_module(x.replace("/", ".")[:-3]) for x in model_files]

        # initialize the signals
        from GBEX_app import signals

        # check for model symbol collisions
        symbols = [model.symbol for model in self.get_models() if hasattr(model, "GBEX_Page")]
        if len(set(symbols)) != len(symbols):
            raise ValueError(f"Duplicate model symbols detected! {symbols}")
