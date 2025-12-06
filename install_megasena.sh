#!/bin/bash

# Script de instalação do Mega-Sena Otimizador

echo "========================================"
echo "🔧 INSTALANDO MEGA-SENA OTIMIZADOR"
echo "========================================"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale primeiro:"
    echo "   sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python3 encontrado"

# Criar ambiente virtual
echo "📁 Criando ambiente virtual..."
python3 -m venv venv_megasena

# Ativar ambiente virtual
source venv_megasena/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install pandas numpy scikit-learn

# Verificar se o requirements.txt existe
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Verificar se o CSV existe
if [ ! -f "resultados_megasena.csv" ]; then
    echo "⚠️  Arquivo resultados_megasena.csv não encontrado!"
    echo "📁 Procurando em subdiretórios..."
    
    found=0
    for dir in . ml_service; do
        if [ -f "$dir/resultados_megasena.csv" ]; then
            echo "✅ Encontrado em $dir/"
            cp "$dir/resultados_megasena.csv" .
            found=1
            break
        fi
    done
    
    if [ $found -eq 0 ]; then
        echo "📄 Criando arquivo CSV de exemplo..."
        cat > resultados_megasena.csv << 'CSVEOF'
Concurso,Data,n1,n2,n3,n4,n5,n6
2933,28/10/2025,1,18,22,42,48,50
2932,25/10/2025,4,13,25,36,40,53
2931,23/10/2025,4,19,23,36,47,52
2930,21/10/2025,1,11,13,14,36,45
2929,18/10/2025,9,16,24,30,33,44
2928,16/10/2025,10,28,31,40,43,48
2927,14/10/2025,8,21,26,28,49,56
2926,11/10/2025,3,7,15,16,32,57
2925,09/10/2025,3,6,25,29,30,42
2924,07/10/2025,5,12,13,28,30,55
CSVEOF
        echo "✅ CSV de exemplo criado com 10 sorteios"
    fi
fi

# Tornar o script executável
chmod +x megasena_corrigido.py

echo ""
echo "========================================"
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "========================================"
echo ""
echo "Para usar o otimizador:"
echo ""
echo "1. Ativar ambiente virtual:"
echo "   source venv_megasena/bin/activate"
echo ""
echo "2. Executar o otimizador:"
echo "   python3 megasena_corrigido.py"
echo ""
echo "3. Para gerar múltiplos jogos (exemplo):"
echo "   python3 -c \"from megasena_corrigido import MegaSenaOtimizadorV3; m = MegaSenaOtimizadorV3(); jogos = m.metodo_hibrido(5); [print(f'Jogo {i+1}: {j}') for i, j in enumerate(jogos)]\""
echo ""
echo "========================================"
