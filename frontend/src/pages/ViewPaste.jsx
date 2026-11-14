
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getPaste } from "../services/api";

function ViewPaste() {
  const { id } = useParams();

  const [paste, setPaste] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchPaste() {
      try {
        setLoading(true);
        setError("");

        const data = await getPaste(id);
        setPaste(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchPaste();
  }, [id]);

  if (loading) {
    return <p className="view-status">Loading paste...</p>;
  }

  if (error) {
    return (
      <div className="view-error">
        <h2>Paste Unavailable</h2>
        <p>{error}</p>
        <Link to="/">Create a new paste</Link>
      </div>
    );
  }

  return (
    <section className="view-paste">
      <h1>Your Paste</h1>

      <pre className="paste-content">{paste.content}</pre>

      <div className="paste-metadata">
        <p>
          Remaining views:{" "}
          {paste.remaining_views === null
            ? "Unlimited"
            : paste.remaining_views}
        </p>

        <p>
          Expires at:{" "}
          {paste.expires_at
            ? new Date(paste.expires_at).toLocaleString()
            : "Never"}
        </p>
      </div>

      <Link to="/" className="back-link">
        Create another paste
      </Link>
    </section>
  );
}

export default ViewPaste;
