import type { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  t: (key: string) => string;
}

/** Minimal markdown-like rendering: bold, links, line breaks */
function renderContent(text: string): JSX.Element[] {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    if (line.trim() === '---') {
      return <hr key={i} style={{ border: 'none', borderTop: '1px solid var(--color-border)', margin: '0.75rem 0' }} />;
    }

    if (line.trim() === '') {
      return <br key={i} />;
    }

    // Replace **bold** with <strong>
    const parts: (string | JSX.Element)[] = [];
    const boldRegex = /\*\*(.+?)\*\*/g;
    let lastIndex = 0;
    let match;

    const lineWithLinks = line;
    const tempParts: (string | JSX.Element)[] = [];

    // Handle links [text](url) first
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let linkLastIndex = 0;
    let linkMatch;
    let processedLine = '';
    const linkElements: { placeholder: string; element: JSX.Element }[] = [];
    let linkIdx = 0;

    while ((linkMatch = linkRegex.exec(lineWithLinks)) !== null) {
      processedLine += lineWithLinks.slice(linkLastIndex, linkMatch.index);
      const placeholder = `__LINK_${linkIdx}__`;
      linkElements.push({
        placeholder,
        element: (
          <a key={`link-${i}-${linkIdx}`} href={linkMatch[2]} target="_blank" rel="noopener noreferrer">
            {linkMatch[1]}
          </a>
        ),
      });
      processedLine += placeholder;
      linkLastIndex = linkMatch.index + linkMatch[0].length;
      linkIdx++;
    }
    processedLine += lineWithLinks.slice(linkLastIndex);

    // Now handle bold
    lastIndex = 0;
    while ((match = boldRegex.exec(processedLine)) !== null) {
      if (match.index > lastIndex) {
        parts.push(processedLine.slice(lastIndex, match.index));
      }
      parts.push(<strong key={`bold-${i}-${match.index}`}>{match[1]}</strong>);
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < processedLine.length) {
      parts.push(processedLine.slice(lastIndex));
    }

    // Replace link placeholders
    const finalParts = parts.map((part, partIdx) => {
      if (typeof part === 'string') {
        const linkPlaceholder = linkElements.find((le) => part.includes(le.placeholder));
        if (linkPlaceholder) {
          const segments = part.split(linkPlaceholder.placeholder);
          return (
            <span key={`seg-${i}-${partIdx}`}>
              {segments[0]}
              {linkPlaceholder.element}
              {segments[1] || ''}
            </span>
          );
        }
        return <span key={`text-${i}-${partIdx}`}>{part}</span>;
      }
      return part;
    });

    // Check for list items
    const trimmed = line.trimStart();
    if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || /^\d+\.\s/.test(trimmed)) {
      return (
        <div key={i} style={{ paddingLeft: '1rem', marginBottom: '0.25rem' }}>
          {finalParts}
        </div>
      );
    }

    return (
      <p key={i} style={{ marginBottom: line.trim() ? '0.4rem' : '0' }}>
        {finalParts}
      </p>
    );
  });
}

export default function ChatMessage({ message, t }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`message message--${message.role}`} role="article" aria-label={`${message.role} message`}>
      <div className="message__avatar" aria-hidden="true">
        {isUser ? '👤' : '🗳️'}
      </div>

      <div className="message__bubble">
        <div className="message__content">
          {renderContent(message.content)}
        </div>

        {/* Meta badges */}
        {!isUser && (message.cached || (message.sources && message.sources.length > 0)) && (
          <div className="message__meta">
            {message.cached && (
              <span className="message__badge message__badge--cached">
                ⚡ {t('chat.cached')}
              </span>
            )}
            {message.sources && message.sources.length > 0 && (
              <span className="message__badge message__badge--grounded">
                🔍 Grounded
              </span>
            )}
          </div>
        )}

        {/* Source Citations */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources">
            <div className="sources__title">{t('chat.sources')}</div>
            <div className="sources__list">
              {message.sources.map((source, idx) => (
                <div key={idx} className="sources__item">
                  <span className="sources__icon">🔗</span>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sources__link"
                  >
                    {source.title}
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
