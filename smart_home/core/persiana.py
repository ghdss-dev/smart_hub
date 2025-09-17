from .dispositivo_base import DispositivoBase

class Persiana(DispositivoBase):
    def __init__(self, id_dispositivo, nome):
        estados = ["fechada", "aberta", "entreaberta"]
        super().__init__(id_dispositivo, nome, tipo="PERSIANA", estados=estados, estado_inicial="fechada")

        self.machine.add_transition("abrir", "fechada", "aberta", after="_on_abrir")
        self.machine.add_transition("fechar", ["aberta", "entreaberta"], "fechada", after="_on_fechar")
        self.machine.add_transition("parar", "aberta", "entreaberta", after="_on_parar")

    def _on_abrir(self):
        self.notify(event="abrir", detalhes=self.detalhes())
        print(f"[INFO] Persiana {self.nome} aberta")

    def _on_fechar(self):
        self.notify(event="fechar", detalhes=self.detalhes())
        print(f"[INFO] Persiana {self.nome} fechada")

    def _on_parar(self):
        self.notify(event="parar", detalhes=self.detalhes())
        print(f"[INFO] Persiana {self.nome} entreaberta")

    def detalhes(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "estado": getattr(self, "state", None),
        }
