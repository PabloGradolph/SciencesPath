from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import json
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable


class Command(BaseCommand):
    help = 'Carga horarios UAM desde tu script'

    def handle(self, *args, **options):
        main_function()

def main_function():

    with open('subjects/Data/schedule_UAM.json', 'r') as json_file:
        schedule_info = json.load(json_file)

    downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UAM"
    subjects_uam = list(Subject.objects.filter(university=2))
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"download.default_directory": downloads_path})
    url = "https://secretaria-virtual.uam.es/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idiomaPais=es.ES"
    
    pos = 0
    # for subject in subjects_uam:
    #     if subject.subject_key == 18445:
    #         pos = subjects_uam.index(subject)
    #         print(pos)
    
    for subject in subjects_uam[pos:]:
        print(subject.subject_key)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.find_element(By.LINK_TEXT, 'Buscar por asignatura').click()
        father_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'bootstrap-tagsinput'))
        )
        father_div.click()
        campo_asignatura = father_div.find_element(By.CSS_SELECTOR, 'input[placeholder="Añade asignaturas a tu búsqueda ..."]')
        campo_asignatura.send_keys(subject.subject_key)
        print(subject.subject_key)

        try:
            ul_list = father_div.find_element(By.CLASS_NAME, 'active').click()
        except:
            driver.quit()
            continue
        # try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'aceptarFiltro'))
        )
        button.click()
        # except TimeoutException:
        #     driver.quit()
        #     continue

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

        # Save the info in the dictionary and in the database.
        files = os.listdir(downloads_path)
        newest_file = max(files, key=lambda x: os.path.getctime(os.path.join(downloads_path, x)))
        new_file_name = f"{str(subject.subject_key)}_{newest_file}"
        os.rename(os.path.join(downloads_path, newest_file), os.path.join(downloads_path, new_file_name))
        subject_instance = Subject.objects.get(id=subject.id)
        schedule_instance = TimeTable.objects.filter(subject=subject_instance).first()

        if schedule_instance:
            schedule_instance.schedule_file_uam = new_file_name
            schedule_instance.save()
        else:
            schedule_instance = TimeTable(subject=subject_instance, schedule_file_uam=new_file_name)
            schedule_instance.save()
        schedule_info[subject.subject_key] = new_file_name
        driver.quit()
    
    filename = 'schedule_UAM.json'
    json_data = json.dumps(schedule_info)
    with open(filename, 'w') as json_file:
        json_file.write(json_data)
