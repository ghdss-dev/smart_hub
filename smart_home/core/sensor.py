from .dispositivo_base import DispositivoBase
from datetime import datetime

class Sensor(DispositivoBase):
    def __init__(self, id_dispositivo, nome):
        estados = ["inativo", "ativo"]
        super().__init__(id_dispositivo, nome, tipo="SENSOR", estados=estados, estado_inicial="inativo")

        self._ultimo_ativado = None

        self.machine.add_transition("ativar", "inativo", "ativo", after="_on_ativar")
        self.machine.add_transition("desativar", "ativo", "inativo", after="_on_desativar")

    def _on_ativar(self):
        self._ultimo_ativado = datetime.utcnow()
        self.notify(event="ativar", detalhes=self.detalhes())
        print(f"[INFO] Sensor {self.nome} ativado")

    def _on_desativar(self):
        self.notify(event="desativar", detalhes=self.detalhes())
        print(f"[INFO] Sensor {self.nome} desativado")

    def detalhes(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, "state", None),
            "ultimo_ativado": self._ultimo_ativado.isoformat() if self._ultimo_ativado else None,
        }
