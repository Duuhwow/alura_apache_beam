# alura_apahce_beam
Descrição do Repositório

🚀 Este repositório contém um projeto em Python que realiza a ingestão de dados utilizando a SDK do Apache Beam. O objetivo é trazer o Apache Beam para dentro do projeto e implementar todas as etapas necessárias, desde a ingestão de dados até a persistência.

📊 O processo de ingestão de dados começa com a utilização do ReadFromText para ler os dados brutos. O dataset inclui informações sobre a quantidade de casos de dengue por cidade, bem como dados de quantidade de chuva ou precipitação meteorológica de diferentes estações.

🔄 Após a leitura dos arquivos, são aplicadas diversas transformações com base nas regras de negócio definidas durante a fase de análise. Para isso, são utilizados métodos como Map, FlatMap e operações de agrupamento e combinação por chave com um método de soma. Essas transformações são aplicadas em pipelines para processar os dados passo a passo.

💾 Por fim, os dados são persistidos em formato de arquivo de texto no padrão CSV. Utilizamos o método WriteToText do Apache Beam para consolidar todos os tratamentos em um arquivo CSV final.

🔍 O objetivo deste projeto é facilitar a análise posterior dos dados, fornecendo um arquivo CSV estruturado com as informações processadas e tratadas.

📚 Este repositório é uma ótima referência para quem deseja aprender sobre a ingestão de dados usando a SDK do Apache Beam e implementar pipelines de transformação de dados em Python de forma eficiente e escalável.
