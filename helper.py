import pandas as pd
#pd.set_option('precision', 2)
#pd.set_option('max_rows', 10)

import requests
import re
import cv2
from PIL import Image
from io import BytesIO
import time
import numpy as np
import pytesseract


from math import sqrt

def cnpj(apelido_fundo):
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
            'MILES' : '28069983000131',
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
    return apelido_fundo,Fundos[apelido_fundo]

#def possiveis_precos(num):
#    num = abs(int(num))
#    lista1 = []
#    lista2 = []

#    for i in range(1, int(sqrt(num)) + 1):
#        if (num % i == 0):
#            lista1.append(str(i / float(100)))
#            lista2.append(str(num / float(100 * i)))

#    return list(map(lambda x : x+'0' if x[-2] == '.' else x,lista1+lista2[::-1]))

#def possiveis_precos_2(num):
#    num = abs(int(str(num)[:-2]+'00'))
#    lista =[]
#    for l in range(100):
#        lista1 = []
#        lista2 = []

#        for i in range(1, int(sqrt(num+l)) + 1):
#            if ((num+l) % i == 0):
#                lista1.append(str(i / float(100)))
#                lista2.append(str((num+l) / float(100 * i)))

#        lista+= list(map(lambda x : x+'0' if x[-2] == '.' else x,lista1+lista2[::-1]))
#    return lista

def mudancas_morfologicas(imagem,x=3,tipo='erode'):
    im_gray = np.array(imagem)
    kernel = np.ones((x, x), np.uint8)
    if tipo == 'erode' or tipo == 'dilate':
        im_gray = cv2.erode(im_gray, kernel, iterations=1)
        im_gray = cv2.dilate(im_gray, kernel, iterations=1)
    if tipo == 'open' or tipo == 'close':
        im_gray = cv2.morphologyEx(im_gray, cv2.MORPH_OPEN, kernel)
        im_gray = cv2.morphologyEx(im_gray, cv2.MORPH_CLOSE, kernel)
    resposta = pytesseract.image_to_string(im_gray, lang='eng',config='-c tessedit_char_whitelist=0123456789').replace(' ', '').replace('.', '').replace(',', '').replace('-', '')
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

