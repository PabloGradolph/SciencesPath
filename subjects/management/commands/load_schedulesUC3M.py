from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from typing import Any
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from ...models import Subject, TimeTable

import re
import json
import os


class Command(BaseCommand):
    """
    A command to load and save schedules info from UC3M university in a JSON file.
    """
    help = 'Carga horarios UC3M desde tu script'

    def handle(self, *args: Any, **kwargs: Any) -> None:
        main_function()


def main_function() -> None:

    # Main variables initialized.
    json_filename = 'subjects\\Data\\schedule_UC3M.json'
    if os.path.exists(json_filename):
        with open(json_filename, 'r') as json_file:
            schedule_info = json.load(json_file)
    else:
        schedule_info = {}

    subjects_uc3m = list(Subject.objects.filter(university__name='UC3M'))
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    print(f"Number of subjects -> {len(subjects_uc3m)}")
    pos = 0
    for subject in subjects_uc3m:
        if subject.subject_key == 15508:
            pos = subjects_uc3m.index(subject)
            print(f"Position -> {pos}")

    j = pos
    for subject in subjects_uc3m[pos:]:
        print(f"Subject -> {subject.subject_key}")
        print(f"Loop -> {j}")
        j += 1

        # We go into the url and into the section we are interested in.
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
        
        windows = driver.window_handles
        driver.switch_to.window(windows[-1]) # We are here in Leganes shcedules.

        try: # If we don't find the schedule or it is not published.
            element = driver.find_element(By.XPATH, "//span[contains(text(), 'Asignatura sin horarios definidos para el curso 2023/2024')]")
            driver.quit()
            continue

        except NoSuchElementException: # In case there is an schedule for the subject.
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'horario completo.'))
            )
            button.click()

            tbody_element = driver.find_element(By.TAG_NAME, "tbody")
            tbody_html = tbody_element.get_attribute("outerHTML")
            
            # We have here the html so we initialize the calendar -> Necesary to change the year for future versions.
            soup = BeautifulSoup(tbody_html, 'html.parser')
            calendar = Calendar()
            current_year = 2023

            # Info of events we want to save.
            events = soup.find_all('td', class_="celdaConSesion")

            for event in events:

                # We get the interesting information for each event.
                info = event.text.strip()
                event_title = info.split(',')[0]
                start_hour = re.search(r'(\d{2}:\d{2})\s*a', info).group(1)
                end_hour = re.search(r'a\s*(\d{2}:\d{2})', info).group(1)
                groups_pattern = re.compile(f'{re.escape(event_title)}(.+?){start_hour}')
                groups_mathc = groups_pattern.search(info)
                groups = groups_mathc.group(1).strip() if groups_mathc else "No especificado"
                groups = groups[2:]
                if '⊕' in groups:
                    pattern = r'(grp\.\d+(?:⊕)?|⊕)'
                    coincidence = re.findall(pattern, groups)
                    groups = list(coincidence) if coincidence else "No especificado"
                elif '(' in groups:
                    pattern = r'\((.*?)\)'
                    coincidence = re.search(pattern, groups)
                    groups = str(coincidence.group(1)) if coincidence else "No especificado"
                else:
                    pattern = r'grp\.\d+'
                    coincidence = re.findall(pattern, groups)
                    groups = list(coincidence) if coincidence else "No especificado"
                
                # We are saving here the locations with their dates.
                location_dates = info.split(end_hour)[-1]
                pattern = r'\d{2}\.\w{3}(?:-\d{2}\.\w{3})?(?::(?:Aula|Aula INF|LAB) \d+\.\d+\.\w\d+\.\d+)?'

                dates = re.findall(pattern, location_dates)
                locations = []
                for i in range(len(dates) - 1):
                    current_date = dates[i]
                    next_date = dates[i + 1]
                    pattern = re.escape(current_date) + r'(.*?)' + re.escape(next_date)
                    coincidence = re.search(pattern, location_dates, re.DOTALL)
                    if coincidence:
                        locations.append(coincidence.group(1).strip())
                        
                last_date = dates[-1]
                pattern_last_date = re.escape(last_date) + r'(.*?)$'
                coincidence_last_date = re.search(pattern_last_date, location_dates, re.DOTALL)
                if coincidence_last_date:
                    locations.append(coincidence_last_date.group(1).strip())
                
                # We replaze the months into english lenguage.
                replacements = {
                    'ene': 'jan',
                    'abr': 'apr',
                    'ago': 'aug',
                    'dic': 'dec'
                }
                for i, date in enumerate(dates):
                    for abbreviation, reemplazo in replacements.items():
                        date = date.replace(abbreviation, reemplazo)
                    dates[i] = date
                    
                for i, date in enumerate(dates):
                    location = locations[i]
                    split_dates = date.split('-')
                    
                    # We have events with a start date and an end date -> Events that repeat every 7 days.
                    if len(split_dates) == 2:
                        try:
                            start_date = f'{split_dates[0]}.{current_year}'
                            end_date = f'{split_dates[1]}.{current_year}'

                            # Verify if the date is after first of January.
                            start_date_obj = datetime.strptime(start_date, '%d.%b.%Y')
                            if 1 <= start_date_obj.month <= 8:
                                current_year = 2024
                                start_date = f'{split_dates[0]}.{current_year}'
                                end_date = f'{split_dates[1]}.{current_year}'

                            start_date = datetime.strptime(start_date, '%d.%b.%Y')
                            end_date = datetime.strptime(end_date, '%d.%b.%Y')
                            delta = timedelta(days=7)
                            
                            # We create events from the start_hour until the end_date with a time delta of 7 days.
                            while start_date <= end_date:
                                event = Event()
                                event.add('summary', event_title)
                                if type(groups) == list:
                                    # groups = groups[-1]
                                    event.add('description', f' {groups}')
                                else:
                                    event.add('description', f' {groups}')
                                event.add('dtstart', start_date.replace(hour=int(start_hour.split(':')[0]), minute=int(start_hour.split(':')[1])))
                                event.add('dtend', start_date.replace(hour=int(end_hour.split(':')[0]), minute=int(end_hour.split(':')[1])))
                                event.add('location', location[1:])
                                calendar.add_component(event)
                                start_date += delta

                        except ValueError:
                            print(f'date y/u hora inválida: {start_date}')
                    
                    # Here we have specific events that repeat once, on a single day.
                    else:
                        event = Event()
                        event.add('summary', event_title)
                        if type(groups) == list:
                            groups = groups[-1]
                            event.add('description', f' {groups}')
                        else:
                            event.add('description', f' {groups}')

                        date = f'{date}.{current_year}'
                        start_date_obj = datetime.strptime(date, '%d.%b.%Y')
                        if 1 <= start_date_obj.month <= 8:
                            current_year = 2024
                            date = f'{split_dates[0]}.{current_year}'

                        event.add('dtstart', datetime.strptime(date, '%d.%b.%Y').replace(hour=int(start_hour.split(':')[0]), minute=int(start_hour.split(':')[1])))
                        event.add('dtend', datetime.strptime(date, '%d.%b.%Y').replace(hour=int(end_hour.split(':')[0]), minute=int(end_hour.split(':')[1])))
                        event.add('location', location[1:])
                        calendar.add_component(event)

            downloads_path = "C:\\Users\\Pablo\\OneDrive\\Documentos\\1Programacion\\TFG\\media\\UC3M"
            filename = f'{subject.subject_key}_UC3M_calendario.ics'

            index = 2
            while os.path.exists(f'{downloads_path}\\{filename}'):
                filename = f'{subject.subject_key}_{index}_UC3M_calendario.ics'
                index += 1

            with open(f'{downloads_path}\\{filename}', 'wb') as f:
                f.write(calendar.to_ical())

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

    with open(json_filename, 'w') as json_file:
        json_data = json.dumps(schedule_info, indent=4)
        json_file.write(json_data)