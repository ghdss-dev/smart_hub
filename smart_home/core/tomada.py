from .dispositivo_base import DispositivoBase
from datetime import datetime
from typing import Optional

from ..hub.observer import Subject


class ValidacaoAtribute(Exception):
    pass


class TomadaInteligente(DispositivoBase, Subject):

    def __init__(self, id_dispositivo, nome, potencia_W=100):

        estados = ['ligada', 'desligada']

        super().__init__(id_dispositivo, nome, tipo='TOMADA', estados=estados, estado_inicial='desligada')

        self._potencia_W = potencia_W
        self._consumo_wh = 0.0
        self._momento_ligado: Optional[datetime] = None

        self.machine.add_transition('ligar', 'desligada', 'ligada', after='_registrar_inicio')
        self.machine.add_transition('desligar', 'ligada', 'desligada', after='_calcular_consumo')

    @property
    def potencia_W(self):

        return self._potencia_W

    @potencia_W.setter
    def potencia_W(self, valor):

        if valor < 0:
            raise ValidacaoAtribute("Potência deve ser > 0")
        self._potencia_W = valor

    def _registrar_inicio(self):

        self._momento_ligado = datetime.utcnow()
        self.notify(event='ligar', detalhes=self.detalhes())
        print(f"[INFO] Tomada {self.nome} ligada")

    def _calcular_consumo(self):

        if not self._momento_ligado:
            return

        agora = datetime.utcnow()
        duracao = agora - self._momento_ligado
        horas = duracao.total_seconds() / 3600.0
        wh = self._potencia_W * horas
        self._consumo_wh += wh

        # reset
        self._momento_ligado = None
        self.notify(event='desligar', detalhes=self.detalhes())
        print(f"[INFO] Tomada {self.nome} desligada — consumo adicionado: {wh:.3f} Wh")

    def consumo_total(self):

        total = self._consumo_wh
        if self.state == "ligada" and self._momento_ligado:
            agora = datetime.utcnow()
            duracao = agora - self._momento_ligado
            horas = duracao.total_seconds() / 3600.0
            total += self._potencia_W * horas
        return round(total, 2)

    def gerar_consumo_simulado(self, minutos: int = 1):

        if self.state != 'ligada':
            return 0.0
        wh = (self._potencia_W * (minutos / 60.0))
        self._consumo_wh += wh
        self.notify(event='consumo', detalhes=self.detalhes())
        return wh

    def detalhes(self):

        return {

            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, 'state', None),
            "potencia_W": self.potencia_W,
            "consumo_wh": self.consumo_total(),  # já mostra consumo parcial em tempo real
        }