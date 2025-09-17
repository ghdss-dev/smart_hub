import json
import os
import csv
from datetime import datetime
from smart_home.core.porta import Port
from smart_home.core.luz import Luz, CorRGB
from smart_home.core.tomada import TomadaInteligente
from smart_home.hub.singleton import Singleton
from smart_home.hub.eventos import Evento

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

class AutomacaoResidencial(Singleton):

    def __init__(self, caminho_config, caminho_rotinas):

        if not hasattr(self, '_inicializado'):
            self._caminho_config = caminho_config
            self._caminho_rotinas = caminho_rotinas
            self.dispositivos = self.carregar_dispositivos(caminho_config)
            self.rotinas = self.carregar_rotinas(caminho_rotinas)
            self.observers = []  # corrigido
            self._carregar_observers()  # inicializa observers das rotinas
            self._inicializado = True
    # -------------------------------
    # Dispositivos
    # -------------------------------
    def carregar_dispositivos(self, caminho_json):
        if not os.path.exists(caminho_json) or os.stat(caminho_json).st_size == 0:
            print(f"[WARN] Arquivo de configuracao '{caminho_json}' nao encontrado ou esta vazio. Iniciando com uma lista de dispositivos vazia.")
            return []

        try:
            with open(caminho_json, 'r') as f:
                dados = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERRO] Falha ao decodificar o arquivo de configuracao '{caminho_json}': {e}")
            return []

        dispositivos_config = dados.get('dispositivos', [])
        dispositivos = []

        for d in dispositivos_config:
            tipo = d['tipo']
            nome = d.get('nome', 'Sem Nome')

            try:
                tipos_dispositivos = {
                    'PORTA': Port,
                    'LUZ': Luz,
                    'TOMADA': TomadaInteligente,
                }

                if tipo in tipos_dispositivos:
                    if tipo == 'LUZ':
                        atributos = d.get('atributos', {})
                        cor_str = atributos.get('cor', 'WHITE')
                        brilho = atributos.get('brilho', 100)
                        cor = CorRGB[cor_str]
                        dispositivo = Luz(d['id'], nome, brilho=brilho, cor=cor)

                    elif tipo == 'TOMADA':
                        atributos = d.get('atributos', {})
                        potencia = atributos.get('potencia_W', 100)
                        dispositivo = TomadaInteligente(d['id'], nome, potencia_W=potencia)

                    else:
                        dispositivo = tipos_dispositivos[tipo](d['id'], nome)

                    estado_inicial = d.get('estado')
                    if estado_inicial and estado_inicial != dispositivo.state:
                        dispositivo.executar_comando(estado_inicial)

                    dispositivos.append(dispositivo)
                else:
                    print(f"[WARN] Tipo de dispositivo desconhecido: {tipo}")

            except Exception as e:
                print(f"[ERRO] Não foi possível carregar o dispositivo '{nome}' (ID: {d.get('id')}): {e}")

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

        dispositivos_para_salvar = []

        if self.dispositivos:

            for d in self.dispositivos:

                dados_dispositivo = d.detalhes()
                dispositivos_para_salvar.append(dados_dispositivo)

        dados_config = {"dispositivos": dispositivos_para_salvar}

        try:

            with open(caminho_json, 'w', encoding='utf-8') as f:

                json.dump(dados_config, f, indent=4)

            print(f"[INFO] Configuracao salva com sucesso em '{caminho_json}'.")

        except IOError as e:

            print(f"[ERRO] Nao foi possivel salvar o arquivo: {e}")

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

    # -------------------------------
    # Rotinas
    # -------------------------------
    def carregar_rotinas(self, caminho_rotinas):

        if not os.path.exists(caminho_rotinas) or os.stat(caminho_rotinas).st_size == 0:
            print(
                f"[WARN] Arquivo de rotinas '{caminho_rotinas}' nao encontrado ou esta vazio. Iniciando com uma lista de rotinas vazia.")
            return {}

        try:
            with open(caminho_rotinas, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            rotinas_dict = {}


            if "rotinas" in dados and isinstance(dados["rotinas"], list):
                rotinas_dict = {r["id"]: r for r in dados["rotinas"]}


            elif isinstance(dados, dict):
                for rid, r in dados.items():
                    if isinstance(r, dict):
                        rotinas_dict[rid] = {
                            "id": rid,
                            "nome": r.get("nome", rid),
                            "acoes": r.get("acoes", [])
                        }

            print(f"[INFO] {len(rotinas_dict)} rotina(s) carregada(s) com sucesso.")
            return rotinas_dict

        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERRO] Falha ao ler o arquivo de rotinas: {e}")
            return {}

    def executar_rotinas(self, id_rotina):
        rotina = self.rotinas.get(id_rotina)

        if not rotina:
            print(f"[ERRO] Rotina com o ID '{id_rotina}' nao encontrada.")
            return

        # Aceitar tanto 'comandos' quanto 'acoes'
        comandos = rotina.get("comandos") or rotina.get("acoes") or []

        if not comandos:
            print(f"[ERRO] A rotina '{rotina['nome']}' não contém comandos/ações válidos.")
            return

        # Verificar dispositivos inexistentes
        ids_invalidos = [c["id_dispositivo"] for c in comandos if not self.buscar_por_id(c["id_dispositivo"])]

        if ids_invalidos:
            print(
                f"[ERRO] A rotina '{rotina['nome']}' contém dispositivos que não existem no sistema: {', '.join(ids_invalidos)}")
            return

        print(f"\n ---- Executando rotina: {rotina['nome']}")

        for comando_info in comandos:
            dispositivo_id = comando_info["id_dispositivo"]
            comando = comando_info["comando"]
            dispositivo = self.buscar_por_id(dispositivo_id)

            try:
                dispositivo.executar_comando(comando)
                print(f"> Executado '{comando}' em '{dispositivo.nome}' (ID: {dispositivo_id})")
            except Exception as e:
                print(f"> [ERRO] Falha ao executar '{comando}' em '{dispositivo.nome}': {e}")

        print("--- Rotina concluida ----")

    def listar_dispositivos(self):
        if self.dispositivos:
            return [d.detalhes() for d in self.dispositivos]
        return []

    def buscar_por_id(self, id_dispositivo):
        if self.dispositivos:
            for d in self.dispositivos:
                if d.id == id_dispositivo:
                    return d
        return None

    def gerar_relatorio(self, tipo_relatorio, nome_arquivo):

        # garante que a pasta exista
        pasta = os.path.dirname(nome_arquivo)
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)

        try:
            if tipo_relatorio == "dispositivos":
                fieldnames = ["id", "nome", "tipo", "estado", "extra_info"]
                with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for dispositivo in self.dispositivos:  # percorre lista
                        detalhes = dispositivo.detalhes()

                        if dispositivo.tipo == "TOMADA":
                            extra_info = f"Consumo: {dispositivo.consumo_total()} Wh"
                        elif dispositivo.tipo == "LUZ":
                            extra_info = f"Brilho: {detalhes.get('brilho', 100)} | Cor: {detalhes.get('cor', 'WHITE')}"
                        else:
                            extra_info = ""

                        writer.writerow({
                            "id": detalhes.get("id"),
                            "nome": detalhes.get("nome"),
                            "tipo": detalhes.get("tipo"),
                            "estado": detalhes.get("estado"),
                            "extra_info": extra_info
                        })

            elif tipo_relatorio == "consumo_tomada":
                fieldnames = ["id", "nome", "consumo_wh"]
                with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for dispositivo in self.dispositivos:
                        if dispositivo.tipo == "TOMADA":
                            writer.writerow({
                                "id": dispositivo.id,
                                "nome": dispositivo.nome,
                                "consumo_wh": dispositivo.consumo_total()
                            })

            else:
                print("[ERRO] Tipo de relatório inválido.")
                return

            print(f"[INFO] Relatório gerado em '{nome_arquivo}'.")

        except IOError as e:
            print(f"[ERRO] Não foi possível salvar relatório: {e}")

    def _calcular_consumo_tomadas(self, eventos_log):
        consumos = []
        tomadas_log = {}
        tomadas_potencia = {d.id: d.potencia_W for d in self.dispositivos if d.tipo == 'TOMADA'}

        if not tomadas_potencia:
            print("[INFO] Nao ha tomadas cadastradas para gerar o relatorio.")
            return []

        for evento in eventos_log:
            id_dispositivo = evento.get('id_dispositivo')
            if id_dispositivo in tomadas_potencia:
                if evento['evento'] == 'ligar':
                    tomadas_log[id_dispositivo] = datetime.fromisoformat(evento['timestamp'])
                elif evento['evento'] == 'desligar' and id_dispositivo in tomadas_log:
                    inicio = tomadas_log.pop(id_dispositivo)
                    fim = datetime.fromisoformat(evento['timestamp'])
                    duracao_h = (fim - inicio).total_seconds() / 3600
                    potencia = tomadas_potencia[id_dispositivo]
                    consumo_wh = potencia * duracao_h
                    consumos.append({
                        'id_dispositivo': id_dispositivo,
                        'total_wh': round(consumo_wh, 2),
                        'periodo_inicio': inicio.isoformat(),
                        'periodo_fim': fim.isoformat()
                    })

        return consumos

    @classmethod
    def instancia(cls, caminho_config=None, caminho_rotinas=None):

        return cls(caminho_config, caminho_rotinas)

    def _carregar_observers(self):

        """
        Cria observers para cada rotina do JSON e registra no hub
        """
        for rid, regra in self.rotinas.items():
            observer = RotinaObserver(regra, {d.id: d for d in self.dispositivos})
            self.registrar_observer(observer)
