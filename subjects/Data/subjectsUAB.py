from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import re
import json
import requests


urls_list = ['https://www.uab.cat/web/estudiar/listado-de-grados/plan-de'
    '-estudios/guias-docentes-1345467811508.html?param1=1231400870814',
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1224052400443', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1231400886500', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1231314915924', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1224150562736', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1231491110582', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1231491113526', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1345879397331', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1216102930384', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1264404714557', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1228117321093', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1216102918128', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1345740824235', 
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1345879691832',
    'https://www.uab.cat/web/estudiar/listado-de-grados/plan-de-estudios/guias'
    '-docentes-1345467811508.html?param1=1263194083206'
]

# Subjects in which we are not interested because they have already been taken
# by the students.
science_subjects = ('Bioestadística', 'Física', 'Matemàtiques', 
    'Química', 'Treball de Final de Grau', 'Pràctiques externes', 'Bioquímica',
    'Treball de final de grau', 'Pràcticum en empreses o institucions',
    'Bioquímica I', 'Pràcticum en empreses i institucions',
    'Pràctiques en empreses i institucions', 'Fonaments de química',
    'Química orgànica', 'Treball de fi de grau', 'Treball de fin de grau',
    'Pràcticum', 'Pràctiques professionals', 'Àlgebra I', 'Càlcul I', 'Càlcul'
    'Equacions Diferencials', 'Pràctiques Externes', 'Àlgebra Lineal', 
    'Càlcul 1', 'Introducció a la Programació', 'Àlgebra lineal',
    'Pràctiques Professionals de la Modalitat Analista',
    'Pràctiques Professionals de la Modalitat Assessor', 
    'Fonaments de geologia', 'Funcions de variable real', 
    'Fonaments de les matemàtiques', 'Estadística', 'Pràctiques en empreses',
    'Càlcul en Una Variable', 'Iniciació a la Programació',
    'Equacions Diferencials Ordinàries', 'Física I', 'Matemàtiques I',
    'Fonaments de Química I'
    )

# Dictionary from which we will generate the final json.
data = {}

for url in urls_list:

    # Mutable variable where we store different data.
    subjects_links = {}
    subjects_info = {}

    # We get the url of the page and create a beautiful soup object to parse 
    # it.
    response = requests.get(url=url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # We get the name of the degree.
    degree = soup.find('span', class_='subtitle').text.strip()
    degree += " | UAB"
    print()
    print(degree)
    print()

    # We obtain the name of each subject with its link.
    subjects = soup.find('div', class_='contingut', id='main')
    subjects = subjects.find_all('p')

    patron = r' - (.+?)\xa0'
    for subject in subjects[2:]:
        a = subject.find('a')
        if a:
            link = a['href']
            title = a.text
            match = re.search(patron,title)
            if match:
                match = match.group(1)
            else:
                match = title.split(' - ')[1]
            subjects_links[match] = link

    for name in subjects_links:
        
        if name in science_subjects:
            continue

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url=subjects_links[name])

        driver.find_element(By.LINK_TEXT, 'espanyol').click()
        html = driver.page_source
        driver.implicitly_wait(4)

        soup = BeautifulSoup(html, 'html.parser')

        info = soup.find('div', class_='assignaturaInfo').text
        result = re.findall(r'\b\w+\b', info)
        title = []
        for i in result:
            if i != 'Código':
                title.append(i)
            else:
                break
        title = ' '.join(title)
        print(title)
        code = re.search(r'Código: (\d+)', info).group(1)
        credits = re.search(r'Créditos ECTS: (\d+)', info).group(1)
        coordinator = soup.find('div', class_='contacte')
        coordinator = coordinator.find('dd').text
        lenguage = soup.find('div', class_='idiomes')
        lenguage = lenguage.find('dd').text.split(' ')[0] if lenguage else '-'
        
        year = soup.find('div', class_='relacions')
        year = year.find('tbody')
        quarter = year.find_all('td')[3].text
        year = year.find_all('td')[2].text
        requirments = soup.find('div', class_='prerequisits')
        requirments = requirments.find('p')
        if requirments:
            requirments = requirments.text
        else:
            requirments = '-'
        program = soup.find('div', class_='continguts')
        h2 = program.find('h2').extract()
        program = program.get_text(strip=False)

        subjects_info[title] = {'Código': code, 
            'Curso': year, 
            'Cuatrimestre': quarter, 
            'Créditos': credits, 
            'Idioma': lenguage, 
            'Coordinador/a': coordinator, 
            'Requisitos previos': requirments, 
            'Guia docente': subjects_links[name], 
            'Programa': program
        }

    # We save the data.
    data[degree] = subjects_info

# Create json file.
file_name = "subjectsUAB.json"
with open(file_name, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False)