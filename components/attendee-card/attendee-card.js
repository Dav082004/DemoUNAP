// Componente: attendee-card
// Renderiza la tarjeta de un asistente a partir del <template> declarado en
// index.html (#attendee-card-template). Es el único "molde" de tarjeta: todas
// las tarjetas comparten el mismo diseño, proporciones y animaciones.

const AVATAR_SOURCES = {
  mona: { src: "img/avatars/MonaPuno.png", alt: "Avatar de Mona, la gata pulpo de GitHub" },
  copilot: { src: "img/avatars/CopilotPuno.png", alt: "Avatar de Copilot" },
  ducky: { src: "img/avatars/DuckyPuno.png", alt: "Avatar de Ducky, el patito de goma" },
};

const FALLBACK_AVATAR = AVATAR_SOURCES.mona;

/**
 * Crea el elemento DOM de una tarjeta de asistente.
 *
 * @param {{username: string, name: string, technology: string, avatar: string}} attendee
 * @param {HTMLTemplateElement} template - Template de origen (#attendee-card-template).
 * @returns {HTMLElement} Nodo `<li class="attendee-card">` listo para insertar.
 */
export function createAttendeeCard(attendee, template) {
  const fragment = template.content.cloneNode(true);
  const card = fragment.querySelector(".attendee-card");

  const avatar = AVATAR_SOURCES[attendee.avatar] ?? FALLBACK_AVATAR;
  const avatarImg = card.querySelector(".attendee-card__avatar");
  avatarImg.src = avatar.src;
  avatarImg.alt = `${avatar.alt} — usado por ${attendee.name}`;

  card.querySelector(".attendee-card__name").textContent = attendee.name;
  card.querySelector(".attendee-card__tech").textContent = attendee.technology;

  const link = card.querySelector(".attendee-card__link");
  link.href = `https://github.com/${attendee.username}`;
  link.setAttribute("aria-label", `Ver el perfil de GitHub de ${attendee.name}`);

  return card;
}
