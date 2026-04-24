interface QuickActionsProps {
  onSelect: (question: string) => void;
  t: (key: string) => string;
}

export default function QuickActions({ onSelect, t }: QuickActionsProps) {
  const actions = [
    { key: 'register', emoji: '📝' },
    { key: 'evm', emoji: '🖥️' },
    { key: 'booth', emoji: '📍' },
    { key: 'eligibility', emoji: '✅' },
    { key: 'vvpat', emoji: '🧾' },
    { key: 'documents', emoji: '📄' },
  ];

  return (
    <div className="quick-actions" role="region" aria-label="Quick questions">
      <div className="quick-actions__title">{t('quickActions.title')}</div>
      <div className="quick-actions__grid">
        {actions.map((action) => (
          <button
            key={action.key}
            className="quick-actions__chip"
            onClick={() => onSelect(t(`quickActions.${action.key}`))}
            id={`quick-action-${action.key}`}
          >
            {action.emoji} {t(`quickActions.${action.key}`)}
          </button>
        ))}
      </div>
    </div>
  );
}
