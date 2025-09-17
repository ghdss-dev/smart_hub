import json
import os
import csv
from smart_home.core.porta import Port
from smart_home.core.luz import Luz, CorRGB
from smart_home.core.tomada import TomadaInteligente
from smart_home.hub.singleton import Singleton
from smart_home.hub.eventos import Evento
from smart_home.hub.consumo_tomada import calcular_consumo_tomada


# -------------------------------
# Ajuste no Enum CorRGB
# -------------------------------
# Se CorRGB ainda não tiver esse método, adicione no arquivo luz.py:
#
# class CorRGB(Enum):
#     WHITE = (255, 255, 255)
#     RED = (255, 0, 0)
#     GREEN = (0, 255, 0)
#     BLUE = (0, 0, 255)
#
#     @classmethod
#     def from_str(cls, cor_str: str, default=None):
#         try:
#             return cls[cor_str.upper()]
#         except KeyError:
#             return default or cls.WHITE


# -------------------------------
# Factory de Dispositivos
# -------------------------------
class DeviceFactory:
    @staticmethod
    def criar_dispositivo(config):
        tipo = config['tipo']
        nome = config.get('nome', 'Sem Nome')
        atributos = config.get('atributos', {})

        if tipo == 'LUZ':
            cor_str = atributos.get('cor', 'WHITE')
            brilho = atributos.get('brilho', 100)
            cor = CorRGB.from_str(cor_str, CorRGB.WHITE)  # ✅ corrigido
            return Luz(config['id'], nome, brilho=brilho, cor=cor)

        elif tipo == 'TOMADA':
            potencia = atributos.get('potencia_W', 100)
            return TomadaInteligente(config['id'], nome, potencia_W=potencia)

        elif tipo == 'PORTA':
            return Port(config['id'], nome)

        else:
            raise ValueError(f"Tipo de dispositivo desconhecido: {tipo}")


# -------------------------------
# Observer de Rotinas
# -------------------------------
class RotinaObserver:
    def __init__(self, regra, dispositivos):
        """
        regra = {
            "quando": "sensor_movimento",
            "origem": "sensor_sala",
            "acao": "ligar",
            "alvo": "luz_sala"
        }
        """
        self.regra = regra
        self.dispositivos = dispositivos

    def atualizar(self, evento: Evento):
        if evento.tipo == self.regra["quando"] and evento.origem == self.regra["origem"]:
            alvo = self.regra["alvo"]
            acao = self.regra["acao"]

            dispositivo = self.dispositivos.get(alvo)
            if dispositivo and hasattr(dispositivo, acao):
                getattr(dispositivo, acao)()
                print(f"[ROTINA] Executada: {self.regra}")
            else:
                print(f"[AVISO] Dispositivo ou ação inválida na rotina: {self.regra}")


