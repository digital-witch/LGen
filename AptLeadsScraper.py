import requests
import csv
import random
from bs4 import BeautifulSoup

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}


class Response404(Exception):
    pass

class ProxyFileDoesNotExist(Exception):
    pass

def loadProxyFile(filename):
    IPs = []
    try:
        file = open(filename, 'r')
    except FileNotFoundError:
        raise ProxyFileDoesNotExist
    for line in file:
        IPs.append(line)
    return IPs

def scrapeSearch(city, stateCode, numberOfResults: int, proxy_list = []):

    #to start, we need to make sure our number of requested results falls within the number of results that are available
    #when you try to go to a page that doesn't exist on apartments.com it simply redirects you to the first page with no error
    #so we're just going to load the page once to grab the number of available apartments and adjust the number of results according to that

    try:
        response = requests.get(f'https://www.apartments.com/apartments/{city}-{stateCode}/', headers=header)
    except Exception as ex:
        print(ex)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        apartmentsAvailable = int(soup.find('h3', {'class': 'count'}).text.strip().split(' ')[0].replace(',' ,''))
        if apartmentsAvailable < numberOfResults:
            resultsRemaining = apartmentsAvailable
        else:
            resultsRemaining = numberOfResults

        pages = []
        resultsURLs = []



        for i in range((resultsRemaining // 25) + 1):
            pages.append(f'https://www.apartments.com/apartments/{city}-{stateCode}/{i+1}')
        for page in pages:
            if proxy_list:
                random_proxy = random.randint(0, len(proxy_list) - 1)
                proxy = {
                    'http': proxy_list[random_proxy]
                }
                try:
                    response = requests.get(page, headers=header, proxies=proxy)
                except Exception as ex:
                    print(ex)
                    pass
            else:
                try:
                    response = requests.get(page, headers=header)
                except Exception as ex:
                    print(ex)
                    pass
            soup = BeautifulSoup(response.text, 'html.parser')

            propertyListingsDiv = soup.find('div', {'class': 'placardContainer'})
            properties = propertyListingsDiv.findAll('article', {'class': 'placard'})
            for index,propertyListing in enumerate(properties):
                if resultsRemaining and index <= 24:
                    propertyURL = str(propertyListing).split('href="')[1].split('"')[0]
                    resultsURLs.append(propertyURL)
                    resultsRemaining -= 1
                else:
                    break
        return resultsURLs
    elif response.status_code == 404:
        raise Response404

def scrapeApartmentInfo(url, proxy_list = []):
    if proxy_list:
        random_proxy = random.randint(0, len(proxy_list) - 1)
        proxy = {
            'http': proxy_list[random_proxy]
        }
        try:
            response = requests.get(url, headers=header, proxies=proxy)
        except Exception as ex:
            print(ex)
            pass
    else:
        try:
            response = requests.get(url, headers=header)
        except Exception as ex:
            print(ex)
            pass
    soup = BeautifulSoup(response.text, 'html.parser')

    #Complex Name block
    complexName = soup.find('h1', {'class': 'propertyName'}).text.strip()

    #Complex Address block
    propertyAddressDiv = soup.find('div', {'class': 'propertyAddress'})
    propertyAddressSpanList = propertyAddressDiv.findAll('span') #0=address, 1=city, 2=state, 3=zip code, 4=neighborhood link
    del propertyAddressSpanList[4] #we don't care about the neighborhood...
    complexAddress = propertyAddressSpanList[0].text
    complexCity = propertyAddressSpanList[1].text
    complexState = propertyAddressSpanList[2].text
    complexZip = propertyAddressSpanList[3].text
    #complexFullAddress = ''
    #for index, span in enumerate(propertyAddressSpanList):
    #    complexFullAddress += span.text

    #Contact Number block
    contactNumber = soup.find('span', {'class': 'contactPhone'}).text

    #Number of Units block
    numberOfUnits = 0
    propertyInfoDiv = soup.find('div', {'class': 'propertyFeatures'})
    propertyInfoLiList = propertyInfoDiv.findAll('li')
    for li in propertyInfoLiList:
        li = str(li)
        if 'Units' in li: #we could use .text like we did with the others, but we'd have to strip the complex story count and the leading bullet point anyways...
            numberOfUnits = int(li.split('</span>')[1].split('Units')[0])

    data = {
            'complex_name': complexName,
            'address': complexAddress,
            'city': complexCity,
            'state': complexState,
            'zip': complexZip,
            'number_of_units': numberOfUnits,
            'contact_number': contactNumber
            }
    return data

fieldnames = ['complex_name', 'address', 'city', 'state', 'zip', 'number_of_units', 'contact_number']

def createCSV(filename):
    f = open(filename, 'w+', newline='')

    with f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def writeCSV(filename, data):
    f = open(filename, 'a', newline='')

    with f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(data)