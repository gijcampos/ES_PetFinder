import os
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


class FluxoTutorE2E(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=False, slow_mo=500)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        super().tearDownClass()

    def test_cadastro_login_e_hub(self):
        page = self.browser.new_page()
        page.goto(f"{self.live_server_url}/tutor/cadastro/")
        page.fill("input[name=nome]", "Maria")
        page.fill("input[name=email]", "maria@teste.com")
        page.fill("input[name=telefone]", "41999999999")
        page.fill("input[name=senha]", "senha123")
        page.click("button[type=submit]")

        page.wait_for_url("**/tutor/login/")
        page.fill("input[name=email]", "maria@teste.com")
        page.fill("input[name=senha]", "senha123")
        page.click("button[type=submit]")

        page.wait_for_url(f"{self.live_server_url}/")
        assert "Maria" in page.content()