
function PasteOptions({ ttl, setTtl, maxViews, setMaxViews }) {
  return (
    <div className="paste-options">
      <h3>Paste Options</h3>

      <div className="option-group">
        <label htmlFor="ttl">Expiration time (seconds)</label>
        <input
          id="ttl"
          type="number"
          min="1"
          placeholder="No expiration"
          value={ttl}
          onChange={(event) => setTtl(event.target.value)}
        />
        <small>Leave empty for no expiration.</small>
      </div>

      <div className="option-group">
        <label htmlFor="maxViews">Maximum views</label>
        <input
          id="maxViews"
          type="number"
          min="1"
          placeholder="Unlimited views"
          value={maxViews}
          onChange={(event) => setMaxViews(event.target.value)}
        />
        <small>Leave empty for unlimited views.</small>
      </div>
    </div>
  );
}

export default PasteOptions;
