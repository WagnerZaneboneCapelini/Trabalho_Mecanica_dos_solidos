from indeterminatebeam import Beam, Support, PointLoadV, PointTorque, DistributedLoadV, PointLoadH
from sympy.abc import L, E, I, x
import matplotlib.pyplot as plt
from math import pi, sqrt
import numpy as np


def create_beam():
    # Solicitando as informações ao usuário
    material = int(input("\nLista de materiais\n"
                         "1 - Aço\n"
                         "2 - Aluminio\n"
                         "3 - Vidro\n"
                         "4 - Concreto\n"
                         "5 - Madeira\n"
                         "6 - Poliestireno\n"
                         "7 - Outro\n"
                         'Digite o tipo do material da viga: '))

    if material == 1:
        E = 200*10**9
    elif material == 2:
        E = 70*10**9
    elif material == 3:
        E = 65*10**9
    elif material == 4:
        E = 30*10**9
    elif material == 5:
        E = 13*10**9
    elif material == 6:
        E = 3*10**9
    elif material == 7:
        E = int(input(f'Digite o valor do módulo de elasticidade do material: '))
    tipo_viga = int(input('1 - I\n'
                          '2 - T\n'
                          '3 - C\n'
                          '4 - Circular\n'
                          '5 - Retangular\n'
                          'Digite o tipo de viga:\n'))

    # Definindo momento de inercia
    def m_inercia(yc, yc_aba, l, h):
        if tipo_viga != 4:
            m = (l * h * 3) / 12 + l * h + (yc - yc_aba) * 2
        else:  # Caso de viga circular
            m = (pi * yc ** 4) / 4
        return m

    # Solicitando informações específicas para viga
    if tipo_viga == 1 or tipo_viga == 2 or tipo_viga == 3:
        h_cen = float(
            input(f'Digite a altura do centro da seção transversal em metros: '))
        l_cen = float(
            input(f'Digite a largura do centro da seção transversal em metros: '))
        h_sup = float(
            input(f'Digite a altura da aba da seção transversal em metros: '))
        l_sup = float(
            input(f'Digite a largura da aba da seção transversal em metros: '))
        if tipo_viga == 1 or tipo_viga == 3:
            h_base = h_sup
            l_base = l_sup
        else:
            h_base, l_base = 0, 0

    # Solicitando informações específicas para viga circular
    elif tipo_viga == 4:
        raio = float(input(f'Digite o raio da seção circular em metros: '))

    # Solicitando informações específicas para viga retangular
    elif tipo_viga == 5:
        h_cen = float(
            input(f'Digite a altura da seção transversal retangular em metros: '))
        l_cen = float(
            input(f'Digite a largura da seção transversal retangular em metros: '))
        h_base, l_base, h_sup, l_sup = 0, 0, 0, 0

    else:
        print("Opção inválida.")

    # Cálculo do centroide
    if tipo_viga != 4:
        yc_sup = h_base + h_cen + h_sup / 2
        yc_cen = h_cen / 2 + h_base
        yc_inf = h_base / 2
        yc = (yc_sup * (h_sup * l_sup) + yc_cen * (h_cen * l_cen) + yc_inf * (h_base * l_base)) / (
            (h_sup * l_sup) + (h_cen * l_cen) + (h_base * l_base))
        A = (h_sup * l_sup) + (h_cen * l_cen) + (h_base * l_base)
        I = m_inercia(yc, yc_inf, l_base, h_base) + m_inercia(yc, yc_cen, l_cen, h_cen) + m_inercia(yc, yc_sup, l_sup,
                                                                                                    h_sup)
    else:
        yc = raio
        I = m_inercia(raio, raio, raio, raio)
        A = pi * raio ** 2

    L = float(input(f'Digite o comprimento da viga: '))
    viga = Beam(L, E, I, A)

    novo_apoio = "s"
    while novo_apoio == "s":
        tipo = int(input('1 - Engaste\n'
                         '2 - Fixo\n'
                         '3 - Rolete\n'
                         'Digite o tipo de apoio da viga:\n'))
        posicao = int(input('Digite a localização do apoio: '))

        if tipo == 1:  # Engaste
            if posicao == 0 or posicao == L:
                viga.add_supports(Support(posicao, (1, 1, 1)))
            else:
                print('Posição inválida para viga engastada, tente novamente')
                continue
        elif tipo == 2:  # Fixo
            viga.add_supports(Support(posicao, (1, 1, 0)))
        elif tipo == 3:  # Rolete
            viga.add_supports(Support(posicao, (0, 1, 0)))
        else:
            print('Tipo de apoio inválido, tente novamente')
            continue

        novo_apoio = input('Deseja adicionar um novo apoio? (s/n): ')

    num_cargas_concentradas = int(
        input(f'Digite o número de cargas concentradas: '))
    for i in range(num_cargas_concentradas):
        carga = float(input(f'Digite o valor da carga concentrada {i + 1}: '))
        posicao = float(
            input(f'Digite a posição da carga concentrada {i + 1}: '))
        viga.add_loads(PointLoadV(carga, posicao))

    num_momentos = int(input(f'Digite o número de momentos aplicados: '))
    for i in range(num_momentos):
        momento = float(input(f'Digite o valor do momento aplicado: '))
        posicao = float(input(f'Digite a posição do momento aplicado: '))
        viga.add_loads(PointTorque(momento, posicao))

    num_cargas_distribuidas = int(
        input("Digite o número de cargas distribuídas: "))
    for i in range(num_cargas_distribuidas):
        pos_ini = float(
            input(f'Digite a posição inicial da carga distribuída: '))
        pos_fim = float(
            input(f'Digite a posição final da carga distribuída: '))

        tipo = int(input(f'Digite tipo de carga distribuída:\n'
                         '1 - Uniforme\n'
                         '2 - linear\n'
                         '3 - parabólica\n'))

        if tipo == 1:
            c = float(
                input(f'Digite a magnitude da carga distribuída {i + 1}: '))
            # a, b = 0, 0
            viga.add_loads(DistributedLoadV(c, (pos_ini, pos_fim)))
        elif tipo == 2:
            mag1 = float(
                input(f'Digite o y inicial da carga distribuída {i + 1}: '))
            mag2 = float(
                input(f'Digite o y final da carga distribuída {i + 1}: '))
            b = (mag2 - mag1) / (pos_fim - pos_ini)
            c = (-pos_ini * b) + pos_fim
            # a = 0
            viga.add_loads(DistributedLoadV(
                expr=b * x + c, span=(pos_ini, pos_fim)))
        else:
            a = float(input(f'Digite o coeficiente a da função parabólica: '))
            b = float(input(f'Digite o coeficiente b da função parabólica: '))
            c = float(input(f'Digite o coeficiente c da função parabólica: '))
            viga.add_loads(DistributedLoadV(expr=a * x ** 2 +
                           b * x + c, span=(pos_ini, pos_fim)))

    viga.analyse()
    while True:
        print('1 - Diagrama de momento fletor\n'
              '2 - Diagrama de forças internas e externas\n'
              '3 - Diagrama de Deflexão ao longo da viga\n'
              '4 - Valores em um ponto x específico ao longo da viga:\n'
              '5 - Voltar para o menu inicial\n')
        opcao = int(input('Escolha uma opção acima: '))
        if opcao == 1:
            fig_1 = viga.plot_shear_force()
            fig_1.show()
        elif opcao == 2:
            fig_1 = viga.plot_beam_external()
            fig_1.show()
            fig_2 = viga.plot_beam_internal()
            fig_2.show()
        elif opcao == 3:
            fig_1 = viga.plot_deflection()
            fig_1.show()
        elif opcao == 4:
            print('1 - Esforço cortante\n'
                  '2 - Deflexão\n'
                  '3 - Momento fletor\n'
                  '4 - Valores máximos e mínimos\n'
                  '5 - Voltar para o menu anterior\n')
            opcao2 = int(input('Escolha uma das opções acima: '))
            x1 = float(
                input(f'Digite o valor da cordenada x ao longo da viga: '))
            if opcao2 == 1:
                t = viga.get_shear_force(x1)
                print(f'Esforço cortante no ponto {x1} da viga: {t} N')
            elif opcao2 == 2:
                d = viga.get_deflection(x1)
                print(f'Deflexão no ponto {x1} da viga: {d} m')
            elif opcao2 == 3:
                v = viga.get_bending_moment(x1)
                print(f'Momento fletor no ponto {x1} da viga: {v} N.m')
            elif opcao2 == 4:
                print(
                    f'\nA maior força cortante em módulo foi de: {viga.get_shear_force(return_absmax=True)} N')
                print(
                    f'O maior momento fletor em módulo foi de: {viga.get_bending_moment(return_absmax=True)} N.m')
                print(
                    f'A maior deflexão em módulo foi de: {viga.get_deflection(return_absmax=True)} m\n')

            elif opcao2 == 5:
                break
            else:
                print("Opção inválida. Tente novamente.")
        elif opcao == 5:
            break
        else:
            print("Opção inválida. Tente novamente.")


