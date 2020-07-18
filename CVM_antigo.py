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
import pdb



pytesseract.pytesseract.tesseract_cmd = r'C:\Users\luiz.cavalcante\AppData\Local\Tesseract-OCR\tesseract.exe'

Fundos={'3GRADAR' : '18324976000185' ,
            'APEX' : '13950080000198' ,
            'ARX' : '04515848000104' ,
            'ADAM' : '23884632000160' ,
            'ALASKA' : '26673556000132' ,
            'ATMOS' : '11188572000162' ,
            'BOGARI' : '15165493000197' ,
            'BRASIL' : '11176045000138' ,
            'BTG' : '12976456000170' ,
            'CLARITAS' : '12219414000195' ,
            'CONST' : '11225860000140' ,
            'CONSTANCIA':'11182064000177', 
            'DAHLIA-LB' : '30317436000170',
            'DAHLIA' : '31635364000171',
            'DYNAMO' : '73232530000139' ,
            'EQUITAS' : '11980010000157' ,
            'FAMA' : '09441424000166' ,
            'HIX' : '28767201000138' ,
            'IBIUNA': '13396819000161',
            'IP' : '04702079000153' ,
            'JGP' : '11228490000102' ,
            'LEBLON' : '10346018000101' ,
            'MSQUARE' : '08927452000125' ,
            'NEO' : '29994412000176',
            'NUCLEO' : '14138786000112' ,
            'OCEANA' : '18454944000102' ,
            'OPPORTUNITY' : '06964937000163' ,
            'PERFIN' : '11695287000138' ,
            'POLLUX' : '16498954000106' ,
            'POLO' : '07914903000127' ,
            'RIOBRAVO' : '06940782000125' ,
            'SPX' : '15350712000108' ,
            'SQUADRA' : '09288254000121' ,
            'SQUADRA-LB' : '09412648000140' ,
            'TEMPO' : '11046362000130',
            'TARPON' : '27389566000103',
            'MASTER':'11225860000140',
            'FIC':'08671980000166',
            'VERSA':'18832847000106',
            'SHARP':'32318881000180',
            'TORK':'31493903000185',
            'KIRON':'28408139000198',
            'VELT':'08927452000125',
            'TRUXT':'26859564000178',
            'VERDE-LB':'16929553000163',}

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
        #print(resposta)
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
                
                #t = 0
                print(opcoes[0][-1],end=' ')
                #if opcoes[0][-1] == '02/2020':
                #    t = 1
                
                if opcoes[-1][-1] == 'Anteriores':
                    opcoes = opcoes[:-1]
                # Testa se o fundo deixou de mandar algum demonstrativo mensal
                if len(opcoes) != (int(opcoes[0][-1].split('/')[0]) - int(opcoes[-1][-1].split('/')[0]) + 1) + 12 * (
                        int(opcoes[0][-1].split('/')[1]) - int(opcoes[-1][-1].split('/')[1])):
                    print('Deixaram de mandar algum demonstrativo mensal')
                out = 'htmls\\' + fundo
                if not os.path.exists(out):
                    os.makedirs(out)
                #if not (os.path.isfile(out + '/' + opcoes[0][-1].split('/')[1] + opcoes[0][-1].split('/')[0] + cnpj + '.html')):
                with open(out + '/' + opcoes[0][-1].split('/')[1] + opcoes[0][-1].split('/')[0] + cnpj + '.html', 'w') as f:
                    f.write(r3.text)


                #return
                ####
                #for n in range(1,min(13,len(opcoes))):
                #for n in range(1,len(opcoes)):
                #for n in [3-t,4-t,5-t]:
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
                    print(opcoes[n][-1],end=' ')
                    r3 = requests.post(url, cookies=cookies_dict, data=params)
                    #if not (
                    #os.path.isfile(out + '/' + opcoes[n][-1].split('/')[1] + opcoes[n][-1].split('/')[0] + cnpj + '.html')):
                    with open(out + '/' + opcoes[n][-1].split('/')[1] + opcoes[n][-1].split('/')[0] + cnpj + '.html',
                              'w') as f:
                        f.write(r3.text)


#salva_carteira(sys.argv[1], sys.argv[2])
#print(sys.argv[1])
#salva_carteira(sys.argv[1].upper(), Fundos[sys.argv[1].upper()])

#output = "C:\\Users\\luiz\\Documents\\output\\"
fundos = [x for x in os.listdir(output) if not '.' in x ]
fundos = ['TORK']
for w in fundos:
    print('\n'+w,end=' ')
    salva_carteira(w.upper(), Fundos[w].upper())