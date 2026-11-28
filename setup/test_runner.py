from django.apps import apps
from django.test.runner import DiscoverRunner


class ManagedModelTestRunner(DiscoverRunner):
    """Cria as tabelas dos models managed=False no banco de teste."""

    def setup_test_environment(self, *args, **kwargs):
        super().setup_test_environment(*args, **kwargs)
        self.unmanaged = [m for m in apps.get_models() if not m._meta.managed]
        for m in self.unmanaged:
            m._meta.managed = True

    def teardown_test_environment(self, *args, **kwargs):
        for m in self.unmanaged:
            m._meta.managed = False
        super().teardown_test_environment(*args, **kwargs)