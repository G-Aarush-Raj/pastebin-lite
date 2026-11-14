
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function createPaste(pasteData) {
  const response = await fetch(`${API_BASE_URL}/api/pastes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(pasteData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to create paste.");
  }

  return data;
}

export async function getPaste(id) {
  const response = await fetch(
    `${API_BASE_URL}/api/pastes/${id}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Paste not found or unavailable.");
  }

  return data;
}
