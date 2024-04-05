from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

import requests
import json
import re


def clean_text(text: str) -> str:
    '''
    Returns the same text without html tags and numbers in square brackets.

    :param text: text we want to clean up.
    :return: The cleaned text.
    '''
    cleaned_text = re.sub(r'<.*?>', '', text)
    cleaned_text = re.sub(r'\[\d+\]', '', cleaned_text)
    return cleaned_text

urls_list = ['https://secretaria-virtual.uam.es/doa/consultaPublica/look'
    '[conpub]BuscarPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcade'
    'mico=2023&_centro=104&_planEstudio=445', 'https://secretaria-virtual.uam.'
    'es/doa/consultaPublica/look%5bconpub%5dBuscarPubGuiaDocAs?entradaPublica='
    'true&idiomaPais=es.ES&_anoAcademico=2023&_centro=104&_planEstudio=449', 
    'https://secretaria-virtual.uam.es/doa/consultaPublica/look%5bconpub%5dBus'
    'carPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcademico=2023&_'
    'centro=104&_planEstudio=532', 'https://secretaria-virtual.uam.es/doa/cons'
    'ultaPublica/look%5bconpub%5dBuscarPubGuiaDocAs?entradaPublica=true&idioma'
    'Pais=es.ES&_anoAcademico=2023&_centro=104&_planEstudio=692', 'https://sec'
    'retaria-virtual.uam.es/doa/consultaPublica/look%5bconpub%5dBuscarPubGuiaD'
    'ocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcademico=2023&_centro=104&'
    '_planEstudio=691', 'https://secretaria-virtual.uam.es/doa/consultaPublica'
    '/look%5bconpub%5dBuscarPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&'
    '_anoAcademico=2023&_centro=104&_planEstudio=448', 'https://secretaria-vir'
    'tual.uam.es/doa/consultaPublica/look%5bconpub%5dBuscarPubGuiaDocAs?entrad'
    'aPublica=true&idiomaPais=es.ES&_anoAcademico=2023&_centro=104&_planEstudi'
    'o=672', 'https://secretaria-virtual.uam.es/doa/consultaPublica/look%5bcon'
    'pub%5dBuscarPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcademi'
    'co=2023&_centro=104&_planEstudio=446', 'https://secretaria-virtual.uam.es'
    '/doa/consultaPublica/look%5bconpub%5dBuscarPubGuiaDocAs?entradaPublica=tr'
    'ue&idiomaPais=es.ES&_anoAcademico=2023&_centro=104&_planEstudio=531',
    'https://secretaria-virtual.uam.es/doa/consultaPublica/look%5bconpub%5dBus'
    'carPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcademico=2023&_'
    'centro=104&_planEstudio=711', 'https://secretaria-virtual.uam.es/doa/cons'
    'ultaPublica/look[conpub]BuscarPubGuiaDocAs?entradaPublica=true&idiomaPais'
    '=es.ES&_anoAcademico=2023&_centro=104&_planEstudio=739'
]

# Dictionary from which we will generate the final json.
data = {}

# Subjects in which we are not interested because they have already been taken 
# by the students.
science_subjects = ('CIENCIA Y SOCIEDAD DEL SIGLO XXI', 'CÁLCULO', 
    'QUÍMICA GENERAL', 'BIOLOGÍA', 'GEOLOGÍA', 'ESTADÍSTICA', 'FÍSICA MODERNA',
    'LÓGICA Y FILOSOFÍA DE LA CIENCIA', 'ÁLGEBRA', 'MECÁNICA Y TERMODINÁMICA', 
    'QUÍMICA ORGÁNICA', 'TÉCNICAS INFORMÁTICAS Y BASES DE DATOS', 
    'COMUNICACIÓN Y DIVULGACIÓN DE LA CIENCIA', 'ECUACIONES DIFERENCIALES', 
    'ELECTRICIDAD, ELECTROMAGNETISMO Y ÓPTICA', 'GEOLOGÍA AMBIENTAL',
    'BIOLOGÍA DE ORGANISMOS Y SISTEMAS', 'HISTORIA DE LA CIENCIA', 
    'GESTIÓN Y EVALUACIÓN DE LA CIENCIA', 'TRABAJO DE FIN DE GRADO', 
    'GENES Y AMBIENTE', 'MODELIZACIÓN', 'PRÁCTICAS EXTERNAS'
)

