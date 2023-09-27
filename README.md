# Implementação de um Modelo Vetorial para Busca e Recuperação de Dados

Este trabalho é o primeiro projeto da dicsciplina Busca e Mineração de Dados, pertencente ao programa de Mestrado do PESC-UFRJ. 
Os programas são separados em quatro eixos principais e que, no desenvolvimento, foram feitos de maneira que um consumisse o output do outro. Os eixo são:

1. Processador de Queries: preenchimento de um banco de dados textual (corpus/coleção de documentos), a partir de atas médicas sobre Fibrose Cística (em inglês). Os textos podiam ser salvos na íntegra ou pré-processados, utilizando 
principalmente a biblioteca NLTK. Tokenização, remoção de stopwords e realização de Stemming eram algumas das opções de tratamento.

2. Geração de Lista Invertida (GLI): a partir da frequência de cada termo, foi construída uma lista ordenada de maneira crescente. Os documentos em que as palavras apareciam (indicados agora por números) eram salvos
junto do termo relacionado. Caso aparecesse mais de uma vez, o identificador do documento era repetido.

3. Indexador: a partir da Lista Invertida, a transformação para um espaço vetorial - utilizando medidas como de Frequência de Termo e Inversa de Frequência de Documento (TF-IDF) - seriam o próximo passo.

4. Busca: com todo o dataset transformado, era hora de realizarmos as buscas com base em um documento fornecido pelo professor. Diante dos resultados obtidos e daqueles esperados, seria possível chegar a métricas de acurácia, recall, entre outras.

Uma análise mais aprofundada da performance era um objetivo posterior, que acabou não sendo factível no tempo hábil.