# -------------------------------
# AutomacaoResidencial
# -------------------------------
class AutomacaoResidencial(Singleton):

    def __init__(self, caminho_config, caminho_rotinas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observers = []
        if not hasattr(self, '_inicializado'):
            self._caminho_config = caminho_config
            self._caminho_rotinas = caminho_rotinas
            self.dispositivos = self.carregar_dispositivos(caminho_config)
            self.rotinas = self.carregar_rotinas(caminho_rotinas)
            self._inicializado = True

    # -------------------------------
    # Dispositivos
    # -------------------------------
    def carregar_dispositivos(self, caminho_json):
        if not os.path.exists(caminho_json) or os.stat(caminho_json).st_size == 0:
            print(f"[WARN] Arquivo '{caminho_json}' não encontrado ou vazio. Lista de dispositivos vazia.")
            return []

        try:
            with open(caminho_json, 'r') as f:
                dados = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERRO] Falha ao decodificar '{caminho_json}': {e}")
            return []

        dispositivos = []
        for d in dados.get('dispositivos', []):
            try:
                dispositivo = DeviceFactory.criar_dispositivo(d)

                estado_inicial = d.get('estado')
                if estado_inicial and estado_inicial != dispositivo.state:
                    dispositivo.executar_comando(estado_inicial)

                dispositivos.append(dispositivo)
            except Exception as e:
                print(f"[ERRO] Não foi possível carregar '{d.get('nome', 'Sem Nome')}' (ID {d.get('id')}): {e}")

        return dispositivos

    def buscar_por_id(self, id_dispositivo):
        return next((d for d in self.dispositivos if d.id == id_dispositivo), None)

    def listar_dispositivos(self):
        return [d.detalhes() for d in self.dispositivos]

    def adicionar_dispostivo(self, novo_dispositivo):
        if self.buscar_por_id(novo_dispositivo.id):
            print(f"[ERRO] Um dispositivo com o ID '{novo_dispositivo.id}' já existe")
            return False

        self.dispositivos.append(novo_dispositivo)
        print(f"[INFO] Dispositivo: {novo_dispositivo.nome} (ID: {novo_dispositivo.id}) adicionado com sucesso.")
        return True

    def remover_dispositivo(self, id_dispositivo):
        dispositivo_a_remover = self.buscar_por_id(id_dispositivo)

        if dispositivo_a_remover:
            self.dispositivos.remove(dispositivo_a_remover)
            print(f"[INFO] Dispositivo {dispositivo_a_remover.nome} (ID: {id_dispositivo}) removido com sucesso.")
            return True
        else:
            print(f"[ERRO] Dispositivo com o ID '{id_dispositivo}' não encontrado")
            return False

    def salvar_dispositivos(self, caminho_json):
        dispositivos_para_salvar = [d.detalhes() for d in self.dispositivos]
        dados_config = {"dispositivos": dispositivos_para_salvar}

        try:
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(dados_config, f, indent=4)
            print(f"[INFO] Configuração salva em '{caminho_json}'.")
        except IOError as e:
            print(f"[ERRO] Não foi possível salvar o arquivo: {e}")

    # -------------------------------
    # Eventos
    # -------------------------------
    def registrar_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def remover_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def notificar(self, evento: Evento):
        print(f"[EVENTO] {evento}")
        for obs in self.observers:
            obs.atualizar(evento)

    def exportar_eventos_csv(self, eventos, nome_arquivo):
        fieldnames = ["id_dispositivo", "evento", "timestamp"]
        self._salvar_csv(nome_arquivo, fieldnames, eventos)

    # -------------------------------
    # Rotinas
    # -------------------------------
    def carregar_rotinas(self, caminho_rotinas):
        if not os.path.exists(caminho_rotinas) or os.stat(caminho_rotinas).st_size == 0:
            print(f"[WARN] Arquivo '{caminho_rotinas}' não encontrado ou vazio. Lista de rotinas vazia.")
            return {}

        try:
            with open(caminho_rotinas, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            rotinas_dict = {}
            if "rotinas" in dados and isinstance(dados["rotinas"], list):
                rotinas_dict = {r["id"]: r for r in dados["rotinas"]}
            elif isinstance(dados, dict):
                rotinas_dict = {
                    rid: {"id": rid, "nome": r.get("nome", rid), "acoes": r.get("acoes", [])}
                    for rid, r in dados.items() if isinstance(r, dict)
                }

            print(f"[INFO] {len(rotinas_dict)} rotina(s) carregada(s).")
            return rotinas_dict

        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERRO] Falha ao ler '{caminho_rotinas}': {e}")
            return {}

    def executar_rotinas(self, id_rotina):
        rotina = self.rotinas.get(id_rotina)

        if not rotina:
            print(f"[ERRO] Rotina com o ID '{id_rotina}' não encontrada.")
            return

        comandos = rotina.get("comandos") or rotina.get("acoes") or []
        if not comandos:
            print(f"[ERRO] A rotina '{rotina['nome']}' não contém comandos/ações válidos.")
            return

        ids_invalidos = [c["id_dispositivo"] for c in comandos if not self.buscar_por_id(c["id_dispositivo"])]
        if ids_invalidos:
            print(f"[ERRO] A rotina '{rotina['nome']}' contém dispositivos inválidos: {', '.join(ids_invalidos)}")
            return

        print(f"\n---- Executando rotina: {rotina['nome']} ----")
        for comando_info in comandos:
            dispositivo_id = comando_info["id_dispositivo"]
            comando = comando_info["comando"]
            dispositivo = self.buscar_por_id(dispositivo_id)

            try:
                dispositivo.executar_comando(comando)
                print(f"> Executado '{comando}' em '{dispositivo.nome}' (ID: {dispositivo_id})")
            except Exception as e:
                print(f"> [ERRO] Falha ao executar '{comando}' em '{dispositivo.nome}': {e}")

        print("---- Rotina concluída ----")

    # -------------------------------
    # Relatórios
    # -------------------------------
    def _salvar_csv(self, nome_arquivo, fieldnames, linhas):
        pasta = os.path.dirname(nome_arquivo)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)

        try:
            with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(linhas)

            print(f"[INFO] Relatório gerado em '{nome_arquivo}'.")
        except IOError as e:
            print(f"[ERRO] Não foi possível salvar relatório: {e}")

    def gerar_relatorio(self, tipo_relatorio, nome_arquivo):
        if tipo_relatorio == "dispositivos":
            linhas = []
            for d in self.dispositivos:
                detalhes = d.detalhes()
                if d.tipo == "TOMADA":
                    extra = f"Consumo: {d.consumo_total()} Wh"
                elif d.tipo == "LUZ":
                    extra = f"Brilho: {detalhes.get('brilho', 100)} | Cor: {detalhes.get('cor', 'WHITE')}"
                else:
                    extra = ""
                linhas.append({
                    "id": detalhes.get("id"),
                    "nome": detalhes.get("nome"),
                    "tipo": detalhes.get("tipo"),
                    "estado": detalhes.get("estado"),
                    "extra_info": extra
                })
            self._salvar_csv(nome_arquivo, ["id", "nome", "tipo", "estado", "extra_info"], linhas)

        elif tipo_relatorio == "consumo_tomada":
            linhas = [
                {"id": d.id, "nome": d.nome, "consumo_wh": d.consumo_total()}
                for d in self.dispositivos if d.tipo == "TOMADA"
            ]
            self._salvar_csv(nome_arquivo, ["id", "nome", "consumo_wh"], linhas)

        else:
            print("[ERRO] Tipo de relatório inválido.")

    def _calcular_consumo_tomadas(self, eventos_log):
        return calcular_consumo_tomada(eventos_log, self.dispositivos)

    @classmethod
    def instancia(cls):
        pass