# Other subjects in which we are not interested because they are practically 
# the same as the previous ones.
similar_subjects = ('FÍSICA', 'MATEMÁTICAS', 'MATEMÁTICAS I', 'QUÍMICA',
    'GEOLOGÍA', 'CÁLCULO I', 'ÁLGEBRA LINEAL', 'CONJUNTOS Y NÚMEROS', 
    'BIOQUÍMICA GENERAL', 'BIOLOGÍA GENERAL', 'BIOLOGÍA Y BIOQUÍMICA', 
    'FÍSICA I', 'FUNDAMENTOS DE FÍSICA I', 'FUNDAMENTOS DE FÍSICA II', 
    'ANÁLISIS I', 'ÁLGEBRA I', 'COMPUTACIÓN I', 'FUNDAMENTOS DE QUÍMICA',
    'ELECTROMAGNETISMO I', 'MEDIO AMBIENTE Y SOCIEDAD', 'PRÁCTICAS EXTERNAS I',
    'FUNDAMENTOS DE BIOLOGÍA', 'GENES Y EVOLUCIÓN', 'PRÁCTICAS EXTERNAS II'
    'FUNDAMENDOS DE BIOQUÍMICA', 'QUÍMICA GENERAL I',
    'QUÍMICA INORGÁNICA I', 'QUÍMICA ORGÁNICA I', 'TRABAJO FIN DE GRADO', 
    'TRABAJO FIN DE GRADO MATEMÁTICAS', 'PRÁCTICAS PROFESIONALES', 
    'PRÁCTICAS EXTERNAS DE CIENCIAS AMBIENTALES', 
    'PROYECTO FIN DE GRADO MATEMÁTICAS'
)

for url in urls_list:

    # Mutable variables where we store different data.
    data_subjects = {}
    subject_names = []
    new_subjects = []

    # We get the url of the main page and create a beautiful soup object to 
    # parse it.
    response = requests.get(url=url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # We get the name of the degree.
    degree = soup.find('span', id='plan').text
    degree = degree.split(' ')
    degree.pop(0)
    degree.pop(0)
    degree[0] = 'Grado'
    degree = ' '.join(degree)
    degree = degree + ' | UAM'
    print(degree)

    # We get some information about the different subjects.
    content = soup.find('div', id='content')
    content = content.find('table', id='tablaAsignaturas')
    content = content.find('tbody')
    table_rows = content.find_all('tr', class_=lambda x: x is None, \
                                  recursive=False)

    for row in table_rows:
        row = row.prettify()
        row = clean_text(row)
        lines = row.strip().splitlines()
        lines = [line for line in lines if line.strip()]
        row = '\n'.join(lines)
        new_subjects.append(row)

    # In final_subjects we will have the information we are interested in.
    final_subjects = []
    for subject in new_subjects:
        row = subject.split('\n')
        new_row = []
        for i in row:
            i = i.strip()
            new_row.append(i)
        final_subjects.append(new_row)

    # We save the subjects names.
    for subject in final_subjects:
        subject_names.append(subject[3])

    # Chrome invisible browser driver. 
    #chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome() #options=chrome_options
    driver.get(url=url)

    for name in subject_names:
        # We solved the names with which we have had problems.
        name = re.sub(r'\s+', ' ', name)
        if name in science_subjects or name in similar_subjects:
            final_subjects.pop(0)
            continue
        
        # We obtain the html of each button (teaching guide) and get the 
        # information we are interested in.
        driver.find_element(By.LINK_TEXT, name).click()
        html = driver.page_source
        driver.implicitly_wait(4)

        soup = BeautifulSoup(html, 'html.parser')

        title = soup.find('div', class_='panel-group', id='accordiones')
        title = title.find_all('h2')[1]

        subjects_info = []
        div_content = soup.find_all('div', class_='col-md-12')
        div_content = div_content[len(div_content)//2:]
        for div in div_content:
            div = div.text
            div = div.lstrip()
            if div.startswith('1.7.') or div.startswith('1.8.') \
            or div.startswith('1.11.'):
                div = div.split('\n\n')[1] if '\n\n' in div else 'None'
                subjects_info.append(div)
            if div.startswith('1.13'):
                div = div.split('\n\n')
                div = '\n\n'.join(div[1:])
                div = div.lstrip()
                subjects_info.append(div)

        title = title.text.strip()
        title = title.split(' - ')
        code = title[0]
        title = title[1]

        # We save the subject data.
        if title == 'BIOQUÍMICA':
            if final_subjects[0][4] == '12.0':
                data_subjects[title] = {'Codigo': code, 
                    'Curso': final_subjects[0][0], 
                    'Cuatrimestre': final_subjects[0][5] 
                    if len(final_subjects[0]) == 6 else None, 
                    'Créditos': final_subjects[0][4], 
                    'Idioma': subjects_info[0], 
                    'Coordinador/a': subjects_info[2], 
                    'Requisitos previos': subjects_info[1], 
                    'Guia docente': url, 
                    'Programa': subjects_info[3]
                }
        else:
            data_subjects[title] = {'Codigo': code, 
                'Curso': final_subjects[0][0], 
                'Cuatrimestre': final_subjects[0][5] 
                if len(final_subjects[0]) == 6 else None, 
                'Créditos': final_subjects[0][4], 
                'Idioma': subjects_info[0], 
                'Coordinador/a': subjects_info[2], 
                'Requisitos previos': subjects_info[1], 
                'Guia docente': url, 
                'Programa': subjects_info[3]
            }

        final_subjects.pop(0)
        driver.back()

    # Close selenium driver and save the degree data.
    driver.quit()
    data[degree] = data_subjects

# Create json file.
file_name = "subjectsUAM.json"
with open(file_name, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False)