import configparser
import pandas as pd
import xml.etree.ElementTree as ET
from unidecode import unidecode


config = configparser.ConfigParser();
config.read("pc.cfg");


def read_xml_file():
    filepath = config["QUERY_CONFIG"]["LEIA"];
    with open(filepath) as f:
        file_content = ET.parse(f);
        print(file_content);
    return file_content.getroot()


def generate_query_and_expected_csv(et):
    
    # Pegando campos de um consulta
    fields = [];
    for child in et.find("QUERY"):
        fields.append(child.tag);
    
    # Primeiro arquivo -> CONSULTAS
    queries = pd.DataFrame(columns=fields[:2]);
    for q in et.iter("QUERY"):
        queries["QueryNumber"] = int(q.find("QueryNumber").text)
        queries["QueryText"] = unidecode(q.find("QueryText").text).upper()


    print(queries);
    # Segundo arquivo -> ESPERADOS
    #expected = pd.DataFrame(columns=[fields[0],"DocNumber","DocVotes"]);



    pass
    

ui = read_xml_file()    
generate_query_and_expected_csv(ui);