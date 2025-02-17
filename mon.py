import requests
from colorama import init, Fore
import time
import datetime
import os
import math
from requests.exceptions import ConnectionError
from json import JSONDecodeError
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini', encoding="UTF-8-SIG")   
init(autoreset=True)
start_time = time.time()
headers = {"user-agent": "Mozilla/5.0 (Linux; Android 13; Redmi Note 10S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36"}
sellers_array = []
new_elements = []
timestamps = []
selection_array = []
yes = {'yes','y', ''}
no = {'no','n'}
r_r = 1
if not os.path.exists('config.ini'):
    open('config.ini', 'w', encoding="UTF-8-SIG").close()
    print(Fore.YELLOW + 'Файл config.ini не найден, будет создан новый с параметрами по умолчанию.')
    with open("config.ini", "w", encoding="UTF-8-SIG") as f:
        f.write("[Settings]\n# useconf - использовать конфиг? (y/n)\n# interval - интервал записи итогов логов (в минутах)\n# delay - частота обновления данных (в секундах)\n# delete - удалять прошлый лог перед запуском? (y/n)\nuseconf = y\ninterval = 10\ndelay = 5\nuseEmojis = n\ndelete = n\nmincost = y\n\n# startnow - не спрашивать ничего, сразу запускать скрипт по всем имеющимся параметрам (y/N)\n# параметры ниже используются только, если startnow = y\n# trafficType - (1-ГБ, 2-минуты, 3-SMS)\n# volume - кол-во ГБ/минут/SMS\n# mincost - Минималка? (y/n)\n# cost - Цена (используется если, mincost = n)\n[StartNow]\nstartnow = n\ntrafficType = 1\nvolume = 1\nmincost = n\ncost = 15")
    raise SystemExit
if not os.path.exists("stats"):
    os.mkdir("stats")
if not os.path.exists("sales"):
    os.mkdir("sales")
cached_data = None
ending = ""
s, s_b, s_p, b, b_b, b_p, r = 0, 0, 0, 0, 0, 0, 0
s_int, s_b_int, s_p_int, r_int, b_int, b_b_int, b_p_int = 0, 0, 0, 0, 0, 0, 0
k_int = 0
startnow = config.get("StartNow", "startnow")
if startnow in no:
    useconf = config.get("Settings", "useconf")    
    if useconf in yes:
        trafficType = input("Введите цифру типа трафика (1-ГБ, 2-минуты, 3-SMS): ")
        traffic_types = {"1": "data", "2": "voice", "3": "sms"}
        trafficType = traffic_types.get(trafficType, trafficType)
        volume = int(input('Введите кол-во ГБ/минут/SMS: '))
        mincost = config.get("Settings", "mincost")
        interval = config.getint("Settings", "interval")
        useEmojis = config.get("Settings", "useEmojis")
        delay = config.getint("Settings", "delay")
        delete = config.get("Settings", "delete")
        interval *= 60
    else:
        writeconf = input("Запомнить настройки? (Y/n): ")
        trafficType = input("Введите цифру типа трафика (1-ГБ, 2-минуты, 3-SMS): ")
        traffic_types = {"1": "data", "2": "voice", "3": "sms"}
        trafficType = traffic_types.get(trafficType)
        volume = int(input('Введите кол-во ГБ/минут: '))
        interval = int(input('За какой интервал собирать статистику (в минутах): ')) * 60
        delay = int(input('Введите частоту обновления (в секундах): '))
        delete = input('Обнулить лог-файл? (Y/n): ').lower()
        mincost = input("Минималка? (Y/n): ").lower()
        if writeconf in yes:
            config.set("Settings", "interval", str(round(interval/60)))
            config.set("Settings", "delay", str(delay))
            config.set("Settings", "delete", delete)
            with open('config.ini', 'w', encoding="UTF-8-SIG") as config_file:
                config.write(config_file)
    if 10 < interval / 60 % 100 < 20:
        ending = ""
    elif interval / 60 % 10 == 1:
        ending = "у"
    elif interval / 60 % 10 in [2, 3, 4]:
        ending = "ы"
    else:
        ending = ""
    if trafficType == "voice":
        if volume % 10 == 1:
            voice_ending = "а"
        elif volume % 10 in [2, 3, 4]:
            voice_ending = "ы"
        else:
            voice_ending = ""
    if mincost in yes:
        if trafficType == "data":
            cost = volume * 15
        elif trafficType == "voice":
            cost = math.ceil(volume / 1.25)
        elif trafficType == "sms":
            cost = math.ceil(volume / 2)
    elif mincost in no:
            cost = int(input("Введите цену лота: "))
    if trafficType == "data":
        trafficTypeVisual = " ГБ"
    elif trafficType == "voice":
        trafficTypeVisual = " минут" + voice_ending
    else:
        trafficTypeVisual = " SMS"
