from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytz
from icalendar import Calendar, Event
import time
import html
from datetime import datetime
import json
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable

class Command(BaseCommand):
    help = 'Carga horarios UAB desde tu script'

    def handle(self, *args, **options):
        main_function()

def main_function():
    try:
        with open('subjects/Data/schedules_UAB.json', 'r') as json_file:
            schedule_info = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        schedule_info = {}

    subjects_uab = list(Subject.objects.filter(university__name='UAB'))

    url = "https://web01.uab.es:31501/pds/consultaPublica/look%5Bconpub%5DInicioPubHora?entradaPublica=true&idioma=ca&pais=ES"
    
    pos = 0
    # for subject in subjects_uab:
    #     if subject.subject_key == 18445:
    #         pos = subjects_uam.index(subject)
    #         print(pos)

    for subject in subjects_uab[pos:]:
        calendario = Calendar()
        print(subject.subject_key)

        # Inicializa una instancia de Chrome en segundo plano con la depuración remota habilitada
        driver = webdriver.Chrome()
        driver.get(url)
        driver.find_element(By.LINK_TEXT, 'Cerca per assignatura').click()
        father_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'bootstrap-tagsinput'))
        )
        father_div.click()
        campo_asignatura = father_div.find_element(By.CSS_SELECTOR, 'input[placeholder="Afegeix assignatures a la teva cerca"]')
        campo_asignatura.send_keys(subject.subject_key)

        try:
            ul_list = father_div.find_element(By.CLASS_NAME, 'active').click()
        except:
            driver.quit()
            continue

        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'aceptarFiltro'))
        )
        button.click()

        time.sleep(1)
        father_div = driver.find_element(By.CLASS_NAME, 'pull-right')
        schedule = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.ID, 'buscarCalendario'))
        )
        schedule = father_div.find_element(By.ID, 'buscarCalendario')
        schedule.click()

        current_url = driver.current_url
        new_url = current_url.replace("look[conpub]MostrarPubHora", "[Ajax]selecionarRangoHorarios")
        new_url = new_url + "&start=1693530000&end=1725090000"
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(new_url)
        body = driver.find_element(By.TAG_NAME, 'body').text
        body = body.split('{')
        body.pop(0)
        
        for event in body:
            event = '{' + event
            event = event[:-1]
            event = json.loads(event)

            evento = Event()
            if 'title' in event:
                if event['title'] == 'Dia no lectiu - ':
                    continue
                evento.add('summary', event['title'])
            else:
                continue
            if 'tipologia' in event:
                if 'grup' in event:
                    evento.add('description', f"{event['tipologia']}, Grupo: {event['grup']}")
                else:
                    evento.add('description', event['tipologia'])
                evento.add('location', event['aula'])
            else:
                evento.add('description', event['className'])

            start_str = event['start']
            end_str = event['end']
            evento.add('dtstart', datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC))
            evento.add('dtend', datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC))
            calendario.add_component(evento)

        driver.quit()
        downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UAB"
        filename = f'{subject.subject_key}_UAB_calendario.ics'
        with open(f'{downloads_path}\\{filename}', 'wb') as f:
            f.write(calendario.to_ical())

        subject_instance = Subject.objects.get(id=subject.id)
        schedule_instance = TimeTable.objects.filter(subject=subject_instance).first()
        if schedule_instance:
            schedule_instance.schedule_file_uab = filename
            schedule_instance.save()
        else:
            schedule_instance = TimeTable(subject=subject_instance, schedule_file_uab=filename)
            schedule_instance.save() 
        schedule_info[subject.subject_key] = filename 
    
    filename = 'subjects\\Data\\schedule_UAB.json'
    json_data = json.dumps(schedule_info)
    with open(filename, 'w') as json_file:
        json_file.write(json_data)


