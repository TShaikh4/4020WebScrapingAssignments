### Talha Shaikh - 218095257 // ITEC 4020 ASSIGNMENT 2
### Python program to scrape data from Wikipedia country pages and save it to a CSV file
### The program will then calculate and display the max values and Pearson correlation coefficient

###IMPORT STATEMENTS & LINK INITIALIZATION
import requests
from bs4 import BeautifulSoup
import csv
import re
import math

country_links = [
    "https://en.wikipedia.org/wiki/Canada",
    "https://en.wikipedia.org/wiki/China",
    "https://en.wikipedia.org/wiki/United_States",
    "https://en.wikipedia.org/wiki/Korea",
    "https://en.wikipedia.org/wiki/United_Kingdom",
    "https://en.wikipedia.org/wiki/France",
    "https://en.wikipedia.org/wiki/Turkey",
    "https://en.wikipedia.org/wiki/Italy"
]

###FUNCTIONS TO SCRAPE COUNTRY CATEGORIES AND DATA

def scrape_country_names(country_links):
    country_names = []
    for link in country_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        country_name = soup.find(id="firstHeading").text
        country_names.append(country_name)
    return country_names

def scrape_capital(country_links):
    capitals = []
    for link in country_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        infobox = soup.find('table', class_='infobox')
        
        if infobox:
            rows = infobox.find_all('tr')
            capital_found = False
            
            for row in rows:
                th = row.find('th', {'scope': 'row'})
                if th:
                    if 'capital' in th.text.lower() or 'largest city' in th.text.lower():
                        capital_element = row.find('td').find('a') or row.find('td')
                        if capital_element:
                            capitals.append(capital_element.get_text(strip=True))
                            capital_found = True
                            break
        
            if not capital_found:
                capitals.append('')
        else:
            capitals.append('')
    
    return capitals

def scrape_languages(country_links):
    languages = []
    for link in country_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        language_info = ''
        infobox = soup.find('table', class_='infobox')
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                th = row.find('th', {'scope': 'row'})
                if th:
                    header_text = th.text.strip().lower()  
                    if 'language' in header_text:
                        td = row.find('td')
                        if td:
                            ul = td.find('ul')
                            if ul:
                                language_info = ', '.join([li.text.strip().split('[')[0] for li in ul.find_all('li')])
                            else:
                                language_info = re.sub(r'\[.*?\]', '', td.text.strip())
                            break

        languages.append(language_info)

    return languages

def scrape_area(country_links):
    areas = []
    for link in country_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')

        area_info = ''
        infobox = soup.find('table', class_='infobox')
        if infobox:
            rows = infobox.find_all('tr')
            for row in rows:
                th = row.find('th', {'scope': 'row'})
                if th and ('area' in th.text.lower() or 'total' in th.text.lower()):
                    td = row.find('td')
                    if td:
                        area_info = td.get_text(separator=' ').strip()
                        area_info = re.sub(r'\[.*?\]', '', area_info)
                        area_info = area_info.replace('\xa0', ' ')
                        break

        areas.append(area_info)

    return convert_to_km2(areas)

def convert_to_km2(area_strings):
    #Converting area values from strings to numbers and then km2 if neccesary
    area_km2 = []
    for area in area_strings:
        matches = re.findall(r'[\d,]+(?:\.\d+)?', area)
        if matches:
            if 'km' in area:
                km2_values = [float(match.replace(',', '')) for match in matches if 'km' in area]
                km2_value = km2_values[0] if km2_values else None
            elif 'sq mi' in area:
                sq_mi_values = [float(match.replace(',', '')) for match in matches if 'sq mi' in area]
                km2_value = sq_mi_values[0] * 2.58999 if sq_mi_values else None
            else:
                km2_value = float(matches[0].replace(',', ''))
            area_km2.append(km2_value)
        else:
            area_km2.append(None)  

    return area_km2

