Workbench Visual de Sistemas Reparáveis

Visão geral

Repairable Systems Visual Workbench é uma aplicação desktop independente para análise exploratória de confiabilidade de sistemas reparáveis. Ela fornece uma interface visual para inserir dados de falha, ajustar um modelo de Processo de Lei de Potência, gerar gráficos diagnósticos e exportar resultados estatísticos.

Este projeto é uma implementação independente de software baseada em métodos estatísticos públicos para NHPP, modelagem por Processo de Lei de Potência e análise de crescimento de confiabilidade. Ele não é uma publicação oficial, endosso, certificação ou ferramenta validada por qualquer organização normativa, editora ou instituição terceira.

Principais recursos

1. Entrada visual de dados com tabelas em estilo planilha
2. Suporte para dados de item único, múltiplos itens com horizonte comum de observação, múltiplos itens com horizontes diferentes de observação e dados agrupados por intervalo
3. Estimação de beta, lambda e intensidade de falha z(t)
4. Gráficos de falhas acumuladas, gráficos log log, gráficos QQ, gráficos TTT e gráficos de intensidade
5. Bandas de confiança baseadas em bootstrap para curvas do modelo quando habilitadas
6. Avaliação de aderência usando simulação de Cramer von Mises
7. Exportação de gráficos e resumos estatísticos
8. Suporte a interface multilíngue

Núcleo matemático

A aplicação implementa a forma do Processo de Lei de Potência

Lambda(t) = lambda t^beta

z(t) = lambda beta t^(beta menos 1)

Os valores críticos de Cramer von Mises são calculados por simulação Monte Carlo em tempo de execução. O programa não inclui tabelas reproduzidas de valores críticos. Em cada simulação, são geradas amostras uniformes ordenadas, o parâmetro relativo de forma é estimado novamente, a estatística de Cramer von Mises é calculada e o quantil solicitado é usado como limiar crítico.

Os limites de confiança para z(t) são calculados por aproximações analíticas e procedimentos de bootstrap, dependendo da opção selecionada. Nenhuma tabulação embutida é usada nesses cálculos.

Exemplos de dados

Os exemplos embutidos são sintéticos e gerados apenas para demonstração do software. Eles não são copiados de qualquer publicação protegida ou fonte proprietária de dados.

Estrutura do projeto

run_workbench.py
    Ponto de entrada principal usado para iniciar a aplicação.

repairable_workbench/i18n.py
    Textos da interface, traduções, rótulos e dicionários de idioma.

repairable_workbench/math_core.py
    Estimação estatística, ajuste de modelo, cálculos de aderência, intervalos de confiança, rotinas de bootstrap e geração de valores críticos por Monte Carlo.

repairable_workbench/results.py
    Contêineres de resultados e resumos estatísticos formatados.

repairable_workbench/plotting.py
    Utilitários de preparação de gráficos e suporte para curvas do modelo.

repairable_workbench/resources.py
    Importação, exportação, salvamento, exemplos sintéticos e recursos auxiliares.

repairable_workbench/ui_components.py
    Componentes visuais reutilizáveis, incluindo tabelas de dados em estilo planilha.

repairable_workbench/visual.py
    Interface gráfica principal e layout da aplicação.

Instalação

Python 3.10 ou mais recente é recomendado.

Instale os pacotes necessários com

pip install numpy scipy matplotlib

Executando a aplicação

A partir da pasta do projeto, execute

python run_workbench.py

Exemplo no Windows

cd "C:\Users\Windows\Documents\Projects\modular_workbench_v3"
C:\Users\Windows\AppData\Local\Programs\Python\Python313\python.exe .\run_workbench.py

Se o arquivo ZIP criar uma pasta aninhada, entre na pasta interna que contém run_workbench.py e o diretório repairable_workbench antes de executar o comando.

Principal mudança recente

O principal arquivo alterado nesta versão é

repairable_workbench/math_core.py

A lógica anterior baseada em tabela fixa para o limiar de Cramer von Mises foi substituída pela geração de valores críticos por Monte Carlo.

Notas para publicação

Este repositório é destinado a software educacional e de engenharia independente. Antes da publicação pública, evite adicionar texto protegido, tabelas reproduzidas, capturas de tela, figuras, logotipos ou exemplos copiados de normas comerciais, livros, manuais ou relatórios internos proprietários.

Nomes recomendados para o repositório

repairable_systems_workbench
nhpp_reliability_workbench
power_law_process_workbench

Descrição curta sugerida para o repositório

Workbench visual independente para análise de confiabilidade de sistemas reparáveis usando métodos NHPP e Processo de Lei de Potência.

Licença

Adicione um arquivo de licença antes de publicar o projeto. Para publicação pública como código aberto, opções comuns são MIT, BSD 3 Clause, Apache 2.0 ou GPL 3.0, dependendo de quão permissivos você deseja que sejam os termos de reutilização.