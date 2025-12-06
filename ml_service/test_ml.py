#!/usr/bin/env python3
import requests
import json

print("🧪 Testando Python ML Service...")

# 1. Testar health
try:
    resp = requests.get('http://localhost:5000/health', timeout=5)
    print(f"✅ Health check: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
except Exception as e:
    print(f"❌ Health check falhou: {e}")

# 2. Testar geração com IA
print("\n🎯 Testando geração com IA Python...")
try:
    resp = requests.post(
        'http://localhost:5000/api/generate',
        json={'day': 15, 'method': 'hybrid'},
        timeout=10
    )
    print(f"✅ IA Python: {resp.status_code}")
    data = resp.json()
    
    if data.get('success'):
        game = data['games'][0]
        print(f"📊 Números: {game['numbers']}")
        print(f"💰 Soma: {game['sum']}")
        print(f"📈 Altos: {game['high_numbers']}")
        print(f"🔢 Pares: {game['even_numbers']}")
        print(f"🤖 Fonte: {data.get('service', 'python_ml')}")
    else:
        print(f"❌ Erro: {data.get('error', 'Desconhecido')}")
        
except Exception as e:
    print(f"❌ IA Python falhou: {e}")
