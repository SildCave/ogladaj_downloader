import requests
import bs4
import json
import os
import time
from urllib.parse import unquote
import threading
import PySimpleGUI as psg

MAX_THREADS = 10

l1 = psg.Text('Oglądaj url', key='-OUT-', font=('Arial Bold', 20), expand_x=True, justification='center')
t1 = psg.Input('', enable_events=True, key='-INPUT-', font=('Arial Bold', 20), expand_x=True, justification='left')
b1 = psg.Button('Ok', key='-OK-', font=('Arial Bold', 20))
b2 = psg.Button('Exit', font=('Arial Bold', 20))
layout = [[l1], [t1], [b1, b2]]
window = psg.Window('Oglądaj downloader', layout, size=(750, 150))

while True:
    event, values = window.read()
    if event == psg.WIN_CLOSED or event == 'Exit':
        break
    elif event == '-OK-':
        url = values['-INPUT-']
        break
window.close()
url = url.strip()
if url[-1] != '/':
    url += '/'
dir_name = url.split('/')[-2]

r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = bs4.BeautifulSoup(r.text, 'html.parser')
lis = soup.find_all('li')
odcinki = lis[-1].attrs['value']
odcinki = int(odcinki)

threads = []

#get python script path
dir_name = os.path.dirname(os.path.realpath(__file__)) + '/' + dir_name

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

if not os.path.exists((os.path.realpath(__file__)) + '/' + 'Cookie.txt'):
    print('Cookie.txt not found')
    exit()

with open(os.path.dirname(os.path.realpath(__file__)) + '/' + 'Cookie.txt', 'r') as f:
    cookie = f.read()

for i in range(1, odcinki + 1):
    r = requests.get(url + str(i), headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    button = soup.select('#changePlayerButton')
    id = button[0].attrs['value']

    r = requests.post('https://ogladajanime.pl/command_manager.php?action=get_player_list', data={'id': id}, headers={
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
        'Referer': url + str(i),
        'Cookie': cookie
    })

    j = json.loads(((r.json()['data'])))
    
    video_url = f"https://www.cda.pl/video/{(unquote(j['url']).split('/')[-1])}"
    print(video_url)

    while threading.active_count() >= MAX_THREADS:
        time.sleep(1)
        pass


    t = threading.Thread(target=os.system, args=(f"yt-dlp -o \"{dir_name}/Ep {str(i).zfill(3)}.%(ext)s\" {video_url}",)).start()
    threads.append(t)
    time.sleep(6)


for thread in threads:
    try:
        thread.join()
    except:
        pass
    
print('Done')



