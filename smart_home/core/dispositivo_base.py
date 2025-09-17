from abc import ABC, abstractmethod
from transitions import Machine
from smart_home.hub.observer import Subject
from typing import Any, List

class DispositivoBase(ABC, Subject):
    state: Any

    def __init__(self, id_dispositivo: str, nome: str, tipo: str, estados: List[str], estado_inicial: str):
        super().__init__()
        self.id = id_dispositivo
        self.nome = nome
        self.tipo = tipo
        self._estados = estados
        self._estado_inicial = estado_inicial
        self.machine = Machine(model=self, states=estados, initial=estado_inicial)

    def get_estado(self):
        return self.state

    def executar_comando(self, comando):

        try:

            metodo = getattr(self, comando)

            if callable(metodo):

                metodo()
                print(f"[INFO] Comando '{comando}' executado em '{self.nome}'.")

            else:

                print(f"[ERRO] '{comando}' não é um comando válido para '{self.nome}'.")

        except AttributeError:

            print(f"[ERRO] O comando '{comando}' não existe para o dispositivo '{self.nome}'.")

        except Exception as e:

            # Mensagem de erro mais clara baseada no estado atual

            print(
                f"[ERRO] O comando '{comando}' não pode ser executado "
                f"no estado atual ('{self.state}') do dispositivo '{self.nome}'."
            )

    @abstractmethod
    def detalhes(self):
        pass
