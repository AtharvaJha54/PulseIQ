const API_BASE_URL = "http://127.0.0.1:5000";

export async function searchNews(query) {

    const response = await fetch(
        `${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
        throw new Error("Failed to fetch news");
    }

    return await response.json();
}