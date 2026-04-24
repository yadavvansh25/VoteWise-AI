import type { Language } from '../types';

interface HeaderProps {
  language: Language;
  setLanguage: (lang: Language) => void;
  onToggleA11y: () => void;
  a11yOpen: boolean;
  t: (key: string) => string;
}

export default function Header({ language, setLanguage, onToggleA11y, a11yOpen, t }: HeaderProps) {
  const languages: { code: Language; label: string }[] = [
    { code: 'en', label: 'EN' },
    { code: 'hi', label: 'हि' },
    { code: 'ta', label: 'த' },
  ];

  return (
    <header className="header" role="banner">
      <div className="header__brand">
        <img
          src="/logo.png"
          alt="VoteWise AI Logo"
          className="header__logo"
        />
        <div>
          <h1 className="header__title">{t('app.title')}</h1>
          <p className="header__tagline">{t('app.tagline')}</p>
        </div>
      </div>

      <div className="header__controls">
        <nav className="language-selector" role="navigation" aria-label="Language selection">
          {languages.map((lang) => (
            <button
              key={lang.code}
              className={`language-selector__btn ${language === lang.code ? 'language-selector__btn--active' : ''}`}
              onClick={() => setLanguage(lang.code)}
              aria-pressed={language === lang.code}
              aria-label={`Switch to ${lang.code === 'en' ? 'English' : lang.code === 'hi' ? 'Hindi' : 'Tamil'}`}
              id={`lang-btn-${lang.code}`}
            >
              {lang.label}
            </button>
          ))}
        </nav>

        <button
          className="a11y-toggle"
          onClick={onToggleA11y}
          aria-expanded={a11yOpen}
          aria-label="Accessibility settings"
          id="a11y-toggle-btn"
        >
          ♿
        </button>
      </div>
    </header>
  );
}
