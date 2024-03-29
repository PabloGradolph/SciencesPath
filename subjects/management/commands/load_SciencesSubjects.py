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
import json
import os
import requests
from unicodedata import normalize
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable


class Command(BaseCommand):
    help = 'Carga asignaturas y horarios del Grado en Ciencias'

    def handle(self, *args, **options):
        main_function()

def main_function():
    url = "https://www.uc3m.es/grado/ciencias"

    # Mutable variables where we store different data.
    subjects_info = {}
    subjects_urls = {}
    subjects_links = []
    subjects_names = []
    lenguages_list = []

    # Url of the main page and create a beautiful soup object to parse it.
    response = requests.get(url=url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Name of the degree.
    degree = soup.find('title').text
    print()
    print(degree)
    print()

    # Names, lenguages and links to the teaching guides.
    div_content = soup.find('div', class_='row marcoLiso programaAsignatura')
    links = div_content.find_all('a')
    lenguages = div_content.find_all('img', class_='idioma_img')

    for img in lenguages:
        lenguage = img['alt']
        lenguages_list.append(lenguage)

    print(lenguages_list)
    for a in links:
        link = a['href']
        subject = a.text
        subject = re.sub(r'^(.*?) \([A-Z]\)$', r'\1', subject)
        if "(UC3M)" in subject or "(B1)" in subject or "(B2)" in subject or "(UAM)" in subject or "(UAB)" in subject or "Prácticas Externas" in subject or "Practicas Externas" in subject:
            subjects_links.append(link)
            subjects_names.append(subject)
        else:
            continue

    # Saving de collected information (name: link).
    for i in range(len(subjects_names)):
        subjects_urls[subjects_names[i]] = subjects_links[i]
    
    # For each link, get the desired information.
    for key in subjects_urls:
        print(f"Subject -> {key}")
        if "(UC3M)" in key or "(B1)" in key or "(B2)" in key:
            response = requests.get(url=subjects_urls[key])
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            id = soup.find_all('div', class_='asignatura')
            id = id[1].text[1:-1]
            coord = soup.find('div', class_='col izquierda separar_imgs_mas')
            coord = coord.text.split(': ')[1].rstrip()
            info = soup.find_all('div', class_='col izquierda separar_imgs')
            credits = info[0].text.split(': ')[1].split(' ')[0]
            quarter = info[1].text.split(': ')[1].rstrip()
            year = soup.find_all('div', class_='col izquierda')[1].text
            year = year.split(': ')[1].rstrip()
            requirments = soup.find('div', class_='panel-heading degradado')
            requirments = requirments.text
            programs = soup.find_all('div', class_='panel-heading degradado')

            if quarter != '':
                quarter = quarter[0]
            if year != '':
                year = year[0]
            if requirments.startswith('Requisitos'):
                requirments = soup.find('div', class_='tarea').text.strip()
            else:
                requirments = 'Ninguno'
            
            for p in programs:
                if p.text == 'Descripción de contenidos: Programa':
                    program = p.find_next('div')
                    program = program.find_next('div').text
                    program = normalize("NFKD", program)
            
            subjects_info[key] = {'Código': id, 
                'Curso': year, 
                'Cuatrimestre': quarter, 
                'Créditos': credits, 
                'Idioma': lenguages_list.pop(0),
                'Coordinador/a': coord, 
                'Requisitos previos': requirments, 
                'Guia docente': subjects_urls[key], 
                'Programa': program
            }
        
        elif "(UAM)" in key or "(UAB)" in key:
            response = requests.get(url=subjects_urls[key])
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.find('div', class_='panel-group', id='accordiones')
            title = title.find_all('h2')[1]

            div_content = soup.find_all('div', class_='col-md-12')
            div_content = div_content[len(div_content)//2:]

            data_subject = []
            for div in div_content:
                div = div.text
                div = div.lstrip()
                if div.startswith('1.7.') or div.startswith('1.8.') \
                or div.startswith('1.11.'):
                    div = div.split('\n\n')[1] if '\n\n' in div else 'None'
                    data_subject.append(div)
                if div.startswith('1.13'):
                    div = div.split('\n\n')
                    div = '\n\n'.join(div[1:])
                    div = div.lstrip()
                    data_subject.append(div)

            title = title.text.strip()
            title = title.split(' - ')
            code = title[0]
            title = title[1]

            year = 1
            if "UAB" in key or "(A" in key:
                year = 2
            # We save the subject data.
            subjects_info[key] = {'Codigo': code, 
                'Curso': year, 
                'Cuatrimestre': 2 if "(A" in key else 1, 
                'Créditos': 6, 
                'Idioma': data_subject[0], 
                'Coordinador/a': data_subject[2], 
                'Requisitos previos': data_subject[1], 
                'Guia docente': subjects_urls[key], 
                'Programa': data_subject[3]
            }
    
    file_name = "subjectsSciences.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(subjects_info, f, ensure_ascii=False)
