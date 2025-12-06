#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GERADOR DE JOGOS MEGA-SENA
Interface simplificada para gerar múltiplos jogos
"""

from megasena_otimizado import MegaSenaAnalytics
from datetime import datetime
import sys
import argparse

def banner():
    print("\n" + "="*70)
    print("🎲 GERADOR DE JOGOS MEGA-SENA - IA + ESTATÍSTICA")
    print("="*70)

def menu_principal():
    print("\n📋 MÉTODOS DISPONÍVEIS:")
    print("1. Método Híbrido (Recomendado) - Combina todas as técnicas")
    print("2. Método Caravaca - Baseado no dia/mês")
    print("3. Método Estatístico - Baseado em frequências históricas")
    print("4. Método IA Avançado - Machine Learning")
    print("5. Comparar todos os métodos")
    print("6. Sair")
    
    while True:
        try:
            opcao = input("\n👉 Escolha uma opção (1-6): ").strip()
            if opcao in ['1', '2', '3', '4', '5', '6']:
                return opcao
            else:
                print("❌ Opção inválida! Digite um número de 1 a 6.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Operação cancelada.")
            sys.exit(0)

def obter_quantidade():
    while True:
        try:
            qtd = input("\n🎯 Quantos jogos deseja gerar? (1-20): ").strip()
            if not qtd.isdigit():
                print("❌ Digite um número válido!")
                continue
                
            qtd = int(qtd)
            if 1 <= qtd <= 20:
                return qtd
            else:
                print("❌ Quantidade deve ser entre 1 e 20!")
        except KeyboardInterrupt:
            print("\n\n⚠️  Operação cancelada.")
            sys.exit(0)

def gerar_jogos(opcao, quantidade):
    """Gera jogos baseado na opção escolhida"""
    otimizador = MegaSenaAnalytics()
    
    metodos = {
        '1': ('Híbrido', 'hibrido'),
        '2': ('Caravaca', 'caravaca'),
        '3': ('Estatístico', 'estatistico'),
        '4': ('IA Avançado', 'ia')
    }
    
    if opcao == '5':
        # Comparar todos os métodos
        print("\n" + "="*70)
        print("🔍 COMPARAÇÃO DE TODOS OS MÉTODOS (2 jogos cada)")
        print("="*70)
        
        resultados = {}
        for nome, metodo in metodos.values():
            try:
                if metodo == 'caravaca':
                    jogos = [otimizador.metodo_caravaca() for _ in range(2)]
                elif metodo == 'estatistico':
                    jogos = otimizador.metodo_estatistico(2)
                elif metodo == 'ia':
                    jogos = otimizador.metodo_ia_avancado(2)
                else:  # hibrido
                    jogos = otimizador.metodo_hibrido(2)
                
                resultados[nome] = jogos
                
                print(f"\n✅ {nome.upper()}:")
                for i, jogo in enumerate(jogos, 1):
                    soma = sum(jogo)
                    altos = sum(1 for n in jogo if n >= 35)
                    print(f"   Jogo {i}: {', '.join(f'{n:2d}' for n in jogo)} "
                          f"(Soma: {soma:3d}, Altos: {altos})")
                    
            except Exception as e:
                print(f"\n❌ {nome}: Erro - {e}")
        
        # Salvar comparação
        salvar = input("\n💾 Salvar comparação em arquivo? (s/n): ")
        if salvar.lower() == 's':
            salvar_resultados(resultados, 'comparacao')
        
        return resultados
    
    else:
        # Gerar jogos de um método específico
        nome_metodo, metodo = metodos[opcao]
        
        print(f"\n{'='*70}")
        print(f"🎰 GERANDO {quantidade} JOGOS - MÉTODO {nome_metodo.upper()}")
        print(f"{'='*70}")
        
        try:
            if metodo == 'caravaca':
                jogos = [otimizador.metodo_caravaca() for _ in range(quantidade)]
            elif metodo == 'estatistico':
                jogos = otimizador.metodo_estatistico(quantidade)
            elif metodo == 'ia':
                jogos = otimizador.metodo_ia_avancado(quantidade)
            else:  # hibrido
                jogos = otimizador.metodo_hibrido(quantidade)
            
            # Exibir jogos
            print(f"\n{'Nº':^4} {'Jogo':^45} {'Soma':^6} {'Altos':^6} {'P/I':^6}")
            print("-"*70)
            
            for i, jogo in enumerate(jogos, 1):
                soma = sum(jogo)
                altos = sum(1 for n in jogo if n >= 35)
                pares = sum(1 for n in jogo if n % 2 == 0)
                impares = 6 - pares
                
                numeros_str = ', '.join(f'{n:2d}' for n in jogo)
                print(f"{i:^4} {numeros_str:^45} {soma:^6} {altos:^6} {pares}/{impares}")
            
            # Estatísticas
            print("\n" + "="*70)
            print("📊 ESTATÍSTICAS DOS JOGOS GERADOS:")
            print("="*70)
            
            todas_somas = [sum(jogo) for jogo in jogos]
            todos_altos = [sum(1 for n in jogo if n >= 35) for jogo in jogos]
            
            print(f"• Soma média: {sum(todas_somas)/len(todas_somas):.1f}")
            print(f"• Média de números altos: {sum(todos_altos)/len(todos_altos):.1f}")
            print(f"• Soma mínima: {min(todas_somas)}")
            print(f"• Soma máxima: {max(todas_somas)}")
            
            # Números mais frequentes nos jogos gerados
            todos_numeros = []
            for jogo in jogos:
                todos_numeros.extend(jogo)
            
            from collections import Counter
            contagem = Counter(todos_numeros)
            
            print(f"\n• Números mais frequentes nos jogos:")
            print("  ", end="")
            for num, freq in contagem.most_common(10):
                print(f"{num:2d}({freq}) ", end="")
            print()
            
            # Salvar em arquivo
            salvar = input("\n💾 Salvar estes jogos em arquivo? (s/n): ")
            if salvar.lower() == 's':
                salvar_resultados({nome_metodo: jogos}, metodo)
            
            return jogos
            
        except Exception as e:
            print(f"❌ Erro ao gerar jogos: {e}")
            import traceback
            traceback.print_exc()
            return None

def salvar_resultados(resultados, metodo):
    """Salva os resultados em arquivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jogos_{metodo}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("JOGOS MEGA-SENA GERADOS POR IA/ESTATÍSTICA\n")
            f.write("="*60 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Método: {metodo}\n\n")
            
            if isinstance(resultados, dict):
                for metodo_nome, jogos in resultados.items():
                    f.write(f"{metodo_nome.upper()}:\n")
                    for i, jogo in enumerate(jogos, 1):
                        soma = sum(jogo)
                        altos = sum(1 for n in jogo if n >= 35)
                        f.write(f"  Jogo {i:2d}: {', '.join(f'{n:2d}' for n in jogo)} "
                               f"(Soma: {soma:3d}, Altos: {altos})\n")
                    f.write("\n")
            else:
                f.write(f"JOGOS:\n")
                for i, jogo in enumerate(resultados, 1):
                    soma = sum(jogo)
                    altos = sum(1 for n in jogo if n >= 35)
                    f.write(f"Jogo {i:2d}: {', '.join(f'{n:2d}' for n in jogo)} "
                           f"(Soma: {soma:3d}, Altos: {altos})\n")
        
        print(f"✅ Jogos salvos em: {filename}")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")

def modo_linha_comando():
    """Modo linha de comando com argumentos"""
    parser = argparse.ArgumentParser(description='Gerador de jogos Mega-Sena')
    parser.add_argument('-m', '--metodo', choices=['hibrido', 'caravaca', 'estatistico', 'ia', 'todos'],
                       default='hibrido', help='Método de geração (padrão: hibrido)')
    parser.add_argument('-q', '--quantidade', type=int, default=5,
                       help='Quantidade de jogos (padrão: 5)')
    parser.add_argument('-o', '--output', help='Arquivo de saída')
    parser.add_argument('-a', '--analise', action='store_true',
                       help='Mostrar análise completa')
    
    return parser.parse_args()

def main():
    """Função principal"""
    
    # Verificar se há argumentos de linha de comando
    if len(sys.argv) > 1:
        args = modo_linha_comando()
        
        otimizador = MegaSenaAnalytics()
        
        if args.analise:
            otimizador.gerar_relatorio()
        
        if args.metodo == 'todos':
            # Gerar com todos os métodos
            metodos = [('hibrido', 'Híbrido'), ('caravaca', 'Caravaca'),
                      ('estatistico', 'Estatístico'), ('ia', 'IA')]
            
            resultados = {}
            for metodo, nome in metodos:
                try:
                    if metodo == 'caravaca':
                        jogos = [otimizador.metodo_caravaca() for _ in range(args.quantidade)]
                    elif metodo == 'estatistico':
                        jogos = otimizador.metodo_estatistico(args.quantidade)
                    elif metodo == 'ia':
                        jogos = otimizador.metodo_ia_avancado(args.quantidade)
                    else:
                        jogos = otimizador.metodo_hibrido(args.quantidade)
                    
                    resultados[nome] = jogos
                    
                    print(f"\n✅ {nome.upper()} ({args.quantidade} jogos):")
                    for i, jogo in enumerate(jogos, 1):
                        soma = sum(jogo)
                        altos = sum(1 for n in jogo if n >= 35)
                        print(f"   {i:2d}. {', '.join(f'{n:2d}' for n in jogo)} "
                              f"(Soma: {soma:3d}, Altos: {altos})")
                    
                except Exception as e:
                    print(f"\n❌ {nome}: Erro - {e}")
            
            if args.output:
                salvar_resultados(resultados, args.output)
            
        else:
            # Gerar com método específico
            try:
                if args.metodo == 'caravaca':
                    jogos = [otimizador.metodo_caravaca() for _ in range(args.quantidade)]
                elif args.metodo == 'estatistico':
                    jogos = otimizador.metodo_estatistico(args.quantidade)
                elif args.metodo == 'ia':
                    jogos = otimizador.metodo_ia_avancado(args.quantidade)
                else:  # hibrido
                    jogos = otimizador.metodo_hibrido(args.quantidade)
                
                print(f"\n✅ {args.metodo.upper()} - {args.quantidade} jogos gerados:")
                for i, jogo in enumerate(jogos, 1):
                    soma = sum(jogo)
                    altos = sum(1 for n in jogo if n >= 35)
                    print(f"   {i:2d}. {', '.join(f'{n:2d}' for n in jogo)} "
                          f"(Soma: {soma:3d}, Altos: {altos})")
                
                if args.output:
                    salvar_resultados({args.metodo: jogos}, args.output)
                
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    else:
        # Modo interativo
        banner()
        
        while True:
            opcao = menu_principal()
            
            if opcao == '6':
                print("\n👋 Obrigado por usar o Gerador de Jogos Mega-Sena!")
                print("   Boa sorte! 🍀")
                break
            
            quantidade = obter_quantidade()
            gerar_jogos(opcao, quantidade)
            
            continuar = input("\n🔄 Deseja gerar mais jogos? (s/n): ")
            if continuar.lower() != 's':
                print("\n👋 Obrigado por usar o Gerador de Jogos Mega-Sena!")
                print("   Boa sorte! 🍀")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
