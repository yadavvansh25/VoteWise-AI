import { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import AccessibilityPanel from './components/AccessibilityPanel';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import QuickActions from './components/QuickActions';
import LoadingIndicator from './components/LoadingIndicator';
import { useLanguage } from './hooks/useLanguage';
import { useAccessibility } from './hooks/useAccessibility';
import { useChat } from './hooks/useChat';

export default function App() {
  const { language, setLanguage, t } = useLanguage();
  const { settings, setFontSize, toggleHighContrast, toggleReducedMotion, resetSettings } = useAccessibility();
  const { messages, isLoading, sendMessage } = useChat(language);
  const [a11yOpen, setA11yOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Hide welcome after first message
  useEffect(() => {
    if (messages.length > 0) {
      setShowWelcome(false);
    }
  }, [messages]);

  const handleSend = (message: string) => {
    sendMessage(message);
  };

  const handleQuickAction = (question: string) => {
    sendMessage(question);
  };

  return (
    <>
      <Header
        language={language}
        setLanguage={setLanguage}
        onToggleA11y={() => setA11yOpen(!a11yOpen)}
        a11yOpen={a11yOpen}
        t={t}
      />

      {a11yOpen && (
        <AccessibilityPanel
          settings={settings}
          setFontSize={setFontSize}
          toggleHighContrast={toggleHighContrast}
          toggleReducedMotion={toggleReducedMotion}
          resetSettings={resetSettings}
          t={t}
        />
      )}

      <main className="chat-container" role="main">
        <div className="chat-messages" aria-live="polite" aria-relevant="additions">
          {/* Welcome Message */}
          {showWelcome && messages.length === 0 && (
            <ChatMessage
              message={{
                id: 'welcome',
                role: 'assistant',
                content: t('chat.welcome'),
                timestamp: new Date().toISOString(),
              }}
              t={t}
            />
          )}

          {/* Conversation Messages */}
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} t={t} />
          ))}

          {/* Loading Indicator */}
          {isLoading && <LoadingIndicator />}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions (show when no messages) */}
        {messages.length === 0 && (
          <QuickActions onSelect={handleQuickAction} t={t} />
        )}
      </main>

      <ChatInput
        onSend={handleSend}
        isLoading={isLoading}
        placeholder={t('chat.placeholder')}
        sendLabel={t('chat.send')}
      />

      <footer className="footer" role="contentinfo">
        <span>{t('footer.disclaimer')}</span>
        <span>•</span>
        <span>{t('footer.powered')}</span>
      </footer>
    </>
  );
}