def parse_html_tudo_int(apelido_fundo,anomes,candidatos=False):

    html  = open('htmls\\'+apelido_fundo+'\\'+str(anomes)+cnpj(apelido_fundo)[1]+'.html').read()

    a = re.findall(r"CDADetAplic\.aspx\?PkCDAAplic=(.*)'\)(.*?) STYLE=(.*?)cursor: hand; COLOR:(.*?)<b></b>\ (.*?)<br><b>(.*?)</b>\ (.*?)<br>(.*?)</span></td><td align=(.*?)center",html)
    ativo =list(map(lambda x : (x[4],x[5],x[6],x[7].replace('<br><b>',' ').replace('<b> ','').replace('</b> ','').replace('<br>','').replace('<b>','')),a))
    ativo+=list(map(lambda x : (x,'','',''),re.findall(r'<b></b>\ (.*?)<br></b>',html)))
    ativo1,ativo2,ativo3,ativo4 = zip(*ativo)
    aserestudado = re.findall(r"CDADetAplic.aspx\?PkCDAAplic=(.*)'",html)
    classificacao = [x.replace('<br>',' ').replace('negociação','negociacao')  for x in re.findall(r'TpNegoc">(.*?)</span>',html)]
    emp_ligada = [x.replace('Não','Nao') for x in re.findall(r'EmpLigada">(.*?)</span></td>', html)]
    emp_ligada_E_vendas_quant = re.findall(r'EmpLigada">(.*?)</span></td><td align="center">(.*?)</td>', html)
    vendas_quant = list(map(lambda x : x[1].replace('.','').replace(',',''),emp_ligada_E_vendas_quant))
    vendas_quant += ['']*int(len(emp_ligada)-len(emp_ligada_E_vendas_quant))

    fechado = [False]*int(len(emp_ligada_E_vendas_quant)) + [True]*int(len(emp_ligada)-len(emp_ligada_E_vendas_quant))


    vendas_montante_E_aquis_quant = re.findall(r'VendasNegoc">(.*?)</span></td><td align="center">(.*?)</td>', html)
    #vendas_montante = list(map(lambda x : x[0].replace('.','').replace(',','') ,vendas_montante_E_aquis_quant))
    vendas_montante = list(map(lambda x : x[0].replace('.','').replace(',','') if ',' in x[0] or x[0] == '' else x[0].replace('.','')+'00',vendas_montante_E_aquis_quant))
    aquis_quant     = list(map(lambda x : x[1].replace('.','').replace(',',''),vendas_montante_E_aquis_quant))
    a= re.findall(r'VendasNegoc">(.*?)</span></td>', html)
    #vendas_montante += [x.replace('.','').replace(',','')  for x in a[len(vendas_montante_E_aquis_quant)::] ]
    vendas_montante += [x.replace('.','').replace(',','') if ',' in x or x == '' else x.replace('.','')+'00' for x in a[len(vendas_montante_E_aquis_quant)::] ]
    aquis_quant += ['']*int(len(a)-len(vendas_montante_E_aquis_quant))

    aquis_montante_E_pf_quant= re.findall(r'AquisNegoc">(.*?)</span></td><td align="center">(.*?)</td>', html)
    #aquis_montante = list(map(lambda x : x[0].replace('.','').replace(',',''),aquis_montante_E_pf_quant))
    aquis_montante = list(map(lambda x : x[0].replace('.','').replace(',','') if ',' in x[0] or x[0] == '' else x[0].replace('.','')+'00',aquis_montante_E_pf_quant))
    pf_quant     = list(map(lambda x : x[1].replace('.','').replace(',',''),aquis_montante_E_pf_quant))
    a = re.findall(r'AquisNegoc">(.*?)</span></td>', html)
    #aquis_montante += [x.replace('.','').replace(',','')  for x in a[len(aquis_montante_E_pf_quant)::]]
    aquis_montante += [x.replace('.','').replace(',','') if ',' in x or x == '' else x.replace('.','')+'00' for x in a[len(aquis_montante_E_pf_quant)::]]
    pf_quant += ['']*int(len(a)-len(aquis_montante_E_pf_quant))

    pf_valor_custo = list(map(lambda x : x.replace('.','').replace(',',''),re.findall(r'CustoCorrecPosFim">(.*?)</span></td>', html)))
    pf_valor_mercado_E_porcent_partrimonio_liquido = re.findall(r'lPosFim">(.*)</span></td><td align="center">(.*?)</td>', html)
    #pf_valor_mercado = list(map(lambda x : x[0].replace('.','').replace(',',''),pf_valor_mercado_E_porcent_partrimonio_liquido))
    pf_valor_mercado = list(map(lambda x : x[0].replace('.','').replace(',','') if ',' in x[0] or x[0] == '' else x[0].replace('.','')+'00',pf_valor_mercado_E_porcent_partrimonio_liquido))
    porcent_partrimonio_liquido    = list(map(lambda x : x[1].replace('.','').replace(',','.'),pf_valor_mercado_E_porcent_partrimonio_liquido))

    
    #aux = pd.DataFrame({'aserestudado':[int(x) for x in aserestudado],'ativo1':ativo1,'ativo2':ativo2,'ativo3':ativo3,'ativo4':ativo4,'classificacao':classificacao,'emp_ligada':emp_ligada,'vendas_quant':vendas_quant,'vendas_montante':vendas_montante,'aquis_quant':aquis_quant,'aquis_montante':aquis_montante,'pf_quant':pf_quant,'pf_valor_custo':pf_valor_custo, 'pf_valor_mercado':pf_valor_mercado ,'porcent_partrimonio_liquido':[float(x) if x != '' else np.nan for x in porcent_partrimonio_liquido ]},index = np.arange(0,len(ativo))) 
    aux = pd.DataFrame({'fechado':fechado,'aserestudado':[int(x) for x in aserestudado],'ativo1':ativo1,'ativo2':ativo2,'ativo3':ativo3,'ativo4':ativo4,'classificacao':classificacao,'emp_ligada':emp_ligada,'vendas_quant':[int(x) if x != '' else np.nan for x in vendas_quant],'vendas_montante':[int(x) if x != '' else np.nan for x in  vendas_montante],'aquis_quant':[int(x) if x != '' else np.nan for x in  aquis_quant],'aquis_montante':[int(x) if x != '' else np.nan for x in  aquis_montante],'pf_quant':[int(x) if x != '' else np.nan for x in  pf_quant],'pf_valor_custo':pf_valor_custo, 'pf_valor_mercado':[int(x) if x != '' else np.nan for x in pf_valor_mercado] ,'porcent_partrimonio_liquido':[float(x) if x != '' else np.nan for x in porcent_partrimonio_liquido ]},index = np.arange(0,len(ativo)))
    aux = aux[['aserestudado','ativo1','ativo2','ativo3','ativo4','classificacao','emp_ligada','vendas_quant','vendas_montante','aquis_quant','aquis_montante','pf_quant','pf_valor_custo','pf_valor_mercado','porcent_partrimonio_liquido','fechado']]
    aux = aux.mask(aux == '', np.nan).sort_values(by='aserestudado')
    
    
    

    
    #aux['candidatos'] = np.nan
    #aux['cand_pf_quant'] = np.nan 
    if candidatos:
        precos = pd.read_csv(str(anomes)[:-2]+'.txt',dtype={'PREULT': str},usecols=['TPMERC','DATA','CODNEG','PREULT'],index_col=False,sep=';',header=0)
        #precos = pd.read_csv('C:\\Users\\luiz.cavalcante\\Documents\\'+str(anomes)[:-2]+'.txt',dtype={'PREULT': str},usecols=['TPMERC','DATA','CODNEG','PREULT'],index_col=False,sep=';',header=0)
        precos = precos[(precos.TPMERC == 10.0)&(precos.DATA < 100*(anomes+1))&(precos.DATA > 100*anomes)].groupby('CODNEG').tail(1).sort_values(by='CODNEG')[['CODNEG','PREULT']]
        precos[['PREULT']] = precos[['PREULT']].applymap(lambda x: str(x).replace('.',',') if x else np.nan)
        precos[['PREULT']] = precos[['PREULT']].applymap(lambda x: (x+'0').replace(',','.') if (x[-2]==',') else x.replace(',','.'))
        
        p_1 =precos[precos.PREULT >'1.00']

        y=pd.DataFrame([(w[0],d[0],int(d[1].replace('.','')),(int((100+abs(int(w[13])))//int(d[1].replace('.',''))))) for w in aux.values  for d in p_1.values if (int(d[1].replace('.',''))*(int(abs(int(w[13]))//int(d[1].replace('.',''))))-abs(int(w[13])))% int(d[1].replace('.',''))< 100])
        
        cand = pd.DataFrame(y.groupby(0)[1].apply(list).reset_index(name='candidatos'))
        cand.columns = ['aserestudado','candidatos']

        quant_cand = pd.DataFrame(y.groupby(0)[3].apply(list).reset_index(name='cand_pf_quant'))
        quant_cand.columns = ['aserestudado','cand_pf_quant']
        
        
        #aux = pd.merge(pd.merge(aux, cand, how='left', on=['aserestudado']), quant_cand, how='left', on=['aserestudado'])
        aux = aux.reset_index().merge(cand, how="left",on=['aserestudado']).set_index('index')
        aux.index = list(aux.index)
        aux = aux.reset_index().merge(quant_cand, how="left",on=['aserestudado']).set_index('index')
        aux.index = list(aux.index)
        
   
    iterator = re.findall(r'id="lbNmDenomSocialAdm">(.*?)</span></td><td colspan="6"><B>CNPJ:&nbsp;</B><span id="lbNrPfPjAdm">(.*?)</span></td>',html)
    adm,adm_cnpj = [(x[0],x[1].replace('.','').replace('-','').replace('/','')) for x in iterator][0]

    iterator =re.findall(r'id="lbPatrimLiq">R\$ (.*?)</span></td><td colspan="6"><b>Data de Recebimento das Informações:&nbsp;</b><span id="lbDtRegDoc">(.*?)</span></td>',html)
    pl,hora_recebimento = [(x[0].replace('.','').replace(',','.'),'-'.join(x[1].split(' ')[0].split('/')[::-1])) for x in iterator][0]
    
    iterator = re.findall(r'id="lbNmDenomSocial">(.*?)</span></td><td colspan="6"><B>CNPJ:&nbsp;</B><span id="lbNrPfPj">(.*?)</span></td>',html)
    fundo,fundo_cnpj = [(x[0],x[1].replace('.','').replace('-','').replace('/','')) for x in iterator][0]

    #if str(int(cnpj)) != str(int(fundo_cnpj)): print('deu erro, penultima linha de planilhar',cnpj,fundo_cnpj)
    
    return aux,fundo,fundo_cnpj,adm,adm_cnpj,pl,hora_recebimento

