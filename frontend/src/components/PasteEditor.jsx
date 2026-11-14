
import { useState } from "react";
import PasteOptions from "./PasteOptions";
import { createPaste } from "../services/api";
import CopyButton from "./CopyButton";

function PasteEditor() {
  const [content, setContent] = useState("");
  const [ttl, setTtl] = useState("");
  const [maxViews, setMaxViews] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [createdPaste, setCreatedPaste] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setCreatedPaste(null);

    if (content.length === 0) {
      setError("Please enter some content.");
      return;
    }

    if (
      ttl !== "" &&
      (!Number.isInteger(Number(ttl)) || Number(ttl) < 1)
    ) {
      setError("Expiration time must be a positive integer.");
      return;
    }

    if (
      maxViews !== "" &&
      (!Number.isInteger(Number(maxViews)) || Number(maxViews) < 1)
    ) {
      setError("Maximum views must be a positive integer.");
      return;
    }

    const pasteData = {
      content,
      ...(ttl !== "" && { ttl_seconds: Number(ttl) }),
      ...(maxViews !== "" && { max_views: Number(maxViews) }),
    };

    try {
      setLoading(true);

      const result = await createPaste(pasteData);
      setCreatedPaste(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
const shareUrl = createdPaste
  ? `${window.location.origin}/p/${createdPaste.id}`
  : "";
  return (
    <section className="paste-editor">
      <h1>Create a Paste</h1>

      <p className="editor-description">
        Write or paste your text below and create a shareable link.
      </p>

      <form onSubmit={handleSubmit}>
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Start typing or paste your content here..."
          rows="14"
        />

        <PasteOptions
          ttl={ttl}
          setTtl={setTtl}
          maxViews={maxViews}
          setMaxViews={setMaxViews}
        />

        <div className="editor-footer">
          <span>{content.length} characters</span>

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create Paste"}
          </button>
        </div>
      </form>

      {error && <p className="error-message">{error}</p>}

      {createdPaste && (
  <div className="success-message">
    <h3>Paste created successfully!</h3>
    <p>Your shareable link:</p>

    <div className="share-link">
      <a href={shareUrl} target="_blank" rel="noopener noreferrer">
        {shareUrl}
      </a>

      <CopyButton text={shareUrl} />
    </div>
  </div>
)}
    </section>
  );
}

export default PasteEditor;
