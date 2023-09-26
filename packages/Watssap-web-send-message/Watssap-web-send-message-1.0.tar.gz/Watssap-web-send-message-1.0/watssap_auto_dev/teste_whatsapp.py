from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os
from time import sleep
# from typing import List, Dict
CSS = 'css selector'
CAMPO_PESQUISA = 'div.qh0vvdkp'
CAMPO_MENSAGEM = 'div._3Uu1_ div.to2l77zo'
BUTTON_ENVIAR = 'button.epia9gcq'
SELECIONAR_GRUPO = 'div.g0rxnol2'
OPTIONS_MENSAGEM = 'span.kiiy14zj'
CAMPO_OPTIONS_MENSAGEM = 'ul._3bcLp li'
MARKDOWN_MENSAGENS = 'div.cgi16xlc'
DISABLE_WEB_PAGE = 'div.rv6u8h8g div.cm280p3y'


class ApiWatssap:
    def __init__(self, chat_name: str, not_display: bool = True) -> None:
        """Inicio do bot para a chat unico"""
        self.url: str = 'https://web.whatsapp.com/'
        self.dir_path = os.getcwd()
        self.options = Options()
        if not_display:
            self.options.add_argument('--headless=new')
        self.options.add_argument(
            r"user-data-dir=" + self.dir_path + "profile/zap"
        )
        self.service = Service(ChromeDriverManager().install())
        self.driver = Chrome(self.options, self.service)
        self.driver.get(self.url)
        self.wait = WebDriverWait(
            driver=self.driver,
            timeout=2,
            poll_frequency=.2
        )
        sleep(30)
        self.pesquisar(chat_name)
        self.selecionar_grupo()

    def pesquisar(self, nome: str) -> None:
        self.driver.find_element(CSS, CAMPO_PESQUISA).send_keys(nome)
        return

    def selecionar_grupo(self) -> None:
        self.driver.find_elements(CSS, SELECIONAR_GRUPO)[4].click()
        return

    def send_message(
            self,
            mensagem: str,
            disable_web_page_prevew: bool = False
    ) -> None:

        self.driver.find_element(CSS, CAMPO_MENSAGEM).send_keys(mensagem)
        sleep(1)
        if disable_web_page_prevew:
            try:
                sleep(0.5)
                self.driver.find_elements(CSS, DISABLE_WEB_PAGE)[-1].click()
            except Exception:
                self.driver.find_element(CSS, BUTTON_ENVIAR).click()
                return
        self.driver.find_element(CSS, BUTTON_ENVIAR).click()
        return

    def delete_message(self):
        try:
            self.driver.find_element(CSS, OPTIONS_MENSAGEM).click()
            sleep(0.3)
            self.driver.find_elements(CSS, CAMPO_OPTIONS_MENSAGEM)[1].click()
            sleep(0.3)
            self.driver.find_elements(CSS, MARKDOWN_MENSAGENS)[-1].click()
            sleep(0.3)
            self.driver.find_elements(CSS, 'button.i6inmy1f')[2].click()
            sleep(0.5)
            delete = self.driver.find_elements(
                CSS,
                'button.emrlamx0'
            )
            delete[0].click()
            sleep(0.5)
            delete[-1].click()
        except Exception:
            return


if __name__ == "__main__":
    grupo_name = input('Nome Do Grupo: ')
    a = ApiWatssap(grupo_name)
