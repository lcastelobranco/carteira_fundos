import requests
import re
import cv2
from PIL import Image
from io import BytesIO
import time
import numpy as np
import pytesseract
import os
import sys
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


import socket
import socks


def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1",9050,True, 'socks5_user','socks_pass')
    socket.socket = socks.socksocket
    print("\n Connected to Tor")

def newidentity():
    socks.setdefaultproxy()
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("127.0.0.1",9051))
    s.send("AUTHENTICATE\r\n")
    response = s.recv(128)
    if response.startswith("250"):
        s.send("SIGNAL NEWNYM\r\n")
        s.close()
        connectTor()

from math import sqrt


def possiveis_precos(num):
    num = abs(int(num))
    lista = []
    p = []

    for i in range(1, int(sqrt(num)) + 1):
        if (num % i == 0):
            z = str(i / float(100))
            z2 = str(num / float(100 * i))
            if z[-2] == '.':
                z = z + '0'
            if z2[-2] == '.':
                z2 = z2 + '0'
            lista.append(z)
            lista.append(z2)

    lista = sorted(list(set(lista)))

    return lista


def mudancas_morfologicas(imagem,x=3,tipo='erode'):


    im_gray = np.array(imagem)
    kernel = np.ones((x, x), np.uint8)
    if tipo == 'erode' or tipo == 'dilate':
        im_gray = cv2.erode(im_gray, kernel, iterations=1)
        im_gray = cv2.dilate(im_gray, kernel, iterations=1)
    if tipo == 'open' or tipo == 'close':
        im_gray = cv2.morphologyEx(im_gray, cv2.MORPH_OPEN, kernel)
        im_gray = cv2.morphologyEx(im_gray, cv2.MORPH_CLOSE, kernel)
    resposta = pytesseract.image_to_string(im_gray).replace(' ', '').replace('.', '').replace(',', '').replace('-', '')
    if not resposta:
        if x == 5:
            return 'erro'
        elif x == 3:
            mudancas_morfologicas(imagem, x=2, tipo='erode')
        elif x == 2:
            mudancas_morfologicas(imagem, x=4, tipo='erode')
        elif x == 4:
            mudancas_morfologicas(imagem, x=1, tipo='erode')
        else:
            mudancas_morfologicas(imagem, x=5, tipo='erode')
    else:
        return resposta


def captcha():
    url = "http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/FormBuscaPartic.aspx?CD_ERRO=4&TpConsulta=5"

    r1 = requests.get(url)
    cookies_dict = r1.cookies.get_dict()
    __VIEWSTATE = re.findall('name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />\r\n\r\n<input', r1.text)[0]
    __EVENTVALIDATION = re.findall('name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)"', r1.text)[0]
    __VIEWSTATEGENERATOR = re.findall('id="__VIEWSTATEGENERATOR" value="(.*?)"', r1.text)[0]
    v1 = re.findall(r"<img src=\'RandomTxt.aspx(.*?)\'><br>", r1.text)[0]
    r2 = requests.get("http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/RandomTxt.aspx" + v1, cookies=cookies_dict)
    imagem = Image.open(BytesIO(r2.content))
    return imagem, cookies_dict,__VIEWSTATE,__EVENTVALIDATION,__VIEWSTATEGENERATOR,mudancas_morfologicas(imagem)



