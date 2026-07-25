// Punto de entrada del frontend: obtiene attendees.json y renderiza las
// tarjetas usando el componente attendee-card.
import { createAttendeeCard } from "../components/attendee-card/attendee-card.js";

const ATTENDEES_URL = "attendees.json";

async function loadAttendees() {
  const grid = document.getElementById("attendees-grid");
  const countEl = document.getElementById("attendees-count");
  const emptyEl = document.getElementById("attendees-empty");
  const template = document.getElementById("attendee-card-template");

  try {
    const response = await fetch(ATTENDEES_URL, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`No se pudo cargar ${ATTENDEES_URL}: ${response.status}`);
    }

    const attendees = await response.json();

    if (!Array.isArray(attendees) || attendees.length === 0) {
      emptyEl.hidden = false;
      countEl.textContent = "0 personas registradas";
      return;
    }

    const fragment = document.createDocumentFragment();
    attendees.forEach((attendee) => {
      fragment.appendChild(createAttendeeCard(attendee, template));
    });
    grid.appendChild(fragment);

    countEl.textContent = `${attendees.length} ${
      attendees.length === 1 ? "persona registrada" : "personas registradas"
    }`;
  } catch (error) {
    console.error(error);
    countEl.textContent = "No se pudo cargar la lista de asistentes.";
  }
}

document.addEventListener("DOMContentLoaded", loadAttendees);
