from configobj import ConfigObj
import logging

config = {}
try: 
    config = ConfigObj('index.cfg')
    logging.info("The config file was parsed with no errors.")
except Exception as e:
    logging.exception("Errors ocurred while parsing the config file.");
    print("For more information, check the exact error below:")
    print(e)

"""  
    - Cada elemento do vetor criado representa o termo no documento. 
    - Podemos utilizar o peso como semântica do elemento. 
    - O número de termos define as dimensões do espaço vetorial de um documento!
    - Tf-idf é interessante porque considera a relevância de um termo em um documento 
      comparado ao poder de idetificação de um termo. Basicamente a ideia é que se temos um 
      documento com um termo de alta incidência, mas que no corpus todo tem pouca aparição,
      a capacidade de caracterizar documentos do termo é maior (sempre pensando em referenciais)  
"""