def scrape_population(country_links):
    populations = []

    for link in country_links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        population = None
        rows = soup.find_all('tr', class_='mergedrow')

        for row in rows:
            header = row.find('th', class_='infobox-label')
            data = row.find('td', class_='infobox-data')

            if header and data:
                header_text = header.get_text(strip=True).lower()

                if 'estimate' in header_text or 'population' in header_text:
                    population_text = data.get_text(strip=True)
                    match = re.search(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', population_text)

                    if match:
                        population_str = match.group()
                        population_str = population_str.replace(',', '')

                        try:
                            population = int(float(population_str))
                        except ValueError:
                            population = None
                        break

        populations.append(population)

    return populations

def scrape_gdp(country_links):
    gdp_values = []
    for link in country_links:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        text_content = soup.get_text()
        
        gdp_pattern = r'\$\d+(\.\d+)?\s+trillion'
        gdp_match = re.search(gdp_pattern, text_content)
        
        if gdp_match:
            gdp_value = gdp_match.group(0)
            gdp_value = int(float(re.sub(r'[^\d.]', '', gdp_value)) * 1e12) #convert back to a full num bc wiki stores this data as ex. 5 trillion
            gdp_values.append(gdp_value)
        else:
            gdp_values.append(None)
    
    return gdp_values

###WRITING OUR SCRAPED DATA IN A CSV FILE
def save_to_csv(country_links):
    country_names = scrape_country_names(country_links)
    capitals = scrape_capital(country_links)
    languages = scrape_languages(country_links)
    areas = scrape_area(country_links)
    populations = scrape_population(country_links)
    gdps = scrape_gdp(country_links)

    with open('country_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Country', 'Capital', 'Languages', 'Area (km²)', 'Population', 'GDP (USD)'])

        for data in zip(country_names, capitals, languages, areas, populations, gdps):
            writer.writerow(data)

### CREATING CSV FILE ###
save_to_csv(country_links)
print('Done scraping and saving!')

### STEP 3 MAX VALUES
def find_max_values(filename):
    max_population = None
    max_population_country = None
    max_area = None
    max_area_country = None
    max_gdp = None
    max_gdp_country = None
    
    with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if max_population is None or float(row['Population']) > float(max_population):
                max_population = row['Population']
                max_population_country = row['Country']
            
            if max_area is None or float(row['Area (km²)']) > float(max_area):
                max_area = row['Area (km²)']
                max_area_country = row['Country']
            
            if max_gdp is None or float(row['GDP (USD)']) > float(max_gdp):
                max_gdp = row['GDP (USD)']
                max_gdp_country = row['Country']
    
    return {
        'max_population': max_population,
        'max_population_country': max_population_country,
        'max_area': max_area,
        'max_area_country': max_area_country,
        'max_gdp': max_gdp,
        'max_gdp_country': max_gdp_country
    }

filename = 'country_data.csv'
max_values = find_max_values(filename)

print("Country with the highest population:", max_values['max_population_country'], "(", max_values['max_population'], ")")
print("Country with the largest area:", max_values['max_area_country'], "(", max_values['max_area'], "km²)")
print("Country with the highest GDP:", max_values['max_gdp_country'], "(", max_values['max_gdp'], "USD)")

### STEP 4 PEARSON CORRELATION COEFFICIENT FUNCTION & EXECUTION
def pearson_correlation(x, y):
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = 0
    denominator_x = 0
    denominator_y = 0
    for i in range(n):
        numerator += (x[i] - mean_x) * (y[i] - mean_y)
        denominator_x += (x[i] - mean_x) ** 2
        denominator_y += (y[i] - mean_y) ** 2
    
    denominator = math.sqrt(denominator_x * denominator_y)
    
    if denominator == 0:
        return 0  
    else:
        return numerator / denominator


#CALCULATE CORRELATIONS
area_population_correlation = pearson_correlation(scrape_area(country_links), scrape_population(country_links))
area_gdp_correlation = pearson_correlation(scrape_area(country_links), scrape_gdp(country_links))
population_gdp_correlation = pearson_correlation(scrape_population(country_links), scrape_gdp(country_links))

#PRINT RESULTS
print("Correlation between area and population:", area_population_correlation)
print("Correlation between area and GDP:", area_gdp_correlation)
print("Correlation between population and GDP:", population_gdp_correlation)
print("Program done runngin")