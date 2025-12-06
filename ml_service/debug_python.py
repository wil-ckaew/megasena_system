#!/usr/bin/env python3
import pandas as pd
import traceback

print("🔍 Debug do Python IA...")
try:
    df = pd.read_csv('resultados_megasena.csv')
    print(f"✅ CSV carregado: {len(df)} linhas")
    print(f"📋 Colunas: {list(df.columns)}")
    
    # Verificar tipos de dados
    print("\n📊 Primeiras 3 linhas:")
    print(df.head(3))
    
    # Verificar dados das colunas n1-n6
    print("\n🔢 Estatísticas dos números:")
    for col in ['n1', 'n2', 'n3', 'n4', 'n5', 'n6']:
        if col in df.columns:
            print(f"{col}: min={df[col].min()}, max={df[col].max()}, tipo={df[col].dtype}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    traceback.print_exc()
