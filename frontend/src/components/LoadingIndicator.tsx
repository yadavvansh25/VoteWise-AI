export default function LoadingIndicator() {
  return (
    <div className="loading" role="status" aria-label="AI is thinking">
      <div className="loading__avatar" aria-hidden="true">🗳️</div>
      <div className="loading__bubble">
        <span className="loading__dot" />
        <span className="loading__dot" />
        <span className="loading__dot" />
      </div>
    </div>
  );
}
