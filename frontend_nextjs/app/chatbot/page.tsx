'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

// Configuração da API - ajuste conforme seu ambiente
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: 'Olá! Sou o assistente da Mega-Sena. Como posso ajudar?', sender: 'bot', timestamp: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
    checkBackendStatus();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setBackendStatus(response.ok ? 'online' : 'offline');
    } catch {
      setBackendStatus('offline');
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Enviar para o backend Rust
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: messages.length + 2,
        text: data.response || 'Desculpe, não consegui processar sua pergunta.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: messages.length + 2,
        text: 'Backend não disponível. Iniciando modo de demonstração...',
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      
      // Modo de demonstração - respostas simuladas
      setTimeout(() => {
        const demoResponse = getDemoResponse(input);
        const demoMessage: Message = {
          id: messages.length + 3,
          text: demoResponse,
          sender: 'bot',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, demoMessage]);
      }, 1000);
    } finally {
      setLoading(false);
    }
  };

  // Respostas de demonstração quando o backend não está disponível
  const getDemoResponse = (question: string): string => {
    const lowerQuestion = question.toLowerCase();
    
    if (lowerQuestion.includes('números mais sorteados') || lowerQuestion.includes('mais sorteados')) {
      return '📊 **Números mais sorteados (base histórica):**\n- 53: 23 vezes\n- 10: 22 vezes\n- 05: 21 vezes\n- 37: 20 vezes\n- 33: 19 vezes\n\nEstes são os 5 números que mais apareceram nos últimos 52 sorteios.';
    }
    
    if (lowerQuestion.includes('probabilidade') || lowerQuestion.includes('chance')) {
      return '🎲 **Probabilidades da Mega-Sena:**\n- Acertar 6 números: 1 em 50.063.860\n- Acertar 5 números: 1 em 154.518\n- Acertar 4 números: 1 em 2.332\n\nCom nosso sistema de IA, otimizamos estas chances através de análise estatística!';
    }
    
    if (lowerQuestion.includes('ia') || lowerQuestion.includes('inteligência artificial') || lowerQuestion.includes('como funciona')) {
      return '🤖 **Sistema de IA:**\n1. Analisa 52 sorteios históricos\n2. Usa Machine Learning Python\n3. Identifica padrões e tendências\n4. Considera números quentes/frios\n5. Otimiza combinações probabilisticamente\n\nO sistema combina Python (ML) + Rust (API) para máxima performance!';
    }
    
    if (lowerQuestion.includes('gerar') || lowerQuestion.includes('jogo') || lowerQuestion.includes('sugestão')) {
      return '🎯 **Jogo sugerido pela IA:**\n```\n05 - 10 - 23 - 37 - 42 - 53\n```\n📈 **Análise:**\n• Soma: 170 (ideal: 180-240)\n• 2 números altos (≥35)\n• 3 pares / 3 ímpares\n• Boa distribuição entre faixas\n\n*Baseado em análise estatística dos últimos sorteios.*';
    }
    
    if (lowerQuestion.includes('estratégia') || lowerQuestion.includes('dica')) {
      return '💡 **Estratégias recomendadas:**\n1. Misture números altos e baixos\n2. Balanceie pares e ímpares\n3. Distribua entre todas as faixas (1-15, 16-30, 31-45, 46-60)\n4. Considere números "quentes" recentes\n5. Use nosso sistema de bolão para aumentar cobertura\n\nA IA do sistema aplica estas estratégias automaticamente!';
    }
    
    return '🤖 **Modo Demonstração:**\nNo momento, o backend de IA está offline. Quando disponível, posso:\n• Analisar estatísticas em tempo real\n• Gerar jogos otimizados com ML\n• Responder perguntas complexas\n• Fazer previsões baseadas em dados\n\nEnquanto isso, experimente perguntar sobre: "números mais sorteados", "probabilidades" ou "estratégias".';
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Arial, sans-serif',
    },
    nav: {
      display: 'flex',
      gap: '20px',
      marginBottom: '30px',
      padding: '15px',
      backgroundColor: '#f0f0f0',
      borderRadius: '10px',
    },
    navLink: {
      textDecoration: 'none',
      color: '#306998',
      fontWeight: 'bold',
      padding: '10px 20px',
      borderRadius: '5px',
      backgroundColor: 'white',
      border: '2px solid #306998',
    },
    statusBadge: {
      padding: '5px 10px',
      borderRadius: '15px',
      fontSize: '12px',
      fontWeight: 'bold',
      backgroundColor: backendStatus === 'online' ? '#4caf50' : 
                     backendStatus === 'offline' ? '#f44336' : '#ff9800',
      color: 'white',
      marginLeft: '10px',
    },
    chatContainer: {
      backgroundColor: 'white',
      borderRadius: '15px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      overflow: 'hidden',
      marginTop: '20px',
    },
    chatHeader: {
      backgroundColor: '#306998',
      color: 'white',
      padding: '20px',
    },
    botInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '15px',
    },
    botAvatar: {
      fontSize: '40px',
    },
    botStatus: {
      opacity: 0.8,
      fontSize: '14px',
      display: 'flex',
      alignItems: 'center',
    },
    messagesContainer: {
      height: '500px',
      overflowY: 'auto',
      padding: '20px',
      backgroundColor: '#f5f5f5',
    },
    message: {
      marginBottom: '15px',
      maxWidth: '80%',
      padding: '15px',
      borderRadius: '15px',
      position: 'relative',
    },
    userMessage: {
      marginLeft: 'auto',
      backgroundColor: '#306998',
      color: 'white',
      borderBottomRightRadius: '5px',
    },
    botMessage: {
      marginRight: 'auto',
      backgroundColor: 'white',
      color: '#333',
      borderBottomLeftRadius: '5px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    },
    messageContent: {
      fontSize: '16px',
      lineHeight: '1.5',
      whiteSpace: 'pre-line',
    },
    timestamp: {
      fontSize: '12px',
      opacity: 0.7,
      marginTop: '5px',
      textAlign: 'right',
    },
    typingIndicator: {
      display: 'flex',
      gap: '5px',
      padding: '15px',
      backgroundColor: 'white',
      borderRadius: '15px',
      width: 'fit-content',
      marginBottom: '15px',
    },
    typingDot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#306998',
      animation: 'typing 1.4s infinite',
    },
    inputContainer: {
      padding: '20px',
      borderTop: '1px solid #eee',
      display: 'flex',
      gap: '10px',
    },
    textarea: {
      flex: 1,
      padding: '15px',
      fontSize: '16px',
      border: '2px solid #ddd',
      borderRadius: '10px',
      resize: 'none',
      fontFamily: 'Arial, sans-serif',
    },
    sendButton: {
      padding: '15px 30px',
      backgroundColor: '#306998',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      cursor: 'pointer',
      fontWeight: 'bold',
    },
    suggestions: {
      padding: '20px',
      backgroundColor: '#f9f9f9',
      borderTop: '1px solid #eee',
    },
    suggestionsTitle: {
      marginBottom: '10px',
      color: '#666',
      fontSize: '14px',
    },
    suggestionButtons: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '10px',
    },
    suggestionButton: {
      padding: '8px 15px',
      backgroundColor: 'white',
      border: '1px solid #ddd',
      borderRadius: '20px',
      fontSize: '14px',
      cursor: 'pointer',
      transition: 'all 0.3s',
    },
  };

  return (
    <div style={styles.container}>
      <nav style={styles.nav}>
        <Link href="/" style={styles.navLink}>🏠 Home</Link>
        <Link href="/bolao" style={styles.navLink}>🎯 Bolão</Link>
        <Link href="/chatbot" style={styles.navLink}>🤖 ChatBot</Link>
      </nav>

      <h1>🤖 ChatBot da Mega-Sena</h1>
      <p>Faça perguntas sobre estatísticas, probabilidades e estratégias</p>

      <div style={styles.chatContainer}>
        <div style={styles.chatHeader}>
          <div style={styles.botInfo}>
            <div style={styles.botAvatar}>🤖</div>
            <div>
              <h3>Assistente Mega-Sena</h3>
              <div style={styles.botStatus}>
                {backendStatus === 'online' ? '✅ Online • IA Python + Rust' : 
                 backendStatus === 'offline' ? '⚠️ Modo Demonstração • Backend offline' : 
                 '⏳ Verificando conexão...'}
                <span style={styles.statusBadge}>
                  {backendStatus === 'online' ? 'CONECTADO' : 
                   backendStatus === 'offline' ? 'OFFLINE' : 'VERIFICANDO'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div style={styles.messagesContainer}>
          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                ...styles.message,
                ...(message.sender === 'user' ? styles.userMessage : styles.botMessage),
              }}
            >
              <div style={styles.messageContent}>
                {message.text}
              </div>
              <div style={styles.timestamp}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          {loading && (
            <div style={styles.typingIndicator}>
              <div style={styles.typingDot}></div>
              <div style={styles.typingDot}></div>
              <div style={styles.typingDot}></div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={styles.inputContainer}>
          <textarea
            style={styles.textarea}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua pergunta sobre a Mega-Sena..."
            rows={3}
            disabled={loading}
          />
          <button
            style={styles.sendButton}
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            {loading ? 'Enviando...' : 'Enviar'}
          </button>
        </div>

        <div style={styles.suggestions}>
          <p style={styles.suggestionsTitle}>Perguntas sugeridas:</p>
          <div style={styles.suggestionButtons}>
            {[
              'Quais são os números mais sorteados?',
              'Como funciona a IA do sistema?',
              'Qual a probabilidade de ganhar?',
              'Gerar um jogo otimizado',
            ].map((suggestion, index) => (
              <button
                key={index}
                style={styles.suggestionButton}
                onClick={() => setInput(suggestion)}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