else:
    interval = config.getint("StartNow", "interval")
    delay = config.getint("StartNow", "delay")
    delete = config.get("StartNow", "delete")
    interval *= 60
    trafficType = config.get("StartNow", "trafficType")
    traffic_types = {"1": "data", "2": "voice", "3": "sms"}
    trafficType = traffic_types.get(trafficType, trafficType)
    volume = config.getint("StartNow", "volume")
    mincost = config.get("StartNow", "mincost")
    if mincost in yes:
        if trafficType == "data":
            cost = volume * 15
        elif trafficType == "voice":
            cost = math.ceil(volume / 1.25)
        elif trafficType == "sms":
            cost = math.ceil(volume / 2)
    elif mincost in no:
            cost = int(input("Введите цену лота: "))
    if trafficType == "data":
        trafficTypeVisual = " ГБ"
    elif trafficType == "voice":
        trafficTypeVisual = "минут" + voice_ending
    else:
        trafficTypeVisual = " SMS"
    
while True:    
    
    trafficTypeFile = "gb" if trafficType == "data" else "min" if trafficType == "voice" else "sms"
    if delete in yes:
        os.chdir("sales")
        open(f"sales_{volume}{trafficTypeFile}_{cost}p.csv", "w", encoding="UTF-8-SIG").close()
        os.chdir("..")
        break
    elif delete in no:
        break

try:
    response = requests.get(f"https://t2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=5000", headers=headers, timeout=5)
    data = response.json()
except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
    print(Fore.YELLOW + 'Потеряно соединение с сервером, 3')
    time.sleep(5)

for item in reversed(data["data"]):
    seller = item.get("seller")
    name = seller.get("name")
    emojis = seller.get("emojis")
    id = item.get("id")
    my = item.get("my")
    seller_list = ["Аноним", emojis, str(id), str(my)] if ((name is None) or (name == "Анонимный продавец")) else [name, emojis, str(id), str(my)]
    sellers_array.insert(0, seller_list)
    timestamps.insert(0, time.time())

def check(id):
    global cached_data
    if not cached_data:
        try:
            response = requests.get(f"https://t2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&limit=500", headers=headers, timeout=5)
            cached_data = response.json()
        except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
            print(Fore.YELLOW + 'Потеряно соединение с сервером, 4')
            time.sleep(5)
    try:
        for item in cached_data["data"]:
            id_check = item.get("id")
            cost_change = item.get("cost").get("amount")
            if id_check == id:
                return True, cost_change
    except Exception as e:
        print(Fore.YELLOW + f'Ошибка обработки данных: {e}')
    return False, None

