from icalendar import Calendar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable
from selenium.webdriver.common.action_chains import ActionChains


class Command(BaseCommand):
    help = 'Carga horarios UAM desde tu script'

    def handle(self, *args, **options):
        main_function()

def main_function():

    downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UAM"
    subjects_uam = list(Subject.objects.filter(university=2))
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"download.default_directory": downloads_path})
    url = "https://secretaria-virtual.uam.es/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idiomaPais=es.ES"
    
    for subject in subjects_uam[242:]:
        print(subject.subject_key)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.find_element(By.LINK_TEXT, 'Buscar por asignatura').click()
        father_div = driver.find_element(By.CLASS_NAME, 'bootstrap-tagsinput')
        campo_asignatura = father_div.find_element(By.CSS_SELECTOR, 'input[placeholder="Añade asignaturas a tu búsqueda ..."]')
        campo_asignatura.send_keys(subject.subject_key)
        print(subject.subject_key)
        ul_list = father_div.find_element(By.CLASS_NAME, 'active').click()
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'aceptarFiltro'))
        )
        button.click()

        time.sleep(5)
        father_div = driver.find_element(By.CLASS_NAME, 'pull-right')
        schedule = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.ID, 'buscarCalendario'))
        )
        schedule = father_div.find_element(By.ID, 'buscarCalendario')
        schedule.click()
        schedule_file = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'generar'))
        )
        schedule_file.click()
        schedule_file2 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'download'))
        )
        schedule_file2.click()
        time.sleep(1.5)

        files = os.listdir(downloads_path)
        newest_file = max(files, key=lambda x: os.path.getctime(os.path.join(downloads_path, x)))
        subject_instance = Subject.objects.get(id=subject.id)
        schedule_instance = TimeTable(subject=subject_instance)
        schedule_instance.schedule_file_uam = newest_file
        schedule_instance.save()
        driver.quit()