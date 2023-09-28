from datetime import datetime
from json import loads
from sys import getsizeof
from time import sleep
from typing import Dict, List, Tuple
from warnings import filterwarnings
from pprint import pprint

from ecoindex.data.grades import A, B, C, D, E, F, G
import undetected_chromedriver as uc
from ecoindex.ecoindex import get_ecoindex
from ecoindex.models import PageMetrics, PageType, Result, ScreenShot, WindowSize
from pydantic.networks import HttpUrl
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from jinja2 import Environment, FileSystemLoader
from ecoindex_scraper.utils import convert_screenshot_to_webp, set_screenshot_rights
from ecoindex.models import Ecoindex
from ecoindex.ecoindex import get_grade
from scrap import EcoindexScraper
from typing import List

from ecoindex.data.grades import A, B, C, D, E, F, G
from ecoindex.data.quantiles import quantiles_dom, quantiles_req, quantiles_size
from ecoindex.models import Ecoindex

mesures_ecoindex = []
class EcoIndexJourneyScrapper(EcoindexScraper):
    grade: str | None
    driver : any
    def __init__(
        self,
        driver,
    ):
        super().__init__(self)
        print(self.all_requests )
        self.driver = driver
        print(driver)

    @property
    #def driver(self):
    #    return self.driver

   
    def Setdriver(self, value):
        self.driver = value
    
    def _handle_network_data_received(self, eventdata):
        return super()._handle_network_data_received(eventdata)
    def _handle_network_loading_finished(self, eventdata):
        return super()._handle_network_loading_finished(eventdata)
    def _handle_network_response_received(self, eventdata):
        return super()._handle_network_response_received(eventdata)
    
    async def init_chromedriver(self):
        print(self.driver)
        self.driver.add_cdp_listener(
            "Network.dataReceived", self._handle_network_data_received
        )
        self.driver.add_cdp_listener(
            "Network.responseReceived", self._handle_network_response_received
        )
        self.driver.add_cdp_listener(
            "Network.loadingFinished", self._handle_network_loading_finished
        )
        print(self.all_requests)

        if self.page_load_timeout is not None:
            self.driver.set_page_load_timeout(float(self.page_load_timeout))

        return self
    
    async def get_page_ecoindex(self) :
        global mesures_ecoindex
        print(self.driver)
        try:
            page_type = await self.get_page_type()
            page_metrics = await self.get_page_metrics()
        except Exception as e:
            self.__del__()
            raise e
        print(self.driver) 
        ecoindex = await get_ecoindex(
            dom=page_metrics.nodes,
            size=page_metrics.size,
            requests=page_metrics.requests,
        )
        ecoindex_result=Result(
            score=ecoindex.score,
            ges=ecoindex.ges,
            water=ecoindex.water,
            grade=ecoindex.grade,
            url=self.driver.current_url,
            date=datetime.now(),
            #width=self.window_size.width,
            #height=self.window_size.height,
            nodes=page_metrics.nodes,
            size=page_metrics.size,
            requests=page_metrics.requests,
            page_type=page_type,
        )
        mesures_ecoindex.append(ecoindex_result)

    async def calculate_average_score(self):
        global mesures_ecoindex
        # Charge le template à partir du fichier
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('rapport_template.html')
        # Génère le rapport HTML de base
        rapport_html = template.render()
        # Calcul de la somme des scores
        somme_scores = sum(ecoindex_result.score for ecoindex_result in mesures_ecoindex)
        print(somme_scores)
        # Calcul de la moyenne
        if len(mesures_ecoindex) > 0:
            moyenne_scores = somme_scores / len(mesures_ecoindex)
        else:
            moyenne_scores = 0
        print("La moyenne des scores est :", moyenne_scores)
        grade=await get_grade(moyenne_scores)
        print(grade)
        # Charger le template mis à jour avec les résultats
        rapport_html = template.render(mesures_ecoindex=mesures_ecoindex,moyenne_scores=moyenne_scores,grade=grade)
        # Écrit le rapport HTML initial dans un fichier
        with open('rapport.html', 'w') as f:
            f.write(rapport_html)
        print("Le rapport a été généré avec succès.")
        return moyenne_scores
    
