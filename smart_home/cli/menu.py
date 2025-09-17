# smart_home/cli/menu.py

import json
from smart_home.core.porta import Port
from smart_home.core.tomada import TomadaInteligente
from smart_home.hub.automacao import AutomacaoResidencial
from smart_home.core.luz import CorRGB, ValidacaoAtributo, Luz
from smart_home.core.sensor import Sensor
from smart_home.core.cafeteira import Cafeteira
from smart_home.core.persiana import Persiana
from smart_home.utils.helpers import get_full_path


def exibir_menu():

    print("\n**** SMART HOME HUB ****")
    print("1 - Listar dispositivos")
    print("2 - Mostrar dispositivo")
    print("3 - Executar comando em dispositivo")
    print("4 - Alterar atributo de dispositivo")
    print("5 - Executar rotina")
    print("6 - Gerar relatório")
    print("7 - Salvar configuração")
    print("8 - Adicionar dispositivo")
    print("9 - Remover dispositivo")
    print("10 - Sair")
    print("11 - Criar rotina")
    print("12 - Exportar eventos para CSV")


def carregar_eventos():

    caminho_eventos = get_full_path("data/eventos.json")

    try:

        with open(caminho_eventos, "r", encoding="utf-8") as f:

            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):

        return []


def salvar_eventos(eventos):

    """Salva eventos no arquivo JSON."""

    caminho_eventos = get_full_path("data/eventos.json")

    with open(caminho_eventos, "w", encoding="utf-8") as f:

        json.dump(eventos, f, indent=4, ensure_ascii=False)


