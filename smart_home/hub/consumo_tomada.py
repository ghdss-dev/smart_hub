from datetime import datetime

def calcular_consumo_tomada(eventos_log, dispositivos):

    consumos = []
    tomadas_log = {}
    tomadas_potencia = {d.id: d.potencia_W for d in dispositivos if d.tipo == 'TOMADA'}

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
