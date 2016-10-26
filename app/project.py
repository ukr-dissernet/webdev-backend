# -*- coding: utf-8 -*-
from datetime import datetime
from yandex_translate import YandexTranslate
import re
import os
import io
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

class PlagResult:
    pl = []
    sl = []
    sumC = 0
    data = []

    def __init__(self, pl, sl, sumC, data):
        self.pl = len(pl)
        self.sl = len(sl)
        self.sumC = sumC
        self.data = data

def orpho(line): #избавляемся от остатков украинской орфографии
    d = {'І':'И',
     'і':'и',
     'Ї':'Й',
     'ї':'й',
     'Ґ':'Г',
     'ґ':'г',
     'Є':'Е',
     'є':'е'}
    line = re.sub('ість', 'ость', line)
    line = re.sub('істі', 'ости', line)
    line = re.sub('ськ', 'ск', line)
    line = re.sub('ння', 'ние', line)
    line = re.sub('нню', 'нию', line)
    line = re.sub('ії', 'ии', line)
    line = re.sub('ає', 'ает', line)
    line = re.sub('іє', 'еет', line)
    match = re.search('(І|і|Ї|ї|Ґ|ґ|Є|є)', line)
    if match != None:
        for i in line:
            if i in d:
                line = re.sub(i, d[i], line)
    return line

def stem(word): #нормализация и стэмы
    word = word.lower()
    word = word.strip('[()«»“”„=\'",.—%<>-—„”?!:;*]'.decode("UTF-8"))
    if len(word) > 7:
        stem = word[:-3]
    elif len(word) > 4:
        stem = word[:-2]
    elif len(word) == 4:
        stem = word[:-1]
    else:
        stem = word
    return stem

#Переводим с помощью Yandex Translate Api

#Ключ для АПИ
translate = YandexTranslate('trnsl.1.1.20160301T113042Z.a037e417e6263093.fdf64af693587fc44d952842186c709d55303ea6')

def project(filepath_ukr, filepath_source):
    #Ввести название файла с плагиатом
    file_ukr = io.open(filepath_ukr, 'r', encoding="UTF-8")
    text = file_ukr.read()
    lines = re.split("\\n", text)
    file_ukr.close()
    #Ввести название файла с источником
    s = io.open(filepath_source, 'r', encoding="UTF-8")
    s = s.read()
    slist = s.split()
    sl = []
    for word in slist:
        sl.append(stem(orpho((word))))

    #название файла с переводом
    print('Производится перевод')
    filerus = open(filepath_ukr + '_rus.txt', 'w')
    for line in lines:
        pardict = translate.translate(line, 'uk-ru')
        par = pardict.get('text')
        filerus.write(par[0] + "\n")
    filerus.close()
    print('Перевод завершён')

    #slist, plist - списки слов источника и плагиата
    #sl, pl - кагбэ стэммированные списки слов источника и плагиата

    p = open(filepath_ukr + '_rus.txt', 'r')
    p = p.read()
    plist = p.split()
    pl = []
    for word in plist:
        pl.append(stem(orpho(word)))

    output = [] #массив из номеров слов в начале совпадающих цепочек
    i = 0 #счетчик цикла по плагиату
    j = 0 #счетчик цикла по источнику
    p = 5 #сколько слов должно быть в цепочке, чтобы это считалось плагиатом?
    ii = 0
    jj = 0
    sumC = 0
    while i < len(pl) - p:
        c = 0
        j = 0
        while j < len(sl) - p:
            #print(pl[i] + ' ' + sl[j])
            ch = ''
            ch1 = ''
            match = re.search('^' + pl[i], sl[j])
            if match != None:
                ii = i #больше счетчиков богу счетчиков
                jj = j
                c = 0 #длина цепочки
                while ii < len(pl) and jj < len(sl):
                    match = re.search('^' + pl[ii], sl[jj])
                    if match != None:
                        ch = ch + plist[ii] + ' '
                        ch1 = ch1 + slist[jj] + ' '
                        c += 1
                        jj += 1
                        ii += 1
                    else:
                        break
                if c < p:
                    j += 1
                    continue
                else: #цепочка - плагиат
                    #output.append(str(ii - c) + '\t' + plist[ii-c] + '\t' + str(jj - c) + '\t' + slist[jj-c] + '_' + ch)
                    output.append(str(ii - c) + '\t' + ch + '\t' + str(jj - c) + '\t' + ch1 + '\t' + str(c))
                    sumC += c
                    break
            j += 1
        i = i + c + 1

    print('Длина проверяемого текста: ' + str(len(pl)) + '\nДлина источника: ' + str(len(sl)) + '\nДлина плагиата: ' + str(sumC))
    result = PlagResult(pl, sl, sumC, output)
    return result
