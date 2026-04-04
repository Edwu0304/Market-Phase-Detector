async function loadDashboard() {
  const response = await fetch("./data/latest.json");
  const payload = await response.json();
  const root = document.getElementById("summary");

  root.innerHTML = "";

  for (const country of payload.countries) {
    const card = document.createElement("article");
    card.className = "card";

    const reasons = country.decision.reasons
      .map((reason) => `<li>${reason}</li>`)
      .join("");

    card.innerHTML = `
      <h2>${country.country}</h2>
      <p class="phase">${country.decision.final_phase}</p>
      <p class="watch">Watch: ${country.decision.watch ?? "none"}</p>
      <p class="date">As of ${country.as_of}</p>
      <ul class="reasons">${reasons}</ul>
    `;

    root.appendChild(card);
  }
}

loadDashboard().catch((error) => {
  const root = document.getElementById("summary");
  root.innerHTML = `<article class="card"><h2>Data load failed</h2><p>${error.message}</p></article>`;
});
