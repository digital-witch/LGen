import AptLeadsScraper as als
import PySimpleGUI as sg
import ProxyScraper as ps

from AptLeadsScraper import Response404, ProxyFileDoesNotExist
from time import sleep

#py -3 -m PyInstaller --noconsole --onefile --hidden-import=PySimpleGui --icon=Lgen4.ico GUI.py

use_proxy = True

def downloadProxy():
    ps.createProxyFile('proxy.log')
    print('Downloading proxy list...')
    proxies = ps.downloadProxyScrapeList()
    numOfProxies = len(proxies)
    print(f'{numOfProxies} proxies found!')
    print(f'Checking proxy list... (This will take approx. {round((numOfProxies // 4.157) // 60)} minutes)')
    checkedProxies = 0
    for proxy in proxies:
        proxy = ps.checkProxy(proxy, 'https://www.apartments.com/')
        if proxy:
            ps.writeProxyFile('proxy.log', proxy)
            checkedProxies += 1
            progress_bar.UpdateBar(round((checkedProxies / numOfProxies) * 100))
    proxies.clear()
    print('Finished!')
    sleep(0.5)
    progress_bar.UpdateBar(0)

statesCodes = ['AL', 'AK', 'AZ', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA',
              'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
              'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
              'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
              'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

sg.theme('LightGrey1')

menu_def = [['&File', ['E&xit']],
            ['&Proxy',
             ['!✓ &Enable Proxy::-proxy_enable-', '&Disable Proxy::-proxy_disable-', '&Download Proxy List']]]
menu = sg.Menu(menu_def, tearoff=True, key='-menu-')

frame_padding = sg.Text('',size=(0,0,),pad=(0,0))
city_label = sg.Text('City:')
city_input_text = sg.InputText(pad=((0,15),(0,0)))
state_label = sg.Text('State:')
state_combo = sg.Combo(statesCodes, default_value='AL', size=(3,5))
results_label = sg.Text('# of Apartments to scrape')
results_spinner = sg.Spin([i for i in range(25,30000)], initial_value=100, size=(10,5))
frame_layout = [
                    [frame_padding],
                    [city_label, city_input_text],
                    [state_label, state_combo, results_spinner, results_label],
                    [frame_padding]
               ]

main_frame = sg.Frame('',frame_layout,pad=((0,0),(5,15)))
padding = sg.Text('',size=(0,0,),pad=(0,0))
output_win = sg.Output(size=(50,4),pad=(15,(0,15)),key=('-output-'))
generate_button = sg.Button('Create CSV', pad=(25,0),bind_return_key=True)
progress_bar = sg.ProgressBar(100, orientation='h', pad=(30,0), size=(20, 15))
layout = [
            [menu],
            [main_frame],
            [output_win],
            [generate_button, progress_bar],
            [padding]
         ]

window = sg.Window('Legion - Lead Generation', layout)
while True:
    event, values = window.read()
    if event == 'Exit':
        break
    elif '-proxy_enable-' in event:
        menu_def = [['&File', ['E&xit']],
                    ['&Proxy',
                     ['!✓ &Enable Proxy::-proxy_enable-', '&Disable Proxy::-proxy_disable-', '&Download Proxy List']]]
        window['-menu-'].update(menu_def)
        use_proxy = True
        print('Proxy Enabled')
    elif '-proxy_disable-' in event:
        menu_def = [['&File', ['E&xit']],
                    ['&Proxy',
                     ['&Enable Proxy::-proxy_enable-', '!✓ &Disable Proxy::-proxy_disable-', '&Download Proxy List']]]
        window['-menu-'].update(menu_def)
        use_proxy = False
        print('Proxy Disabled')
    elif event == 'Download Proxy List':
        window['-output-'].update('')
        downloadProxy()
    elif event == 'Create CSV':
        try:
            window['-output-'].update('')
            city_name = values[0]
            statecode = values[1]
            number_of_results = int(values[2])
            results_retrieved = 0
            if statecode.upper() not in statesCodes:
                raise AttributeError
            if use_proxy:
                apartments = als.scrapeSearch(city_name.replace(' ', '-'), statecode, number_of_results, als.loadProxyFile('proxy.log'))
            else:
                apartments = als.scrapeSearch(city_name.replace(' ', '-'), statecode, number_of_results)

            als.createCSV(f'{city_name}.csv')
            print(f'{city_name}.csv created...')
            print('Preparing to collect results...')
            for apartmentURL in apartments:
                if use_proxy:
                    aptData = als.scrapeApartmentInfo(apartmentURL, als.loadProxyFile('proxy.log'))
                else:
                    aptData = als.scrapeApartmentInfo(apartmentURL)
                als.writeCSV(f'{city_name}.csv', aptData)
                results_retrieved += 1
                progress_bar.UpdateBar(round((results_retrieved/number_of_results)*100))
                window['-output-'].update('')
                if results_retrieved == 1:
                    print(f'{results_retrieved} result retrieved...')
                else:
                    print(f'{results_retrieved} results retrieved...')

            apartments.clear()
        except Response404 as ex:
            print('Error: City/state combo entered does not exist.')
        except ProxyFileDoesNotExist as ex:
            print('Error: Proxy enabled and not downloaded...')
            window.refresh()
            sleep(0.25)
            downloadProxy()
        except ValueError as ex:
            print('Error: "# of Apartments to scrape" must contain an integer.')
        except AttributeError as ex:
            print('Error: "State" must contain a valid two letter state code.','for a list of two letter state codes visit:','https://pe.usps.com/text/pub28/28apb.htm',sep='\n')
        except Exception as ex:
            print(ex)
        else:
            print('Finished!')
            sleep(0.5)
        finally:
            progress_bar.UpdateBar(0)

window.close()