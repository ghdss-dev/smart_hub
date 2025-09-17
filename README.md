# 🏠 Sistema de Automação Inteligente

Projeto desenvolvido em Python para simular um **hub de automação residencial**, permitindo gerenciar e monitorar dispositivos inteligentes como luzes, tomadas, portas, persianas, sensores e cafeteiras.

## ✨ Funcionalidades

- 📋 **Gerenciar dispositivos**  
  - Listar dispositivos cadastrados  
  - Mostrar detalhes de cada dispositivo  
  - Executar comandos (ligar, desligar, abrir, trancar, etc.)  
  - Alterar atributos (ex: brilho da luz, potência da tomada, cor RGB)  
  - Adicionar e remover dispositivos  

- 📦 **Rotinas inteligentes**  
  - Criar rotinas que executam ações em vários dispositivos  
  - Executar rotinas já cadastradas  

- 📊 **Relatórios e Consumo**  
  - Gerar relatório de consumo de energia por tomada  
  - Exportar eventos registrados para **CSV**  

- 💾 **Persistência de dados**  
  - Salvar e carregar configuração em JSON  
  - Histórico de eventos  

## 🛠️ Tecnologias Utilizadas

- **Python 3.13+**
- Padrões de **POO (Programação Orientada a Objetos)**
- **Máquinas de estados** para dispositivos  
- Armazenamento em **JSON**  
- Exportação de dados em **CSV**

- ## 🚀 Como Executar o Projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/smart_hub.git
   cd smart_hub

Crie e ative o ambiente virtual:

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate  

Execute o menu principal:

python smart_home/cli/menu.py

Exemplo de Uso
**** SMART HOME HUB ****
1 - Listar dispositivos
2 - Mostrar dispositivo
3 - Executar comando em dispositivo
4 - Alterar atributo de dispositivo
5 - Executar rotina
6 - Gerar relatório
7 - Salvar configuração
8 - Adicionar dispositivo
9 - Remover dispositivo
10 - Sair
11 - Criar rotina
12 - Exportar eventos para CSV

Estrutura do Projeto
smart_home/
│
├── cli/              # Interface do menu em linha de comando
├── core/             # Classes principais dos dispositivos
├── config/           # Arquivos de configuração JSON
├── data/             # Relatórios e CSVs gerados
└── hub/              # Lógica do hub principal

Autor

Projeto desenvolvido como parte do trabalho acadêmico da disciplina de Robótica / Programação Orientada a Objetos.
Professor: Leopoldo
Aluno: Gustavo Henrique de Souza Silva
