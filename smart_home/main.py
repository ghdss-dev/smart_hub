import os
from smart_home.hub.automacao import AutomacaoResidencial

automacao = AutomacaoResidencial("smart_home/config/config_exemplo.json")

for d in automacao.dispositivos:
    print(d.detalhes())