def salva_carteira(fundo, cnpj):
    url = "http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/FormBuscaPartic.aspx?CD_ERRO=4&TpConsulta=5"
    imagem, cookies_dict,__VIEWSTATE,__EVENTVALIDATION,__VIEWSTATEGENERATOR,resposta = captcha()
    if not resposta:
        salva_carteira(fundo, cnpj)
    else:
        print(resposta)
        url =  "https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/ResultBuscaPartic.aspx?TpConsulta=5&CNPJNome="+str(cnpj)+"&COMPTC=&numRandom="+resposta
        params = {'__EVENTTARGET': '',
              '__EVENTARGUMENT': '',
              '__VIEWSTATE': __VIEWSTATE,
              '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR,
              '__EVENTVALIDATION': __EVENTVALIDATION,
              'txtCNPJNome': str(cnpj),
              'ddComptc': '',
              'numRandom': resposta,
              'btnContinuar': 'Continuar >'
              }
        r3 = requests.post(url, cookies=cookies_dict, data=params)



        CNPJ = re.findall(r'<span id="lbNrPfPj">(.* ?)</span>', r3.text)
        if not CNPJ:
            salva_carteira(fundo, cnpj)
        else:

            url = re.findall(r'PK_PARTIC=(.*?)&amp;COMPTC=', r3.text)[0]
            url = 'https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CDA/CPublicaCDA.aspx?PK_PARTIC=' + url + '&COMPTC='
            if CNPJ[0].replace('.','').replace('-','').replace('/','') != cnpj:
                print(cnpj,' Deu erro no CNPJ que voltou ',CNPJ[0].replace('.','').replace('-','').replace('/',''))
                #print('Deu erro no CNPJ que voltou')
            else:
                opcoes = re.findall(r'<option(.*?)value="(.*?)">(.*?)</option>', r3.text)
                if opcoes[-1][-1] == 'Anteriores':
                    opcoes = opcoes[:-1]
                # Testa se o fundo deixou de mandar algum demonstrativo mensal
                if len(opcoes) != (int(opcoes[0][-1].split('/')[0]) - int(opcoes[-1][-1].split('/')[0]) + 1) + 12 * (
                        int(opcoes[0][-1].split('/')[1]) - int(opcoes[-1][-1].split('/')[1])):
                    print('Deixaram de mandar algum demonstrativo mensal')
                out = 'C:\\Users\luiz\\Documents\\output\\' + fundo+"\\htmls"
                if not os.path.exists(out):
                    os.makedirs(out)
                if not (os.path.isfile(out + '/' + opcoes[0][-1].split('/')[1] + opcoes[0][-1].split('/')[0] + cnpj + '.html')):
                    with open(out + '/' + opcoes[0][-1].split('/')[1] + opcoes[0][-1].split('/')[0] + cnpj + '.html', 'w') as f:
                        f.write(r3.text)


                #return
                ####
                #for n in range(1,13):
                #for n in range(1,len(opcoes)):
                for n in [3]:

                    __VIEWSTATE = re.findall('name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />\r\n\r\n<input', r3.text)[0]
                    __EVENTVALIDATION = re.findall('name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)"', r3.text)[0]
                    __VIEWSTATEGENERATOR = re.findall('id="__VIEWSTATEGENERATOR" value="(.*?)"', r3.text)[0]

                    time.sleep(3)
                    params = {
                                '__EVENTTARGET': 'ddCOMPTC',
                                '__EVENTARGUMENT': '',
                                '__LASTFOCUS': '',
                                '__VIEWSTATE': __VIEWSTATE,
                                '__VIEWSTATEGENERATOR' : __VIEWSTATEGENERATOR,
                                '__EVENTVALIDATION': __EVENTVALIDATION,
                                'ddCOMPTC': opcoes[n][1]
                    }
                    r3 = requests.post(url, cookies=cookies_dict, data=params)
                    if not (
                    os.path.isfile(out + '/' + opcoes[n][-1].split('/')[1] + opcoes[n][-1].split('/')[0] + cnpj + '.html')):
                        with open(out + '/' + opcoes[n][-1].split('/')[1] + opcoes[n][-1].split('/')[0] + cnpj + '.html',
                                  'w') as f:
                            f.write(r3.text)

#connectTor()
#newidentity()
#print(sys.argv[1], sys.argv[2])
#salva_carteira(sys.argv[1], sys.argv[2])
salva_carteira('CONSTANCIA', '11.182.064/0001-77'.replace('-','').replace('.','').replace('/',''))
