from smart_home.core.luz import Luz, CoreRGB
from smart_home.core.porta import Porta
from smart_home.core.tomada import TomadaInteligente
from time import sleep

if __name__ =='__main__':

    ## Porta
    porta = Porta("porta_entrada")

    porta.abrir()
    print(f"Estado inicial: {porta.state}")

    porta.fechar()
    print(f"Estado após fechar: {porta.state}")

    ## Luz
    luz = Luz("luz_quarto")

    luz.ligar()
    print(f"Estado: {luz.state}") # ligada

    luz.dimerizar(50)
    print(f"Brilho: {luz.brilho}") # 50

    luz.definir_cor(CoreRGB.BLUE)
    print(f"Cor: {luz.cor.name}") # Cor azul

    luz.desligar()
    print(f"Estado final: {luz.state}") # Desliga

    ## Tomada Inteligente
    tomada = TomadaInteligente("tomada_tv", potencia_W=200)
    tomada.ligar()
    sleep(3) # tempo ligado de 2 segundos
    tomada.desligar()

    print(f"Consumo total: {tomada.consumo_total()} Wh")
