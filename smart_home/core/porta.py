from .dispositivo_base import DispositivoBase
from smart_home.hub.observer import Subject

class TransicaoInvalida(Exception):
    pass

class Port(DispositivoBase, Subject):

    def __init__(self, id_dispositivo, nome):

        estados = ['trancada', 'destrancada', 'aberta']

        super().__init__(id_dispositivo, nome, tipo='PORTA', estados=estados, estado_inicial='destrancada')

        self.machine.add_transition('abrir', 'destrancada', 'aberta', after='_on_abrir')
        self.machine.add_transition('fechar', 'aberta', 'destrancada', after='_on_fechar')
        self.machine.add_transition('destrancar', 'trancada', 'destrancada', after='_on_destrancar')
        self.machine.add_transition('trancar', 'destrancada', 'trancada', conditions=['pode_trancar'], after='_on_trancar')

    def abrir(self):

        if self.state == 'trancada':

            raise Exception("Porta está trancada, não pode abrir. Primeiro destranque.")

        elif self.state == 'aberta':

            raise Exception("Porta já está aberta.")

        self.machine.abrir()

    def fechar(self):
        if self.state == 'destrancada':

            raise Exception("Porta já está fechada (destrancada).")

        elif self.state == 'trancada':

            raise Exception("Porta já está fechada e trancada.")

        self.machine.fechar()

    def trancar(self):

        if self.state == 'aberta':

            raise Exception("Porta aberta, não pode trancar.")

        elif self.state == 'trancada':

            raise Exception("Porta já está trancada.")

        self.machine.trancar()

    def destrancar(self):

        if self.state == 'destrancada':

            raise Exception("Porta já está destrancada.")

        elif self.state == 'aberta':

            raise Exception("Porta aberta não precisa ser destrancada.")

        self.machine.destrancar()

    def pode_trancar(self):

        return self.state != 'aberta'

    def _on_abrir(self):

        self.notify(event='abrir', detalhes=self.detalhes())

        print("[INFO] Porta aberta")

    def _on_fechar(self):

        self.notify(event='fechar', detalhes=self.detalhes())
        print("[INFO] Porta fechada")

    def _on_destrancar(self):

        self.notify(event='destrancar', detalhes=self.detalhes())
        print("[INFO] Porta destrancada")

    def _on_trancar(self):

        self.notify(event='trancar', detalhes=self.detalhes())
        print("[INFO] Porta trancada")

    def detalhes(self):

        return {

            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, 'state', None),

        }
