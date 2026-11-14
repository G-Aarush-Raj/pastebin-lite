function CopyButton({ text }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      alert("Link copied successfully!");
    } catch {
      alert("Unable to copy the link.");
    }
  };

  return (
    <button type="button" onClick={handleCopy}>
      Copy Link
    </button>
  );
}

export default CopyButton;
