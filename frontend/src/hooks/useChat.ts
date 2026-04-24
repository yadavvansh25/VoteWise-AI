import { useState, useCallback } from 'react';
import type { ChatMessage, Language } from '../types';
import api from '../services/api';

let messageIdCounter = 0;

function generateId(): string {
  messageIdCounter += 1;
  return `msg_${Date.now()}_${messageIdCounter}`;
}

export function useChat(language: Language) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Build conversation history (last 6 messages)
        const history = messages.slice(-6).map((msg) => ({
          role: msg.role,
          content: msg.content,
        }));

        const response = await api.sendMessage({
          message: content.trim(),
          language,
          conversation_history: history,
        });

        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: response.message,
          timestamp: response.timestamp,
          intent: response.intent,
          sources: response.sources,
          piiDetected: response.pii_info?.detected,
          cached: response.cached,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        // Add error message
        const errorMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content:
            '⚠️ I apologize, but I\'m having trouble connecting right now. Please try again in a moment, or visit **voters.eci.gov.in** for official information.',
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [messages, language, isLoading]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  };
}
