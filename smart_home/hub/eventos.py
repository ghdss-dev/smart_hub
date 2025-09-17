from datetime import datetime

class Evento:
    def __init__(self, tipo: str, origem: str, dados: dict = None):
        self.tipo = tipo          # Ex: "mudanca_estado", "sensor_movimento", "acao"
        self.origem = origem      # Nome do dispositivo que gerou o evento
        self.dados = dados or {}  # Informações adicionais
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"<Evento {self.tipo} de {self.origem} em {self.timestamp:%H:%M:%S}>"
