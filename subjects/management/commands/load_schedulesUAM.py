from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable
import time
import os
import json


class Command(BaseCommand):
    help = 'Carga horarios UAM desde tu script'

    def handle(self, *args, **options):
        main_function()

def main_function() -> None:

    # Main variables initialized.
    schedule_info = {}
    downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UAM"
    subjects_uam = list(Subject.objects.filter(university__name='UAM'))
    
    # Set up the driver.
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("prefs", {"download.default_directory": downloads_path})
    url = "https://secretaria-virtual.uam.es/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idiomaPais=es.ES"
    
    # Piece of code executed in case we want execute starting from a specific subject.
    pos = 0
    # for subject in subjects_uam:
    #     if subject.subject_key == 18440:
    #         pos = subjects_uam.index(subject)
    #         print(f"Posicion -> {pos}")
    
    # Start the loop from the position of the subject we want (0 in case we want to execute the hole script)
    for subject in subjects_uam[pos:]:

        # Initialize the driver going to the url and send the keys of the subject in the correct academic year.
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.find_element(By.LINK_TEXT, 'Buscar por asignatura').click()
        select_element = driver.find_element(By.ID, "planDocente")
        select_object = Select(select_element)
        select_object.select_by_value("2023")
        father_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'bootstrap-tagsinput'))
        )
        father_div.click()
        campo_asignatura = father_div.find_element(By.CSS_SELECTOR, 'input[placeholder="Añade asignaturas a tu búsqueda ..."]')
        campo_asignatura.send_keys(subject.subject_key)

        try:
            ul_list = father_div.find_element(By.CLASS_NAME, 'active').click()
        except:
            driver.quit()
            continue

        # Accept the filter -> The subject key.
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'aceptarFiltro'))
        )
        button.click()

        # Go to the calendar page (we wait in order to avoid problems)
        time.sleep(5)
        father_div = driver.find_element(By.CLASS_NAME, 'pull-right')
        schedule = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.ID, 'buscarCalendario'))
        )
        schedule = father_div.find_element(By.ID, 'buscarCalendario')
        schedule.click()

        # Generate and download the calendar into the correct path (driver options).
        schedule_file = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'generar'))
        )
        schedule_file.click()
        schedule_file2 = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'download'))
        )
        schedule_file2.click()
        time.sleep(1.5)

        # We rename the downloaded file which the name we want.
        files = os.listdir(downloads_path)
        newest_file = max(files, key=lambda x: os.path.getctime(os.path.join(downloads_path, x)))
        new_file_name = f"{str(subject.subject_key)}_UAM_calendario.ics"
        full_new_path = os.path.join(downloads_path, new_file_name)

        # When the subject key is repeted...
        index_file = 2
        while os.path.exists(full_new_path):
            new_file_name = f"{str(subject.subject_key)}_{index_file}_UAM_calendario.ics"
            full_new_path = os.path.join(downloads_path, new_file_name)
            index_file += 1

        os.rename(os.path.join(downloads_path, newest_file), os.path.join(downloads_path, new_file_name))
        
        # Save the info into the database.
        subject_instance = Subject.objects.get(id=subject.id)
        schedule_instance = TimeTable.objects.filter(subject=subject_instance).first()
        if schedule_instance:
            schedule_instance.schedule_file_uam = new_file_name
            schedule_instance.save()
        else:
            schedule_instance = TimeTable(subject=subject_instance, schedule_file_uam=new_file_name)
            schedule_instance.save()
        driver.quit()
    
    # When everything is executed we create a json file with all the information.
    filename = 'subjects\\Data\\schedule_UAM.json'
    with open(filename, 'w') as json_file:
        for subject in subjects_uam:
            if subject.subject_key in schedule_info.keys():
                schedule_info[f"{subject.subject_key}_2"] = f"{str(subject.subject_key)}_2_UAM_calendario.ics"
            else:
                
                schedule_info[subject.subject_key] = f"{str(subject.subject_key)}_UAM_calendario.ics"
        json_data = json.dumps(schedule_info)
        json_file.write(json_data)
