import discord
import sqlite3
from random import choice
import requests
from bs4 import BeautifulSoup


city = None
TOKEN = "ODMwMDk0MjkyMTQ3MzcyMDcy.YHBrjQ.cZqX_r3aTPtwzG2wWbuHJH-abGY"
client = discord.Client()
used = []
game_start = False
init1 = False
number_of_players = 0
players = []
index_of_player = 0
current_number_of_players = 0
wrongs = 0
begin = True
new_player = False
max_wrongs = 3
wrongs_init = False
history = []  # Определение глобальных переменных


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'{client.user.id} сыграет с вами в города!')


@client.event
async def on_message(message):
    global city, used, game_start, init1, number_of_players, index_of_player, current_number_of_players, players,\
        wrongs, new_player, max_wrongs, wrongs_init
    try:
        if len(players) > len(players):
            index_of_player = index_of_player % len(players)
        if message.author == client.user:
            return
        elif '!покажи историю' in message.content.lower():
            if len(history) == 0:
                await message.channel.send('Она пустая')  # Случай, когда история пустая
            for i in history:
                await message.channel.send(i)  # Показывает историю
        elif '!очисти историю' in message.content.lower():
            history.clear()  # Список с историей очищается
        elif '!перезапуск' in message.content.lower():  # Перезапуск
            history.clear()
            index_of_player = 0
            used.clear()
            city = None
            wrongs = 0
            await message.channel.send('Начинает ' + players[0])
        elif '!количество ошибок' in message.content.lower() and not game_start and not init1:
            wrongs_init = True  # Флаг, отвечающий за ввод кол-ва ошибок
            await message.channel.send('Введите максимальное количество ошибок.')
        elif wrongs_init:
            n = message.content.lower()
            if n in [str(i) for i in range(1, 200)]:
                wrongs_init = False
                max_wrongs = int(n)
            else:
                await message.channel.send('Введите число от 1 до 200.')
        elif new_player and 'я' in message.content.lower():
            if message.author.name not in players:
                players.append(message.author.name)
                game_start = True
                await message.channel.send('Ходит ' + players[index_of_player] + ': ')
                new_player = False
            else:
                await message.channel.send('Вы уже записаны')
        elif new_player and 'не надо' in message.content.lower():
            game_start = True
            await message.channel.send('Ходит ' + players[index_of_player] + ': ')
            new_player = False
        elif '!добавить игрока' in message.content.lower():  # Добавление игрока
            new_player = True
            game_start = False
            await message.channel.send('Напишите <я>, чтобы записаться')  # Удаление игрока
        elif '!я ухожу' in message.content.lower():
            if message.author.name in players:
                players.remove(message.author.name)
                await message.channel.send(message.author.name + ' выбывает')
                if len(players) == 0:
                    history.clear()  # Очищение истории
                    game_start = False  # Конец игры
                    used = []
                    players = []
                    await message.channel.send('Я выиграл.')
                else:
                    await message.channel.send('Ходит ' + players[index_of_player] + ': ')
            else:
                await message.channel.send('Вы не играете')
        elif '!покажи использованные города' in message.content.lower():
            for i in used:
                await message.channel.send(i)  # Показывает использованные города
        elif '!как дела' in message.content.lower():
            await message.channel.send('Хорошо. Спасибо, что поинтересовались.')  # Ответ на вопрос <Как дела>
        elif '!help' in message.content.lower() or '!привет бот' in message.content.lower():
            if 'привет' in message.content.lower():
                await message.channel.send('Привет! Чтобы поиграть, используй команды:')
            await message.channel.send('Введите <!Правила>, чтобы узнать правила игры.\n'
                                       'Введите <!Сыграем>, чтобы начать игру в города.\n'
                                       'Введите <!Закончим>, чтобы закончить игру\n'
                                       'Введите <!Расскажи о городе>, чтобы посмотреть информацию о городе.\n'
                                       'Введите <!Покажи историю>, чтобы посмотреть историю игры.\n'
                                       'Введите <!Очисти историю>, чтобы очистить историю игры.\n'
                                       'Введите <!Покажи использованные города>, чтобы показать использованные.'
                                       ' города\n'
                                       'Введите <!Перезапуск>, чтобы перезапустить игру.\n'
                                       'Введите <!Добавить игрока>, чтобы добавить.'
                                       ' игрока в уже идущую игру\n'
                                       'Введите <!Я ухожу>, чтобы выйти из игры.\n'
                                       'Введите <!Количество ошибок>, чтобы установить максимальное кол-во ошибок\n'
                                       )  # Список команд
        elif '!правила' in message.content.lower():
            await message.channel.send('Игроки называют города по цепочке. Каждый последующий игрок называет город,'
                                       ' начинающийся с той же буквы, '
                                       'на какую закончился город озвученный предыдущим игроком.'
                                       ' Игрок ошибающийся три раза(по умолчанию) подряд, проигрывает.'
                                       ' Используются города России.'
                                       ' Вводится их официальное название.')  # Список правил
        elif '!сыграем' in message.content.lower() and not game_start:
            await message.channel.send('Давайте сыграем в города!'
                                       ' Введите количество игроков.')  # Начало создания команды
            city = None
            init1 = True  # Запись игроков начинается
        elif init1 and number_of_players == 0:
            number_of_players = message.content.lower()  # Вводится количество людей
            if number_of_players in [str(i) for i in range(1, 200)]:
                number_of_players = int(number_of_players)
                current_number_of_players = 0
                await message.channel.send('Напишите <я>, чтобы записаться')
            else:
                number_of_players = 0
                await message.channel.send('Введите число от 1 до 200.')
        elif number_of_players > 0 and message.content.lower() == 'я':
            if message.author.name not in players:
                players.append(message.author.name)  # Запись игрока в список
                current_number_of_players += 1
                if current_number_of_players == number_of_players:  # Количество записавшихся равно кол-ву игроков всего
                    number_of_players = 0
                    index_of_player = 0
                    current_number_of_players = 0
                    await message.channel.send('Начинает ' + players[0])
                    init1 = False
                    game_start = True
            else:
                await message.channel.send('Вы уже записаны')  # В случае повторного написания <я> одним человеком
        elif game_start and message.content.lower() == '!расскажи о городе':  # Пишется информация о городе
            a = used[-1]
            r = requests.get("https://www.google.ru/search?tbm=isch&q=карта города {}".format(a))
            text = r.text
            soup = BeautifulSoup(text, "html.parser")
            await message.channel.send('Карта города ' + a + ':')
            await message.channel.send(soup.find_all('img')[2].get('src'))
            geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=" \
                               "40d1649f-0493-4b70-98ba-98533de7710b&geocode" \
                               "={}&format=json".format(a)
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()  # Собираем информацию о городе
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                await message.channel.send('Федеральный округ: ' + toponym["metaDataProperty"][
                    "GeocoderMetaData"]['Address']['Components'][1]['name'])
                await message.channel.send(
                    'Область: ' + toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['Components'][2]['name'])
                await message.channel.send(
                    'Координаты: ' + toponym["Point"]["pos"])
            else:
                await message.channel.send('Ошибка')
        elif '!закончим' in message.content.lower() and (game_start or init1 or new_player):
            await message.channel.send('Я выиграл.')
            history.clear()  # Очищение истории
            game_start = False  # Конец игры
            init1 = False
            new_player = False
            used = []
            players = []
            wrongs = 0
        elif game_start and message.author.name in players and message.author.name != players[index_of_player]:
            await message.channel.send('Дождитесь своей очереди.')
        elif game_start and message.author.name == players[index_of_player]:  # Человек вводит город
            con = sqlite3.connect('data.sqlite')
            cur = con.cursor()
            a = """SELECT city FROM 'goroda_Список городов в России' WHERE city == '{}'""".format(message.content)
            result = cur.execute(a).fetchall()  # Поиск города в базе данных
            con.close()
            if len(result) == 0:
                await message.channel.send('Данный город не найден в базе данных. Используйте другой')
                history.append(players[index_of_player] + ': ' + message.content + ' (Ошибка)')
                wrongs += 1
                if wrongs == max_wrongs:  # Вылет игрока при трех ошибках
                    if len(players) == 1:
                        await message.channel.send(players[index_of_player] + ' проиграл. Я выиграл')
                        history.clear()
                        used = []
                        players = []
                        game_start = False
                    else:
                        await message.channel.send(players[index_of_player] + ' выбыл')
                        players.remove(players[index_of_player])
                        wrongs = 0
                        index_of_player = index_of_player % len(players)
                        await message.channel.send('Ходит ' + players[index_of_player])
            else:
                wrongs = 0
                if (message.content.lower()[0] == city or city is None) and message.content not in used:
                    index_of_player += 1
                    r = requests.get("https://www.google.ru/search?tbm=isch&q=герб города {}".format(
                        message.content.lower()))
                    text = r.text
                    soup = BeautifulSoup(text, "html.parser")
                    used.append(message.content)
                    history.append(players[index_of_player - 1] + ': ' + message.content)
                    await message.channel.send('Герб города ' + message.content.capitalize() + ':')
                    await message.channel.send(soup.find_all('img')[1].get('src'))  # Выводится фото герба
                    if index_of_player == len(players):
                        await message.channel.send('Мой ход')
                        index_of_player = 0
                        con = sqlite3.connect('data.sqlite')
                        cur = con.cursor()
                        a = """SELECT city FROM 'goroda_Список городов в России'
                         WHERE city LIKE '{}%'""".format(message.content.rstrip('цыьъй').strip('цыъьй').upper()[-1])
                        result = cur.execute(a).fetchall()
                        while True:  # Поиск города ботом
                            result2 = choice(result)[0]
                            if result2 not in used:
                                used.append(result2)
                                break
                        con.close()
                        await message.channel.send(result2)
                        history.append('Я: ' + result2)
                        r = requests.get("https://www.google.ru/search?tbm=isch&q=герб города {}".format(result2))
                        text = r.text
                        soup = BeautifulSoup(text, "html.parser")
                        city = result2.rstrip('цыьъй').strip('цыъьй')[-1]
                        await message.channel.send(soup.find_all('img')[1].get('src'))
                        flag = None
                        for i in range(1, len(result2.rstrip('цыьъй').strip('цыъьй')) + 1):
                            con = sqlite3.connect('data.sqlite')
                            cur = con.cursor()
                            a = """SELECT city FROM 'goroda_Список городов в России'
                                                 WHERE city LIKE '{}%'""".format(
                                message.content.rstrip('цыьъй').strip('цыъьй').upper()[-i])
                            result = cur.execute(a).fetchall()
                            con.close()
                            if len(result) > 0:
                                city = result2.rstrip('цыьъй').strip('цыъьй')[-i]
                                flag = True
                                break
                        if flag is None:  # Случай, когда все буквы города не могут быть использованы
                            game_start = False
                            await message.channel.send('Закончим. Дальнейшая игра невозможна.')
                            history.clear()
                        else:
                            await message.channel.send('Вам на ' + city + '. Ходит '
                                                       + players[index_of_player] + ':')
                    else:
                        flag = None
                        for i in range(1, len(message.content.rstrip('цыьъй').strip('цыъьй')) + 1):
                            con = sqlite3.connect('data.sqlite')
                            cur = con.cursor()
                            a = """SELECT city FROM 'goroda_Список городов в России'
                                                 WHERE city LIKE '{}%'""".format(
                                message.content.rstrip('цыьъй').strip('цыъьй').upper()[-i])
                            result = cur.execute(a).fetchall()
                            if len(result) > 0:
                                flag = True
                                city = message.content.rstrip('цыьъй').strip('цыъьй')[-i]
                                break
                            con.close()
                        if flag is None:  # Случай, когда все буквы города не могут быть использованы
                            game_start = False
                            history.clear()
                            await message.channel.send('Закончим. Дальнейшая игра невозможна.')
                        else:
                            await message.channel.send('Ходит ' + players[index_of_player])
                elif message.content in used:  # Повторение города
                    await message.channel.send('Этот город уже был')
                    history.append(players[index_of_player] + ': ' + message.content + ' (Ошибка)')
                    wrongs += 1
                    if wrongs == max_wrongs:
                        if len(players) == 1:
                            await message.channel.send(players[index_of_player] + ' проиграл. Я выиграл')
                            history.clear()
                            used = []
                            players = []
                            game_start = False
                        else:
                            await message.channel.send(players[index_of_player] + ' выбыл')
                            players.remove(players[index_of_player])
                            wrongs = 0
                            index_of_player = index_of_player % len(players)
                            await message.channel.send('Ходит ' + players[index_of_player])
                else:
                    history.append(players[index_of_player] + ': ' + message.content + ' (Ошибка)')
                    await message.channel.send('Этот город на ' + message.content.lower()[0].upper()
                                               + ', а должен быть на '
                                               + city.upper())
                    wrongs += 1
                    if wrongs == max_wrongs:  # Вылет игрока в случае трех ошибок
                        if len(players) == 1:
                            await message.channel.send(players[index_of_player] + ' проиграл. Я выиграл')
                            history.clear()
                            used = []
                            players = []
                            game_start = False
                        else:
                            await message.channel.send(players[index_of_player] + ' выбыл')
                            players.remove(players[index_of_player])
                            wrongs = 0
                            index_of_player = index_of_player % len(players)
                            await message.channel.send('Ходит ' + players[index_of_player])
        elif message.content.lower()[0] == '!':
            await message.channel.send('Не понял команду.')
    except Exception:
        await message.channel.send('Ошибка.')


client.run(TOKEN)