while True:
    if s == 0 and r == 0:
        k = round(((b_p/(s+r+1))*100), 1)
    else:
        k = round(((b_p/(s+r))*100), 1)
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > interval:
        os.chdir("stats")
        with open(f"stats_{volume}{trafficTypeFile}_{cost}p.txt", "a", encoding="UTF-8-SIG") as f:
            f.write('\nВремя на момент записи: {}'.format(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + f'\nСтатистика за {round(interval / 60)} минут{ending}:\n')
            f.write('Выставлено лотов: ' + str(s - s_int) + '\n – Ботами: ' + str(s_b - s_b_int) + '\n – Продавцами: ' + str(s_p - s_p_int))
            f.write('\nКуплено лотов: ' + str(b - b_int) + '\n – Ботов: ' + str(b_b - b_b_int) + '\n – Продавцов: ' + str(b_p - b_p_int) + '\nРакет: ' + str(r - r_int) + "\nКоэффициент: " + str(round(k - k_int, 1)) + "\n" + '-------------------------------------------------------')
        start_time += interval
        s_int, s_b_int, s_p_int, r_int = s, s_b, s_p, r
        b_int, b_b_int, b_p_int = b, b_b, b_p
        k_int = k
        os.chdir("..")
        
    os.system('cls' if os.name == 'nt' else 'clear')
   
    print(Fore.WHITE + f"{volume}{trafficTypeVisual} " + f"за {str(cost).replace('.0', '')} ₽")
    print(Fore.YELLOW + 'Выставлено лотов: ' + str(s) + '. Ботами: ' + str(s_b) + '. Продавцами: ' + str(s_p))
    print(Fore.GREEN + 'Куплено лотов: ' + str(b) + '. Ботов: ' + str(b_b) + '. Продавцов: ' + str(b_p))
    print(Fore.CYAN + 'Ракет: ' + str(r) + ". Коэффициент: " + str(k))
    print('--------------------------------------------------------')
    counter = 0
    try:
        for item in data["data"][:20]:
            seller = item.get("seller")
            name = seller.get("name")
            emojis = seller.get("emojis")
            trafficType = item.get("trafficType")
            my = item.get("my")
            if useEmojis in yes:
                emoji_dict = {"devil": "\U0001F608", "cool": "\U0001F60E", "cat": "\U0001F431", "zipped": "\U0001F910", "scream": "\U0001F631", "rich": "\U0001F911", "tongue": "\U0001F61B", "bomb": "\U0001F4A3", "": "  "}
                for i in range(len(emojis)):
                    try:
                        emojis[i] = emoji_dict[emojis[i]]
                    except KeyError:
                        emojis[i] = "  "
            else:
                emoji_dict = {"devil": "демон ", "cool": "крутой", "cat": "кот   ", "zipped": "молчит", "scream": "ужас  ", "rich": "деньги", "tongue": "язык  ", "bomb": "бомба ", "": "      "}
                for i in range(len(emojis)):
                    try:
                        emojis[i] = emoji_dict[emojis[i]]
                    except KeyError:
                        emojis[i] = "      "

            name = "Аноним" if name is None or name == "Анонимный продавец" else name
            if my is False:
                name = Fore.GREEN + str(name)
                emojis = Fore.GREEN + " ".join(emojis)
            else:
                name = Fore.RED + str(name)
                emojis = Fore.RED + " ".join(emojis)

            counter += 1
            if counter <= 9:
                print(str(counter) + '.  ' + f"{Fore.WHITE}{name:<17}{emojis}")
            elif counter > 9:
                print(str(counter) + '. ' + f"{Fore.WHITE}{name:<17}{emojis}")
    except KeyError:
        print(Fore.YELLOW + "Ошибка обработки данных, 5")
        time.sleep(5)
    print('--------------------------------------------------------')
   
    try:
        response = requests.get(f"https://t2.ru/api/exchange/lots?trafficType={trafficType}&volume={volume}&cost={cost}&limit=300", headers=headers, timeout=5)
        data = response.json()
    except (JSONDecodeError, ConnectionError, requests.exceptions.ReadTimeout):
        print(Fore.YELLOW + 'Потеряно соединение с сервером, 6')
        time.sleep(5)
    new_elements = []
    selection_array = []
    for item in reversed(data["data"]):
        seller = item.get("seller")
        name = seller.get("name")
        emojis = seller.get("emojis")
        id = item.get("id")
        my = item.get("my")
        seller_list = ["Аноним", emojis, str(id), str(my)] if (name is None) or (name == "Анонимный продавец") else [name, emojis, str(id), str(my)]
        selection_array.insert(0, seller_list)
        if seller_list[-2] not in [element[-2] for element in sellers_array]:
            new_elements.insert(0, seller_list)
            s += 1
            sellers_array.insert(0, seller_list)
            timestamps.insert(0, time.time())
            value = seller_list[-1]
            if value == 'True':
                s_b += 1
            elif value == 'False':
                s_p += 1
        else:
            for i, element in enumerate(sellers_array):
                if element[-2] == seller_list[-2] and element[0] != seller_list[0]:                    
                    sellers_array[i] = seller_list
                    break
    if len(new_elements) > 0:
        for element in new_elements:
            if element[-1] == 'True':
                if useEmojis in yes:
                    print('\U00002795 ' + Fore.RED + str(element[0]))
                else:
                    print("+ " + Fore.RED + str(element[0]))
            else:
                if useEmojis in yes:
                    print('\U00002795 ' + Fore.GREEN + str(element[0]))
                else:
                    print("+ " + Fore.GREEN + str(element[0]))
    os.chdir("sales")
    with open(f"sales_{volume}{trafficTypeFile}_{cost}p.csv", "a", encoding="UTF-8-SIG") as f:
        if os.path.getsize(f"sales_{volume}{trafficTypeFile}_{cost}p.csv") == 0:
            f.write("Имя,Тип,Время покупки\n")
        for element in sellers_array[:20]:
            id = element[-2]
            if id not in [element[-2] for element in selection_array]:
                pos = sellers_array.index(element) - len(new_elements) + 1
                timestamp_index = [element[-2] for element in sellers_array].index(id)
                timestamp = timestamps[timestamp_index]
                if (element[-1] == 'True' and 0 <= time.time() - timestamp <= 3600):
                    if useEmojis in yes:
                        print("\U0001F4B8 " + Fore.RED + str(element[0]) + ", позиция: " + str(pos))
                    else:
                        print("$ " + Fore.RED + str(element[0]) + ", позиция: " + str(pos))
                    f.write(str(element[0]) + ',Бот,{}'.format(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
                    b_b += 1; b += 1
                elif (element[-1] == 'True' and time.time() - timestamp > 3600):
                    print('Лот сгорел. Позиция: ' + str(pos))
                    print(Fore.RED + str(element[0]) + ' ' + str(element[1]))
                elif element[-1] == 'False':
                    result, cost_change = check(id)
                    if not result:
                        if useEmojis in yes:
                            print("\U0001F4B8 " + Fore.GREEN + str(element[0]) + ", позиция: " + str(pos))
                        else:
                            print("$ " + Fore.GREEN + str(element[0]) + ", позиция: " + str(pos))
                        f.write(str(element[0]) + ',Продавец,{}'.format(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
                        b_p += 1; b += 1                
                    else:
                        if useEmojis in yes:
                            print("\U0001F501 " + Fore.GREEN + str(element[0]) + ' - изменил(а) цену на ' + str(int(cost_change)) + " ₽")
                        else:
                            print(Fore.GREEN + str(element[0]) + ' - изменил(а) цену на ' + str(int(cost_change)) + " ₽")
    
                sellers_array.remove(element)
                timestamps.pop(timestamp_index)
                r_r += 1
    os.chdir("..")
    for element in selection_array[:20]:
        if element in sellers_array and sellers_array.index(element) - selection_array.index(element) > r_r:
            r += 1
            old_index = sellers_array.index(element)
            new_index = selection_array.index(element)
            sellers_array.remove(element)
            sellers_array.insert(new_index, element)
            value_to_move = timestamps.pop(old_index)
            timestamps.insert(new_index, value_to_move)
            if element[-1] == 'False':
                seller_id = element[2]
                if useEmojis in yes:
                    print('\U0001F680 ' + Fore.GREEN + str(element[0]) + ', ' + str(old_index + 1 - len(new_elements)) + ' --> ' + str(new_index + 1))
                else:
                    print("∆ " + Fore.GREEN + str(element[0]) + ', ' + str(old_index + 1 - len(new_elements)) + ' --> ' + str(new_index + 1))
    sellers_array = sellers_array[:30000]
    timestamps = timestamps[:30000]
    cached_data = None
    r_r = 1
    time.sleep(delay)
