from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from icalendar import Calendar, Event
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import os
import json
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable


class Command(BaseCommand):
    help = 'Carga horarios UC3M desde tu script'

    def handle(self, *args, **options):
        main_function()

def main_function():
    try:
        with open('subjects/Data/schedules_UC3M.json', 'r') as json_file:
            schedule_info = json.load(json_file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        schedule_info = {}
    
    subjects_uc3m = list(Subject.objects.filter(university__name='UC3M'))
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    pos = 0
    for subject in subjects_uc3m:
        if subject.subject_key == 15976:
            pos = subjects_uc3m.index(subject)
            print(pos)

    for subject in subjects_uc3m[pos:]:
        print(subject.subject_key)
        print(subject.name)
        print(subject.degree)
        url = subject.subject_url
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        div = driver.find_element(By.CLASS_NAME, 'container-fluid')
        div = div.find_element(By.CLASS_NAME, 'justify-content-around')
        div = div.find_element(By.CLASS_NAME, 'col-xs-5')
        div = div.find_element(By.CLASS_NAME, 'col-xs-12')
        img = div.find_element(By.CLASS_NAME, 'separar_imgs')
        if img:
            img.click()
        
        ventanas = driver.window_handles
        driver.switch_to.window(ventanas[-1])
        try:
            elemento = driver.find_element(By.XPATH, "//span[contains(text(), 'Asignatura sin horarios definidos para el curso 2023/2024')]")
            driver.quit()
            continue
        except NoSuchElementException:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'horario completo.'))
            )
            button.click()

            tbody_element = driver.find_element(By.TAG_NAME, "tbody")
            tbody_html = tbody_element.get_attribute("outerHTML")
            
            soup = BeautifulSoup(tbody_html, 'html.parser')
            calendario = Calendar()
            año_actual = datetime.now().year
            lista_eventos = []
            eventos = soup.find_all('td', class_="celdaConSesion")

            for evento in eventos:
                info_evento = {}
                info = evento.text.strip()
                titulo_evento = info.split(',')[0]
                hora_inicio = re.search(r'(\d{2}:\d{2})\s*a', info).group(1)
                hora_fin = re.search(r'a\s*(\d{2}:\d{2})', info).group(1)
                grupos_pattern = re.compile(f'{re.escape(titulo_evento)}(.+?){hora_inicio}')
                grupos_match = grupos_pattern.search(info)
                grupos = grupos_match.group(1).strip() if grupos_match else "No especificado"
                grupos = grupos[2:]
                if '⊕' in grupos:
                    patron = r'(grp\.\d+(?:⊕)?|⊕)'
                    coincidencia = re.findall(patron, grupos)
                    grupos = list(coincidencia) if coincidencia else "No especificado"
                elif '(' in grupos:
                    patron = r'\((.*?)\)'
                    coincidencia = re.search(patron, grupos)
                    grupos = str(coincidencia.group(1)) if coincidencia else "No especificado"
                else:
                    patron = r'grp\.\d+'
                    coincidencia = re.findall(patron, grupos)
                    grupos = list(coincidencia) if coincidencia else "No especificado"
                
                fechas_ubicaciones = info.split(hora_fin)[-1]
                numero_fechas = len(fechas_ubicaciones.split(':')) - 1
                patron = r'\d{2}\.\w{3}(?:-\d{2}\.\w{3})?(?::(?:Aula|Aula INF|LAB) \d+\.\d+\.\w\d+\.\d+)?'

                fechas = re.findall(patron, fechas_ubicaciones)
                ubicaciones = []
                for i in range(len(fechas) - 1):
                    fecha_actual = fechas[i]
                    fecha_siguiente = fechas[i + 1]
                    patron = re.escape(fecha_actual) + r'(.*?)' + re.escape(fecha_siguiente)
                    coincidencia = re.search(patron, fechas_ubicaciones, re.DOTALL)
                    if coincidencia:
                        ubicaciones.append(coincidencia.group(1).strip())
                        
                ultima_fecha = fechas[-1]
                patron_ultima_fecha = re.escape(ultima_fecha) + r'(.*?)$'
                coincidencia_ultima_fecha = re.search(patron_ultima_fecha, fechas_ubicaciones, re.DOTALL)
                if coincidencia_ultima_fecha:
                    ubicaciones.append(coincidencia_ultima_fecha.group(1).strip())
                
                reemplazos = {
                    'ene': 'jan',
                    'abr': 'apr',
                    'ago': 'aug',
                    'dic': 'dec'
                }
                for i, fecha in enumerate(fechas):
                    for abreviacion, reemplazo in reemplazos.items():
                        fecha = fecha.replace(abreviacion, reemplazo)
                    fechas[i] = fecha
                    
                for i, fecha in enumerate(fechas):
                    ubicacion = ubicaciones[i]
                    
                    fechas_divididas = fecha.split('-')
                    
                    if len(fechas_divididas) == 2:
                        try:
                            fecha_inicio = f'{fechas_divididas[0]}.{año_actual}'
                            fecha_fin = f'{fechas_divididas[1]}.{año_actual}'
                            if fecha_inicio == '29.feb.2023':
                                fecha_inicio = '01.mar.2023'
                            if fecha_fin == '29.feb.2023':
                                fecha_fin = '01.mar.2023'
                            fecha_inicio = datetime.strptime(fecha_inicio, '%d.%b.%Y')
                            fecha_fin = datetime.strptime(fecha_fin, '%d.%b.%Y')
                            delta = timedelta(days=7)
                            
                            while fecha_inicio <= fecha_fin:
                                evento = Event()
                                evento.add('summary', titulo_evento)
                                if type(grupos) == list:
                                    # grupos = grupos[-1]
                                    evento.add('description', f' {grupos}')
                                else:
                                    evento.add('description', f' {grupos}')
                                evento.add('dtstart', fecha_inicio.replace(hour=int(hora_inicio.split(':')[0]), minute=int(hora_inicio.split(':')[1])))
                                evento.add('dtend', fecha_inicio.replace(hour=int(hora_fin.split(':')[0]), minute=int(hora_fin.split(':')[1])))
                                evento.add('location', ubicacion[1:])
                                calendario.add_component(evento)
                                fecha_inicio += delta

                        except ValueError:
                            print(f'Fecha y/u hora inválida: {fecha_inicio}')
                    else:
                        evento = Event()
                        evento.add('summary', titulo_evento)
                        if type(grupos) == list:
                            grupos = grupos[-1]
                            evento.add('description', f' {grupos}')
                        else:
                            evento.add('description', f' {grupos}')
                        fecha = f'{fecha}.{año_actual}'
                        if fecha == '29.feb.2023':
                            fecha = '01.mar.2023'
                        evento.add('dtstart', datetime.strptime(fecha, '%d.%b.%Y').replace(hour=int(hora_inicio.split(':')[0]), minute=int(hora_inicio.split(':')[1])))
                        evento.add('dtend', datetime.strptime(fecha, '%d.%b.%Y').replace(hour=int(hora_fin.split(':')[0]), minute=int(hora_fin.split(':')[1])))
                        evento.add('location', ubicacion[1:])
                        calendario.add_component(evento)

            downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UC3M"
            filename = f'{subject.subject_key}_UC3M_calendario.ics'
            with open(f'{downloads_path}\\{filename}', 'wb') as f:
                f.write(calendario.to_ical())

            subject_instance = Subject.objects.get(id=subject.id)
            schedule_instance = TimeTable.objects.filter(subject=subject_instance).first()
            if schedule_instance:
                schedule_instance.schedule_file_uc3m = filename
                schedule_instance.save()
            else:
                schedule_instance = TimeTable(subject=subject_instance, schedule_file_uc3m=filename)
                schedule_instance.save() 
            schedule_info[subject.subject_key] = filename      

            driver.quit()

    filename = 'subjects\\Data\\schedule_UC3M.json'
    json_data = json.dumps(schedule_info)
    with open(filename, 'w') as json_file:
        json_file.write(json_data)