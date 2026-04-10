const cities = Array.isArray(window.__CITIES__) ? window.__CITIES__ : [];

const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const citySelect = document.getElementById("citySelect");
const panelTitle = document.getElementById("panelTitle");
const panelSubtitle = document.getElementById("panelSubtitle");
const panelMeta = document.getElementById("panelMeta");
const daysRow = document.getElementById("daysRow");
const placeholder = document.getElementById("placeholder");
const meteogramImg = document.getElementById("meteogramImg");

const normalize = (text) => {
  return text
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "");
};

const renderDays = () => {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat("pl-PL", {
    weekday: "short",
    day: "2-digit",
    month: "2-digit",
  });

  daysRow.innerHTML = "";
  for (let i = 0; i < 4; i += 1) {
    const day = new Date(now);
    day.setDate(now.getDate() + i);

    const pill = document.createElement("div");
    pill.className = "day-pill";
    pill.textContent = formatter.format(day);
    daysRow.appendChild(pill);
  }
};

const renderCities = (list) => {
  citySelect.innerHTML = "";
  if (!list.length) {
    const option = document.createElement("option");
    option.textContent = "Brak wynikow";
    option.disabled = true;
    citySelect.appendChild(option);
    return;
  }

  list.forEach((city) => {
    const option = document.createElement("option");
    option.value = city.name;
    option.textContent = city.name;
    citySelect.appendChild(option);
  });
};

const filterCities = () => {
  const query = normalize(searchInput.value || "");
  if (!query) {
    renderCities(cities);
    return;
  }

  const filtered = cities.filter((city) => normalize(city.name).includes(query));
  renderCities(filtered);
};

const showMeteogram = async (cityName) => {
  if (!cityName) {
    return;
  }

  panelTitle.textContent = `Ladowanie prognozy...`;
  panelSubtitle.textContent = "Trwa pobieranie meteogramu.";
  panelMeta.textContent = "";
  placeholder.textContent = "Pobieram meteogram...";
  placeholder.style.display = "grid";
  meteogramImg.classList.remove("is-visible");

  try {
    const response = await fetch(`/api/meteogram?name=${encodeURIComponent(cityName)}`);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Blad pobierania danych");
    }

    meteogramImg.src = payload.url;
    meteogramImg.onload = () => {
      placeholder.style.display = "none";
      meteogramImg.classList.add("is-visible");
    };

    panelTitle.textContent = `Prognoza: ${payload.name}`;
    panelSubtitle.textContent = "Aktualny meteogram z meteo.pl";
    panelMeta.textContent = `Cykl: ${payload.fdate.slice(0, 8)} ${payload.fdate.slice(8)} UTC`;
  } catch (error) {
    panelTitle.textContent = "Nie udalo sie pobrac danych";
    panelSubtitle.textContent = error.message || "Sprobuj ponownie";
    placeholder.textContent = "Nie udalo sie zaladowac meteogramu.";
  }
};

searchBtn.addEventListener("click", filterCities);
searchInput.addEventListener("input", filterCities);
citySelect.addEventListener("change", (event) => {
  showMeteogram(event.target.value);
});

renderDays();
renderCities(cities);