def main():

    try:

        caminho_config = get_full_path("config/config_exemplo.json")

        caminho_rotinas = get_full_path("config/rotinas.json")

        automacao = AutomacaoResidencial(caminho_config, caminho_rotinas)

    except (FileNotFoundError, json.JSONDecodeError) as e:

        print(f"[ERRO] Falha ao iniciar o Smart Hub: {e}")

        return

    # eventos ficam persistidos em arquivo
    eventos_log = carregar_eventos()

    while True:

        exibir_menu()

        opcao = input("Escolha uma opção: ")

        if opcao == "1":

            print("\n--- Dispositivos ---")

            dispositivos = automacao.listar_dispositivos()

            for d in dispositivos:

                print(f"ID: {d['id']}, Nome: {d['nome']}, Tipo: {d['tipo']}, Estado: {d['estado']}")

        elif opcao == "2":

            id_dispositivo = input("Digite o ID do dispositivo: ")

            dispositivo = automacao.buscar_por_id(id_dispositivo)

            if dispositivo:

                print("\n--- Dispositivo ---")

                for chave, valor in dispositivo.detalhes().items():

                    print(f"{chave.capitalize()}: {valor}")
            else:

                print("[ERRO] Dispositivo não encontrado.")


        elif opcao == "3":

            id_dispositivo = input("Digite o ID do dispositivo: ")

            dispositivo = automacao.buscar_por_id(id_dispositivo)

            if not dispositivo:

                print("[ERRO] Dispositivo não encontrado.")

                continue

            # Mapear comandos por tipo

            comandos_por_tipo = {

                "LUZ": ["ligar", "desligar"],

                "PORTA": ["abrir", "trancar"],

                "TOMADA": ["ligar", "desligar"],

                "CAFETEIRA": ["ligar", "desligar"],

                "PERSIANA": ["abrir", "fechar", "parar"],

                "SENSOR": ["ativar", "desativar"]

            }

            comandos_validos = comandos_por_tipo.get(dispositivo.tipo, [])

            print(f"Dispositivo selecionado: {dispositivo.nome} ({dispositivo.tipo})")

            if comandos_validos:

                print(f"Comandos suportados: {', '.join(comandos_validos)}")

            comando = input("Digite o comando: ").lower()

            if comandos_validos and comando not in comandos_validos:

                print(f"[ERRO] Comando inválido para {dispositivo.tipo}.")

                continue

            try:

                dispositivo.executar_comando(comando)

                # cria evento e adiciona no log

                evento = {

                    "id_dispositivo": id_dispositivo,

                    "evento": comando,

                    "timestamp": dispositivo.ultimo_evento.isoformat() if hasattr(dispositivo,"ultimo_evento") else "N/A"
                }

                eventos_log.append(evento)

                salvar_eventos(eventos_log)

                print(f"[INFO] Comando '{comando}' executado em '{dispositivo.nome}'.")

            except Exception as e:

                print(f"[ERRO] Falha ao executar comando: {e}")

        elif opcao == "4":

            id_dispositivo = input("Digite o ID do dispositivo: ")

            dispositivo = automacao.buscar_por_id(id_dispositivo)

            if not dispositivo:

                print("[ERRO] Dispositivo não encontrado.")

                continue

            print(f"Dispositivo selecionado: {dispositivo.nome} ({dispositivo.tipo})")

            # pega os detalhes e decide dinamicamente o que pode ser editado
            detalhes = dispositivo.detalhes()

            nao_editaveis = {"id", "nome", "tipo", "estado", "consumo_wh", "ultimo_ativado", "periodo_inicio", "periodo_fim"}

            atributos_validos = [k for k, v in detalhes.items() if k not in nao_editaveis]

            if not atributos_validos:

                print(f"[INFO] Nenhum atributo editável disponível para {dispositivo.tipo}.")

                continue

            print(f"Atributos disponíveis: {', '.join(atributos_validos)}")

            atributo = input("Qual atributo deseja alterar?: ").strip()

            if atributo not in atributos_validos:

                print("[ERRO] Atributo inválido.")

                continue

            novo_valor_raw = input("Digite o novo valor: ").strip()

            # converte para o tipo do valor atual (int/float/bool/str) se possível

            valor_atual = detalhes.get(atributo)

            novo_valor = novo_valor_raw

            try:

                if isinstance(valor_atual, int):

                    novo_valor = int(novo_valor_raw)

                elif isinstance(valor_atual, float):

                    novo_valor = float(novo_valor_raw)

                elif isinstance(valor_atual, bool):

                    novo_valor = novo_valor_raw.lower() in ("1", "true", "t", "sim", "s", "yes", "y")

                else:

                    # string ou None → manter string

                    novo_valor = novo_valor_raw
            except ValueError:

                print(f"[ERRO] Tipo inválido para '{atributo}'. Esperado {type(valor_atual).__name__}.")

                continue

            # Caso especial: cor (enum)

            try:

                if atributo == "cor":

                    # exige que CorRGB tenha from_str
                    novo_enum = CorRGB.from_str(novo_valor_raw, CorRGB.WHITE)

                    dispositivo.cor = novo_enum

                    print(f"[INFO] Cor da luz alterada para {novo_enum.name}")

                else:

                    # tenta setar atributo direto — nome do campo no detalhes deve coincidir com o atributo do objeto

                    if hasattr(dispositivo, atributo):

                        setattr(dispositivo, atributo, novo_valor)

                        print(f"[INFO] Atributo '{atributo}' alterado para {novo_valor}.")

                    else:
                        # fallback: alguns dispositivos guardam em atributos com outro nome (ex.: potencia_W vs potencia)
                        # tenta mapear common cases:

                        mappings = {

                            "potencia_W": "potencia_W",
                            "brilho": "brilho",
                            "potencia": "potencia_W"
                        }

                        mapped = mappings.get(atributo)

                        if mapped and hasattr(dispositivo, mapped):

                            setattr(dispositivo, mapped, novo_valor)

                            print(f"[INFO] Atributo '{mapped}' alterado para {novo_valor}.")

                        else:

                            print(f"[ERRO] Não foi possível alterar '{atributo}' — atributo interno não encontrado.")

            except Exception as e:

                print(f"[ERRO] Falha ao alterar atributo: {e}")

        elif opcao == "5":

            if not automacao.rotinas:

                print("[INFO] Nenhuma rotina encontrada.")

            else:

                print("\n--- Rotinas ---")

                for rotina_id, rotina in automacao.rotinas.items():

                    print(f"ID: {rotina_id}, Nome: {rotina['nome']}")

                id_rotina = input("Digite o ID da rotina: ")

                automacao.executar_rotinas(id_rotina)

        elif opcao == "6":

            nome_arquivo = input("Digite o nome do relatório (ex: consumo.csv): ")

            caminho_relatorio = get_full_path(f"data/{nome_arquivo}")

            automacao.gerar_relatorio("dispositivos", caminho_relatorio)

        elif opcao == "7":

            automacao.salvar_dispositivos(get_full_path("config/config_exemplo.json"))

        elif opcao == "8":

            print("Tipos disponíveis: luz, porta, tomada, cafeteira, persiana, sensor")

            tipo = input("Tipo de dispositivo: ").lower()

            id_dispositivo = input("Digite o ID: ")

            nome = input("Digite o nome: ")

            if tipo == "luz":

                novo = Luz(id_dispositivo, nome)

            elif tipo == "porta":

                novo = Port(id_dispositivo, nome)

            elif tipo == "tomada":

                potencia = int(input("Digite a potência (W): "))

                novo = TomadaInteligente(id_dispositivo, nome, potencia_W=potencia)

            elif tipo == "cafeteira":

                novo = Cafeteira(id_dispositivo, nome)

            elif tipo == "persiana":

                novo = Persiana(id_dispositivo, nome)

            elif tipo == "sensor":

                novo = Sensor(id_dispositivo, nome)

            else:

                print("[ERRO] Tipo inválido.")

                continue

            automacao.adicionar_dispostivo(novo)

        elif opcao == "9":

            id_dispositivo = input("Digite o ID do dispositivo: ")

            automacao.remover_dispositivo(id_dispositivo)

        elif opcao == "10":
            print("Saindo...")
            break

        elif opcao == "11":

            print("\n--- Criar Nova Rotina ---")

            id_rotina = input("Digite o ID da rotina: ")

            nome_rotina = input("Digite o nome da rotina: ")

            acoes = []

            while True:

                id_disp = input("Digite o ID do dispositivo (ou ENTER para parar): ")

                if not id_disp:

                    break

                comando = input("Digite o comando (ex: ligar, desligar, abrir, trancar): ")

                acoes.append({"id_dispositivo": id_disp, "comando": comando})

            if not acoes:

                print("[ERRO] Nenhuma ação adicionada à rotina.")

            else:

                automacao.rotinas[id_rotina] = {

                    "nome": nome_rotina,
                    "acoes": acoes
                }

                caminho_rotinas = get_full_path("config/rotinas.json")

                with open(caminho_rotinas, "w", encoding="utf-8") as f:

                    json.dump(automacao.rotinas, f, indent=4, ensure_ascii=False)

                print(f"[INFO] Rotina '{nome_rotina}' criada e salva em rotinas.json.")

        elif opcao == "12":

            if not eventos_log:

                print("[INFO] Nenhum evento registrado até agora.")

            else:

                nome_arquivo = input("Digite o nome do arquivo CSV (ex: eventos.csv): ")

                caminho_csv = get_full_path(f"data/{nome_arquivo}")

                automacao.exportar_eventos_csv(eventos_log, caminho_csv)

        else:

            print("[ERRO] Opção inválida.")


if __name__ == "__main__":

    main()
