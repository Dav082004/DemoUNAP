"""Valida y procesa el registro de un asistente a partir de una Issue Form.

Este script se ejecuta desde el workflow `.github/workflows/process-attendee.yml`.
Lee la identidad autenticada (`GITHUB_ACTOR`) y el cuerpo de la Issue
(`ISSUE_BODY`), aplica la regla de unicidad (1 registro por usuario) y, si el
usuario es nuevo, agrega su registro a `attendees.json`.

Variables de entorno esperadas:
    GITHUB_ACTOR   Usuario autenticado que creó la Issue (inyectado por Actions).
    ISSUE_BODY     Cuerpo markdown de la Issue generado por el Issue Form.
    ATTENDEES_PATH Ruta al archivo JSON de asistentes (opcional, por defecto
                   "attendees.json" en la raíz del repositorio).
    GITHUB_OUTPUT  Ruta del archivo de outputs del step (inyectado por Actions).

Outputs escritos en GITHUB_OUTPUT:
    error         "true" si faltan campos o el avatar no es válido.
    duplicate     "true" si el usuario ya estaba registrado.
    display_name  Nombre a mostrar capturado en el formulario.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ATTENDEES_PATH = Path(os.environ.get("ATTENDEES_PATH", "attendees.json"))

# Las claves deben coincidir con las opciones del dropdown en
# .github/ISSUE_TEMPLATE/registro-asistencia.yml
AVATAR_MAP = {
    "mona": "mona",
    "copilot": "copilot",
    "ducky": "ducky",
}

FIELD_NOMBRE = "Nombre a mostrar"
FIELD_TECNOLOGIA = "Tecnología"
FIELD_AVATAR = "Selecciona tu avatar"

NO_RESPONSE = "_No response_"


def parse_issue_body(body: str) -> dict[str, str]:
    """Convierte el body markdown de una Issue Form en un dict {label: valor}.

    GitHub renderiza cada campo del formulario como:

        ### Label

        valor

    por lo que basta con separar por encabezados de nivel 3.
    """
    fields: dict[str, str] = {}
    sections = re.split(r"\n?### ", body.strip())
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        label = lines[0].strip()
        value = "\n".join(lines[1:]).strip()
        if value == NO_RESPONSE:
            value = ""
        fields[label] = value
    return fields


def normalize_avatar(raw_value: str) -> str:
    key = raw_value.strip().lower()
    if key not in AVATAR_MAP:
        raise ValueError(f"Avatar no reconocido: {raw_value!r}")
    return AVATAR_MAP[key]


def load_attendees() -> list[dict]:
    if not ATTENDEES_PATH.exists():
        return []
    content = ATTENDEES_PATH.read_text(encoding="utf-8").strip()
    return json.loads(content) if content else []


def save_attendees(attendees: list[dict]) -> None:
    ATTENDEES_PATH.write_text(
        json.dumps(attendees, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        print(f"{name}={value}")
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> int:
    actor = os.environ.get("GITHUB_ACTOR", "").strip()
    body = os.environ.get("ISSUE_BODY", "")

    fields = parse_issue_body(body)
    display_name = fields.get(FIELD_NOMBRE, "").strip()
    technology = fields.get(FIELD_TECNOLOGIA, "").strip()
    avatar_raw = fields.get(FIELD_AVATAR, "").strip()

    write_output("display_name", display_name)

    if not actor or not display_name or not technology or not avatar_raw:
        print("::error::Faltan campos requeridos (actor, nombre, tecnología o avatar).")
        write_output("error", "true")
        write_output("duplicate", "false")
        return 1

    try:
        avatar = normalize_avatar(avatar_raw)
    except ValueError as exc:
        print(f"::error::{exc}")
        write_output("error", "true")
        write_output("duplicate", "false")
        return 1

    attendees = load_attendees()
    already_registered = any(
        entry.get("username", "").lower() == actor.lower() for entry in attendees
    )

    write_output("error", "false")

    if already_registered:
        print(f"El usuario '{actor}' ya está registrado. No se realizan cambios.")
        write_output("duplicate", "true")
        return 0

    attendees.append(
        {
            "username": actor,
            "name": display_name,
            "technology": technology,
            "avatar": avatar,
        }
    )
    save_attendees(attendees)

    print(f"Registro agregado para '{actor}' ({display_name}, {technology}, {avatar}).")
    write_output("duplicate", "false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
