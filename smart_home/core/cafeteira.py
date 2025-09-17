from .dispositivo_base import DispositivoBase
from datetime import datetime

class Cafeteira(DispositivoBase):
    def __init__(self, id_dispositivo, nome):
        estados = ["desligada", "ligada", "preparando"]
        super().__init__(id_dispositivo, nome, tipo="CAFETEIRA", estados=estados, estado_inicial="desligada")

        self._momento_ligado = None

        # Definindo as transições
        self.machine.add_transition("ligar", "desligada", "ligada", after="_on_ligar")
        self.machine.add_transition("desligar", ["ligada", "preparando"], "desligada", after="_on_desligar")
        self.machine.add_transition("preparar", "ligada", "preparando", after="_on_preparar")

    def _on_ligar(self):
        self._momento_ligado = datetime.utcnow()
        self.notify(event="ligar", detalhes=self.detalhes())
        print(f"[INFO] Cafeteira {self.nome} ligada")

    def _on_desligar(self):
        self._momento_ligado = None
        self.notify(event="desligar", detalhes=self.detalhes())
        print(f"[INFO] Cafeteira {self.nome} desligada")

    def _on_preparar(self):
        self.notify(event="preparar", detalhes=self.detalhes())
        print(f"[INFO] Cafeteira {self.nome} iniciou o preparo do café")

    def detalhes(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, "state", None),
        }
