
import { searchNews } from "./api.js";

export async function loadNews(query) {
    const container = document.getElementById("news-container");

    container.innerHTML = "<p>Loading news...</p>";

    try {
        const data = await searchNews(query);

        const articles = data.articles;
        const duplicateGroups = data.duplicate_groups;

        container.innerHTML = "";

        // Identify articles that belong to an exact-title group.
        const groupedUrls = new Set();

        for (const group of duplicateGroups) {
            for (const article of group.articles) {
                groupedUrls.add(article.url);
            }
        }

        // Display only one representative article per duplicate group.
        const displayedGroups = new Set();

        for (const article of articles) {
            const card = document.createElement("div");

            const group = duplicateGroups.find(
                item =>
                    item.articles.some(
                        groupedArticle => groupedArticle.url === article.url
                    )
            );

            if (group) {
                if (displayedGroups.has(group.title)) {
                    continue;
                }

                displayedGroups.add(group.title);
            }

            card.innerHTML = `
                ${article.image ? `<img src="${article.image}" alt="">` : ""}

                <h2></h2>

                <p></p>

                <p>
                    Source: <strong></strong>
                </p>

                <p></p>

                <a target="_blank" rel="noopener noreferrer">
                    View original article ↗
                </a>
            `;

            // Use textContent for article text rather than inserting
            // external news text directly as HTML.
            card.querySelector("h2").textContent = article.title;
            card.querySelectorAll("p")[0].textContent =
                article.description || "No description available.";

            card.querySelector("strong").textContent = article.source;

            card.querySelectorAll("p")[2].textContent =
                new Date(article.publishedAt).toLocaleString();

            const articleLink = card.querySelector("a");
            articleLink.href = article.url;

            if (group) {
                const publisherList = document.createElement("details");
                const summary = document.createElement("summary");

                summary.textContent =
                    `Also reported by ${group.count - 1} other publisher(s)`;

                publisherList.appendChild(summary);

                for (const groupedArticle of group.articles) {
                    const publisherLink = document.createElement("p");
                    const link = document.createElement("a");

                    link.href = groupedArticle.url;
                    link.target = "_blank";
                    link.rel = "noopener noreferrer";
                    link.textContent =
                        `${groupedArticle.source} — View article ↗`;

                    publisherLink.appendChild(link);
                    publisherList.appendChild(publisherLink);
                }

                card.appendChild(publisherList);
            }

            container.appendChild(card);
        }

        if (articles.length === 0) {
            container.innerHTML = "<p>No news articles found.</p>";
        }

    } catch (error) {
        console.error(error);

        container.innerHTML =
            "<p>Unable to load news. Please try again.</p>";
    }
}

const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");

searchButton.addEventListener("click", () => {
    const query = searchInput.value.trim();

    if (query) {
        loadNews(query);
    }
});

searchInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        const query = searchInput.value.trim();

        if (query) {
            loadNews(query);
        }
    }
});
