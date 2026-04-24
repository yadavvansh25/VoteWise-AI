import type { AccessibilitySettings } from '../types';

interface AccessibilityPanelProps {
  settings: AccessibilitySettings;
  setFontSize: (size: number) => void;
  toggleHighContrast: () => void;
  toggleReducedMotion: () => void;
  resetSettings: () => void;
  t: (key: string) => string;
}

export default function AccessibilityPanel({
  settings,
  setFontSize,
  toggleHighContrast,
  toggleReducedMotion,
  resetSettings,
  t,
}: AccessibilityPanelProps) {
  return (
    <div className="a11y-panel" role="dialog" aria-label="Accessibility settings" id="a11y-panel">
      <h2 className="a11y-panel__title">{t('accessibility.title')}</h2>

      {/* Font Size */}
      <div className="a11y-panel__row">
        <label className="a11y-panel__label" htmlFor="font-size-slider">
          {t('accessibility.fontSize')}
        </label>
        <input
          id="font-size-slider"
          type="range"
          min={100}
          max={200}
          step={10}
          value={settings.fontSize}
          onChange={(e) => setFontSize(Number(e.target.value))}
          className="a11y-panel__slider"
          aria-valuemin={100}
          aria-valuemax={200}
          aria-valuenow={settings.fontSize}
          aria-valuetext={`${settings.fontSize}%`}
        />
        <span className="a11y-panel__value">{settings.fontSize}%</span>
      </div>

      {/* High Contrast */}
      <div className="a11y-panel__row">
        <span className="a11y-panel__label">{t('accessibility.highContrast')}</span>
        <button
          className={`toggle-switch ${settings.highContrast ? 'toggle-switch--active' : ''}`}
          onClick={toggleHighContrast}
          role="switch"
          aria-checked={settings.highContrast}
          aria-label={`High contrast mode: ${settings.highContrast ? 'on' : 'off'}`}
          id="high-contrast-toggle"
        >
          <span className="toggle-switch__knob" />
        </button>
      </div>

      {/* Reduced Motion */}
      <div className="a11y-panel__row">
        <span className="a11y-panel__label">{t('accessibility.reducedMotion')}</span>
        <button
          className={`toggle-switch ${settings.reducedMotion ? 'toggle-switch--active' : ''}`}
          onClick={toggleReducedMotion}
          role="switch"
          aria-checked={settings.reducedMotion}
          aria-label={`Reduced motion: ${settings.reducedMotion ? 'on' : 'off'}`}
          id="reduced-motion-toggle"
        >
          <span className="toggle-switch__knob" />
        </button>
      </div>

      {/* Reset */}
      <button
        className="a11y-panel__reset"
        onClick={resetSettings}
        id="a11y-reset-btn"
      >
        {t('accessibility.reset')}
      </button>
    </div>
  );
}
