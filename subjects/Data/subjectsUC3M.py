import requests
from bs4 import BeautifulSoup
import re
import json
from unicodedata import normalize

def clean_text(text: str) -> str:
    '''
    Returns the same text without html tags and numbers in square brackets.    

    :param text: text we want to clean up.
    :return: The cleaned text.
    '''
    cleaned_text = re.sub(r'<.*?>', '', text)
    cleaned_text = re.sub(r'\[\d+\]', '', cleaned_text)
    return cleaned_text

urls_list = ['https://www.uc3m.es/grado/datos', 
    'https://www.uc3m.es/grado/informatica', 
    'https://www.uc3m.es/grado/aeroespacial',
    'https://www.uc3m.es/grado/biomedica', 
    'https://www.uc3m.es/grado/comunicaciones-moviles', 
    'https://www.uc3m.es/grado/energia', 
    'https://www.uc3m.es/grado/telematica',
    'https://www.uc3m.es/grado/sonido-imagen', 
    'https://www.uc3m.es/grado/electrica', 
    'https://www.uc3m.es/grado/electronica',
    'https://www.uc3m.es/grado/tecnologias-industriales', 
    'https://www.uc3m.es/grado/ingenieria-fisica', 
    'https://www.uc3m.es/grado/mecanica', 'https://www.uc3m.es/grado/robotica', 
    'https://www.uc3m.es/grado/matematica-aplicada'
]

# Subjects in which we are not interested because they have already been taken
# by the students.
science_sujects2 = ('CIENCIA Y SOCIEDAD DEL SIGLO XXI', 'CÁLCULO', 
    'QUÍMICA GENERAL', 'BIOLOGÍA', 'GEOLOGÍA', 
    'LÓGICA Y FILOSOFÍA DE LA CIENCIA', 'ÁLGEBRA', 'MECÁNICA Y TERMODINÁMICA', 
    'QUÍMICA ORGÁNICA', 'TÉCNICAS INFORMÁTICAS Y BASES DE DATOS', 
    'COMUNICACIÓN Y DIVULGACIÓN DE LA CIENCIA', 'ECUACIONES DIFERENCIALES', 
    'ELECTRICIDAD, ELECTROMAGNETISMO Y ÓPTICA', 
    'BIOLOGÍA DE ORGANISMOS Y SISTEMAS', 'GEOLOGÍA AMBIENTAL',
    'HISTORIA DE LA CIENCIA', 'ESTADÍSTICA', 
    'GESTIÓN Y EVALUACIÓN DE LA CIENCIA', 'TRABAJO DE FIN DE GRADO', 
    'FÍSICA MODERNA', 'GENES Y AMBIENTE', 'MODELIZACIÓN', 'PRÁCTICAS EXTERNAS'
)

science_sujects = []
for subject in science_sujects2:
    subject = subject.lower()
    subject = subject.capitalize()
    science_sujects.append(subject)

# Other subjects in which we are not interested because they are practically 
# the same as the previous ones.
similar_subjects = ('Física', 'Álgebra lineal', 'Programación', 
    'Programacion', 'Prácticas Externas', 'Cálculo I', 'Fisica I', 
    'Trabajo Fin de Grado', 'Calculo I', 'Algebra Lineal',
    'Trabajo de Fin de Grado', 'Prácticas Externas I', 'Prácticas Externas II',
    'Física I', 'Fisica', 'Química', 'Quimica', 'Ecuaciones Diferenciales',
    'Química I', 'Quimica I', 'Trabajo fin de grado', 'Cálculo Diferencial', 
    'Álgebra Lineal', 'Calculo', 'Estadistica', 'Prácticas externas I',
    'Habilidades profesionales interpersonales', 'Prácticas externas II', 
    'Prácticas externas', 'Prácticas Externas (A), (B), (C), (D), (E), (F)', 
    'Habilidades profesionales Interpersonales', 'Habilidades: Humanidades', 
    'Habilidades: Humanidades I', 'Habilidades: Humanidades II', 
    'Habilidades profesionales interprofesionales', 'Humanidades II',
    'Habilidades Profesionales Interpersonales', 'Humanidades I',  
    'Toma de decisión inteligente en robótica', 
    'Prácticas externas (a), (b), (c), (d), (e),'
)

# Dictionary from which we will generate the final json.
data = {}

for url in urls_list:

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

    for a in links:
        link = a['href']
        subject = a.text
        subject = re.sub(r'^(.*?) \([A-Z]\)$', r'\1', subject)
        if subject in science_sujects or subject in similar_subjects:
            continue
        else:
            subjects_links.append(link)
            subjects_names.append(subject)

    # Saving de collected information (name: link).
    for i in range(len(subjects_names)):
        subjects_urls[subjects_names[i]] = subjects_links[i]
    
    # For each link, get the desired information.
    for key in subjects_urls:
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

    data[degree] = subjects_info

file_name = "subjectsUC3M.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