def exemplos():
    validacao = 1
    print(" Exercicios disponíveis do capítulo 6 de resistencia dos materiais: ")
    print(" 1 - 2 - 3 - 4 - 5 - 6 - 7 - 8 - 9 - 10")
    num_exemplo = int(input("Escolha um exercício: "))

    if num_exemplo == 1:
        L = 1.050
        viga = Beam(L)
        viga.add_supports(Support(0.25, (1, 1, 0)))
        viga.add_supports(Support(1.05, (1, 1, 0)))
        viga.add_loads(PointLoadV(-24000, 0))

    elif num_exemplo == 2:
        L = 0.375
        viga = Beam(L)
        viga.add_supports(Support(0.3, (1, 1, 0)))
        viga.add_supports(Support(0.375, (1, 1, 0)))
        viga.add_loads(PointLoadV(-250, 0))

    elif num_exemplo == 3:
        L = 1.525
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(1.225, (1, 1, 0)))
        viga.add_loads(PointLoadV(-400, 0.35))
        viga.add_loads(PointLoadV(-550, 0.85))
        viga.add_loads(PointLoadV(-175, 1.525))

    elif num_exemplo == 4:
        L = 5
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(5, (1, 1, 0)))
        viga.add_loads(PointLoadV(-10000, 1))
        viga.add_loads(PointLoadV(-10000, 2))
        viga.add_loads(PointLoadV(-10000, 3))
        viga.add_loads(PointLoadV(-10000, 4))

    elif num_exemplo == 5:
        L = 7
        viga = Beam(L)
        viga.add_supports(Support(1, (1, 1, 0)))
        viga.add_supports(Support(6, (1, 1, 0)))
        viga.add_loads(PointLoadV(-60000, 0))
        viga.add_loads(PointLoadV(-60000, 7))
        viga.add_loads(PointLoadV(-35000, 2))
        viga.add_loads(PointLoadV(-35000, 3.5))
        viga.add_loads(PointLoadV(-35000, 5))

    elif num_exemplo == 6:
        L = 0.8
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(0.8, (1, 1, 0)))
        viga.add_loads(PointLoadV(-800, 0.125))
        viga.add_loads(PointLoadV(-1500, 0.725))
        print("\nV (0.125 < x < 0.725) = 15.625 N")
        a = (111.328-101.953)/(0.725-0.125)
        b = 101.953-a*0.125
        print("M (0.125 < x < 0.725) = ", a, "* x +", b, "N.m\n")

    elif num_exemplo == 7:
        L = 1.95
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(1.5, (1, 1, 0)))
        viga.add_loads(PointLoadV(-4000, 0.9))
        viga.add_loads(PointLoadV(-2500, 1.95))

    elif num_exemplo == 8:
        L = 0.4
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(0.4, (1, 1, 0)))
        viga.add_loads(PointLoadH(-5000, 0))
        viga.add_loads(PointTorque(-5000*0.08, 0.4))

    elif num_exemplo == 9:
        L = 3
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(3, (0, 1, 0)))
        viga.add_loads(PointLoadV(-75000, 1))
        viga.add_loads(PointLoadH(-100000, 2))
        viga.add_loads(PointTorque(100000*0.25, 2))

    elif num_exemplo == 10:
        L = 2.4
        viga = Beam(L)
        viga.add_supports(Support(0, (1, 1, 0)))
        viga.add_supports(Support(0.9, (0, 1, 0)))
        viga.add_loads(PointLoadV(-6000, 2.4))

    else:
        validacao = 0
        print("Opção indisponivel\n")

    if validacao == 1:
        print("Devido a falta de informações do exercicio, os valores de A, I e E foram definidos para:")
        print("| A=0.23 | I=9.05 * 10^-6 | E=2 * 10^11 |\n")

        viga.analyse()
        fig_1 = viga.plot_beam_external()
        fig_1.show()

        fig_2 = viga.plot_beam_internal()
        fig_2.show()

        print(
            f"A maior força cortante em módulo foi de: {viga.get_shear_force(return_absmax=True)} N")
        print(
            f"O maior momento fletor em módulo foi de: {viga.get_bending_moment(return_absmax=True)} N.m\n")


def menu():
    while True:
        print("----- Análise de Viga -----")
        print("1. Criar uma nova viga")
        print("2. Simular exercicios do livro (Recomendado)")
        print("3. Sair\n")
        print("OBS: Respostas serão plotadas no navegador de internet\n")
        choice = input("Escolha uma opção: ")

        if choice == "1":
            create_beam()
        elif choice == "2":
            exemplos()
        elif choice == "3":
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
