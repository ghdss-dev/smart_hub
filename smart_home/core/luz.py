from .dispositivo_base import DispositivoBase
from enum import Enum
from datetime import datetime


class CorRGB(Enum):
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    @classmethod
    def from_str(cls, cor_str, default=None):
        if not cor_str:
            return default or cls.WHITE
        try:
            return cls[cor_str.upper()]
        except KeyError:
            return default or cls.WHITE


class ValidacaoAtributo(Exception):
    pass

class Luz(DispositivoBase):
    def __init__(self, id_dispositivo, nome, brilho=100, cor=CorRGB.WHITE):
        estados = ["ligada", "desligada"]
        super().__init__(id_dispositivo, nome, tipo="LUZ", estados=estados, estado_inicial="desligada")

        self._brilho = None
        self._cor = None
        self._momento_ligado = None

        self.machine.add_transition("ligar", "desligada", "ligada", after="_on_ligar")
        self.machine.add_transition("desligar", "ligada", "desligada", after="_on_desligar")

        self._brilho = brilho
        self._cor = cor

    def _on_ligar(self):
        self._momento_ligado = datetime.utcnow()
        self.notify(event="ligar", detalhes=self.detalhes())
        print(f"[INFO] Luz {self.nome} ligada")

    def _on_desligar(self):
        self._momento_ligado = None
        self.notify(event="desligar", detalhes=self.detalhes())
        print(f"[INFO] Luz {self.nome} desligada")

    @property
    def brilho(self):
        return self._brilho

    @brilho.setter
    def brilho(self, valor: int):
        if not isinstance(valor, int) or not (0 <= valor <= 100):
            raise ValidacaoAtributo(f"Brilho inválido: {valor}")
        self._brilho = valor
        print(f"[INFO] Brilho ajustado para {valor}%")

    @property
    def cor(self):
        return self._cor

    @cor.setter
    def cor(self, cor):
        if not isinstance(cor, CorRGB):
            raise ValidacaoAtributo(f"Cor inválida: {cor}")
        self._cor = cor
        print(f"[INFO] Cor definida para {cor.name}")

    def detalhes(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, "state", None),
            "brilho": self._brilho,
            "cor": self._cor.name if self._cor else None,
        }
