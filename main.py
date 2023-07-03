import apache_beam as beam
import re
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

pipeline_options = PipelineOptions(argv=None)
pipeline = beam.Pipeline(options=pipeline_options)

colunas_dengue = [
        'id',
        'data_iniSE',
        'casos',
        'ibge_code',
        'cidade',
        'uf',
        'cep',
        'latitude',
        'longitude']

def lista_para_dicionario(elemento, colunas):
    "Recebe 2 listas"
    "Retorna 1 dicionario"
    return dict(zip(colunas, elemento))

def texto_para_lista (elemento, delimitador='|'):
    "Recebe um texto e um delimitador"
    "Retorna uma lista de elementos pelo delimitador"

    return elemento.split(delimitador)

def trata_datas(elemento):
    "Recebe um dicionário e cria um novo campo com ANO-MES"
    "Retorna o mesmo dicionário com o novo campo"
    elemento['ano_mes'] = '-'.join(elemento['data_iniSE'].split('-')[:2])
    return elemento

def chave_uf(elemento):
    "Recebe um dicionário"
    "Retorna uma tupla com o estado (UF) e o elemento (UF, dicionário)"
    chave = elemento['uf']
    return(chave, elemento)

def casos_dengue(elemento):
    "Recebe uma tupla ('RS', [{},{}])"
    "Retorna uma tupla ('RS-20140-12, 8.0)"
    uf, registros = elemento
    for registro in registros:
        if bool(re.search(r'\d', registro['casos'])):
            yield (f"{uf}-{registro['ano_mes']}", float(registro['casos']))
        else:
            yield (f"{uf}-{registro['ano_mes']}", 0.0)

def  chave_uf_ano_mes_de_lista(elemento):
    "Recebe uma lista de elementos"
    "Retorna uma tupla contendo uma chave e o valor de chuva em mm"
    "Exemplo (UF-ANO-MES, 1.3)"
    data, mm, uf = elemento
    ano_mes = '-'.join(data.split('-')[:2])
    chave = f'{uf}-{ano_mes}'
    if float(mm) < 0:
        mm = 0.0
    else:
        mm = float(mm)
    return chave, mm

def arredonda(elemento):
    "Recebe uma tupla"
    "Retorna uma tupla com o valor arrendado"
    chave, mm = elemento
    return (chave, round(mm, 1))


def filtra_campos_vazios(elemento):
    "Remove elementos que tenham chaves vazias"
    "Recebe uma tupla e retorna uma tupla sem campos ou chavez vazias"
    chave, dados = elemento
    if all([
        dados ['chuvas'],
        dados['dengue']    
        ]):
        return True
    return False


def descompactar_elemento(elem):
    "Recebe uma tupla EX: ('CE-2015-11', {'chuvas': [0.4], 'dengue': [21.0]})"
    "Retorna uma tupla EX: ('CE', '2015', '11', '0.4', '21.0')"
    chave, dados = elem
    chuva = dados['chuvas'][0]
    dengue = dados['dengue'][0]
    uf, ano, mes = chave.split('-')
    return uf, ano, mes, str(chuva), str(dengue)

def preparar_csv(elem, delimitador=';'):
    "Recebe uma tupla EX:('CE', 2015, 11, 0.4, 21.0)"
    "Retorna uma string delmitada EX: 'CE;2015;11;0.4;21.0'"
    return f"{delimitador}".join(elem)

#pcollec, vai receber o resultado de todos os passos posteiormente 
#cada pipe '|' é um passo 
dengue = (
    pipeline
    | "Leitura do dataset de casos dengue" >> 
        ReadFromText('casos_dengue.txt', skip_header_lines=1)
    | "De texto para lista" >> beam.Map(texto_para_lista)
    | "De lista para dicionario" >> beam.Map(lista_para_dicionario, colunas_dengue)
    | "Criar campo ano_mes" >>beam.Map(trata_datas)
    | "Criar chave pelo estado" >> beam.Map(chave_uf)
    | "Agrupar pelo estado" >> beam.GroupByKey()
    | "Descompactar casos de dengue" >> beam.FlatMap(casos_dengue)
    | "Soma dos casos pela chave" >> beam.CombinePerKey(sum)
)

chuvas = (
    pipeline
    | "Leitura do dataset de dengue" >> 
        ReadFromText('chuvas.csv', skip_header_lines=1)
    | "De texto para lista (chuvas)" >> beam.Map(texto_para_lista, delimitador=',')
    | "Criando uma chave UF-ANO-MES" >> beam.Map(chave_uf_ano_mes_de_lista)
    | "Soma do total de chuvas pela chave" >> beam.CombinePerKey(sum)
    | "Arredondar resultados de chuvas" >> beam.Map(arredonda)
)

resultado = (
    #(chuvas, dengue)
    #| "Empilha as pcollec" >> beam.Flatten()
    #| "Agrupa as pcollec" >> beam.GroupByKey
    ({'chuvas': chuvas, 'dengue': dengue})
    | "Mesclar pcollec" >> beam.CoGroupByKey()
    | "Filtra dados vaios" >> beam.Filter(filtra_campos_vazios)
    | "Descompactar elementos" >> beam.Map(descompactar_elemento)
    | "Preparar CSV" >> beam.Map(preparar_csv)   
)

                                #Cria um arquivo na mesma pasta do código, com um sufixo .csv
header = 'UF;ANO;MES;CHUVA;DENGUE'
resultado | "Criar arquivo CSV" >> WriteToText('resultado', file_name_suffix='.csv', header=header)


pipeline.run()