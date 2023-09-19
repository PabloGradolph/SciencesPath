import requests
from bs4 import BeautifulSoup
import re
import json


url = "https://www.uab.cat/web/estudiar/graus/graus/horaris-1345722992469.html"
schedules = {}

response = requests.get(url=url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table', class_="taula taulaborder")
for table in tables:
    title = 'Grau en ' + table.find('caption').text.strip().lower().capitalize()
    print(title)