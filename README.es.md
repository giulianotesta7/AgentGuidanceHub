<div align="center">

# Agent Guidance Hub (AGH)

<p><strong>Guidance para agentes de código, self-hosted.</strong></p>

<p>
  <a href="https://pypi.org/project/agh/"><img alt="PyPI" src="https://img.shields.io/pypi/v/agh?color=1f6feb"></a>
  <a href="https://github.com/giulianotesta7/AgentGuidanceHub/pkgs/container/agent-guidance-hub"><img alt="GHCR" src="https://img.shields.io/badge/ghcr-agent--guidance--hub-1f6feb"></a>
  <a href="https://github.com/giulianotesta7/AgentGuidanceHub/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/giulianotesta7/AgentGuidanceHub/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/giulianotesta7/AgentGuidanceHub/releases"><img alt="Release" src="https://img.shields.io/github/v/release/giulianotesta7/AgentGuidanceHub"></a>
</p>

<p>
  <a href="#instalar">instalar</a> · <a href="#quick-start">quick start</a> · <a href="#como-funciona-agh">cómo funciona</a> · <a href="#operaciones-del-server">operaciones</a> · <a href="#desarrollo">desarrollo</a> · <a href="README.md">english</a>
</p>

</div>

[English](README.md)

---

![Demo de pull de workspace en AGH](assets/agh-workspace-demo.gif)

**AGH le da a un equipo un lugar para publicar, versionar, asignar y pullear instrucciones y skills reutilizables de agentes a sus repos.**

Usalo cuando el guidance de agentes necesita la misma disciplina que la infraestructura: cambios reproducibles, ownership claro y un server propio. AGH está en una etapa temprana, es Docker-first y se publica como paquete PyPI, fórmula Homebrew e imagen server en GHCR.

- **Centralizá el guidance**: publicá `AGENTS.md`, `CLAUDE.md` y archivos de skill compartidos una sola vez.
- **Versioná cada cambio**: los packages son releases SemVer inmutables asignados a proyectos.
- **Mantené repos determinísticos**: cada workspace registra `.agh/lock.toml` y aplica solo el target elegido.
- **Operalo vos**: corré el server con Docker, SQLite y storage persistente en `/data`.

---

## Instalar

Linux / macOS:

```bash
brew install giulianotesta7/tap/agh
```

o agregá el tap una vez:

```bash
brew tap giulianotesta7/tap
brew install agh
```

Windows (Scoop):

```powershell
scoop bucket add agh https://github.com/giulianotesta7/scoop-agh
scoop install agh
```

o instalá con script:

```bash
curl -fsSL https://raw.githubusercontent.com/giulianotesta7/AgentGuidanceHub/main/scripts/install.sh | sh
```

o instalá con uv:

```bash
uv tool install --force agh
```

desde un checkout:

```bash
git clone https://github.com/giulianotesta7/AgentGuidanceHub.git
cd AgentGuidanceHub
uv tool install --force .
```

probá el CLI:

```bash
agh --help
```

Levantá el server con la imagen Docker publicada:

```bash
docker compose up -d
curl http://127.0.0.1:8912/api/v1/health
```

Compose usa esta imagen por defecto:

```text
ghcr.io/giulianotesta7/agent-guidance-hub:${AGH_IMAGE_TAG:-latest}
```

Pinneá deployments de producción con un release tag:

```bash
AGH_IMAGE_TAG=0.2.0 docker compose up -d
```

## Quick start

Leé el primer token owner en el host donde corre AGH:

```bash
docker run --rm -v agh-data:/data busybox \
  cat /data/secrets/initial_owner_token
```

Configurá la URL de la instancia una vez y después logueate desde tu máquina:

```bash
agh config set <instance-url>
agh login --email owner@example.com --token "<initial-owner-token>"
```

`agh config` muestra la URL de la instancia configurada:

```bash
agh config
```

Usá `agh config clear` para borrar la URL de la instancia y `agh logout` para limpiar las credenciales sin cambiar la instancia.

Creá un proyecto con la URL que los devs usan en sus remotes de git:

```bash
agh project create "Agent Guidance Hub" \
  --git-url https://github.com/giulianotesta7/AgentGuidanceHub.git
```

Trabajá desde un repo conectado:

```bash
agh link
agh target set opencode # o: agh target set claude
agh pull --dry-run
agh pull
agh target
```

`agh target` muestra el target elegido para este workspace; usá `agh target clear` para borrar la selección del workspace o agregá `--global` para manejar el default global.

<a id="como-funciona-agh"></a>

## Cómo funciona AGH

```text
Package author ── publish ──▶ AGH server ── assign ──▶ Project
                              │                         │
                              │                         ▼
                         SQLite + /data          Repo workspace
                                                       │
                                                       ├─ AGENTS.md + .opencode/skills/
                                                       └─ CLAUDE.md + .claude/skills/
```

| Pieza | Qué hace |
|-------|----------|
| Packages | Instrucciones compartidas, skills o ambas. Las versiones publicadas son inmutables. |
| Proyectos | Un repo git más las versiones de packages que tiene que usar. |
| Workspaces | Un repo local conectado con `agh link`, un target elegido y un lockfile commiteado. |

<details>
<summary><strong>Autoría de packages</strong></summary>

Un package arranca con esta forma:

```text
my-package/
├── agh.package.toml
├── instructions/
│   ├── AGENTS.md
│   └── CLAUDE.md
└── skills/
    └── reviewer/
        └── SKILL.md
```

Creá un template:

```bash
agh package init ./my-package --domain acme --name onboarding --version 1.0.0
```

El manifest arranca así:

```toml
domain = "acme"
name = "onboarding"
version = "1.0.0"
description = "TODO"
```

Flags útiles:

- `--with-agents` crea `instructions/AGENTS.md`.
- `--with-claude` crea `instructions/CLAUDE.md`.
- `--with-skill NAME` crea `skills/NAME/SKILL.md`.

Archivos permitidos:

- `agh.package.toml`
- `instructions/AGENTS.md`
- `instructions/CLAUDE.md`
- `skills/<name>/SKILL.md`

Reglas:

- Un package puede contener instrucciones, skills o ambas.
- Tiene que incluir al menos un archivo de instrucciones o una skill.
- `version` tiene que ser SemVer exacto, como `1.0.0`.
- Las versiones publicadas son inmutables. Publicá `1.0.1` para cambios.
- No publiques `latest`. Usá `latest` solo al asignar packages a proyectos.
- Usá archivos UTF-8. No incluyas symlinks.

Publicá y listá packages:

```bash
agh package publish ./my-package
agh package list
```

Salida de publish:

```text
Published acme/onboarding@1.0.0.
Package ID: pkg_...
Checksum: sha256:...
```

</details>

<details>
<summary><strong>Asignación a proyectos</strong></summary>

Un proyecto es un registro de AGH conectado a un repo git.

```bash
agh project create "Agent Guidance Hub" \
  --git-url https://github.com/giulianotesta7/AgentGuidanceHub.git
agh project list
agh project describe prj_...
agh project update prj_... --name "App API"
agh project deactivate prj_...
agh project member list prj_...
```

Asigná packages a través de los comandos unificados de `package` con exactamente un scope de destino (`--project` o `--collection`):

```bash
agh package assign acme/onboarding@latest --project prj_...
agh package list --project prj_...
agh package describe acme/onboarding@1.0.0
agh package activate acme/onboarding@latest --project prj_...
agh package deactivate acme/onboarding@latest --project prj_...
agh package unassign acme/onboarding@latest --project prj_...
```

Las referencias de package aceptan `pkgv_...`, `domain/name@version` y `name@version` exactos. Los refs sin dominio tienen que matchear un único dominio de package; si no, AGH reporta un conflicto. Usá una versión exacta para fijar el proyecto. Usá `latest` con refs calificados por dominio cuando el proyecto tenga que resolver la versión publicada más nueva durante el pull. `package describe PACKAGE_REF@latest` resuelve a la versión SemVer más alta.

El server mantiene los ids de asignación internos: activate, deactivate y unassign buscan la asignación existente por ref de package más scope de destino. Cuando un package no está asignado, el error nombra el ref de package, el scope y el id del scope y sugiere `agh package list --<scope> <id>`.

Durante el pull del workspace, AGH escribe la versión concreta y el checksum en `.agh/lock.toml`.

</details>

<details>
<summary><strong>Administración de colecciones</strong></summary>

Las colecciones agrupan packages que contienen solo skills y que los miembros instalan con `agh skill ...`. Los owners y admins administran colecciones con los comandos `agh collection`. Estos comandos de administración están separados del flujo de consumo `agh skill ...`.

```bash
agh collection create "Team Skills" --description "Skills de review compartidas"
agh collection list
agh collection describe "Team Skills"
agh collection update "Team Skills" --name "Review Skills"
agh collection deactivate "Review Skills"
```

Los comandos de colección que toman una referencia aceptan ids `col_...` o nombres exactos de colecciones activas. Los ids canónicos omiten la resolución por nombre; los nombres exactos se resuelven a través del endpoint de colecciones activas por nombre.

Asigná packages que contienen solo skills a una colección a través de los comandos unificados de `package` con `--collection`:

```bash
agh package assign acme/reviewer@latest --collection "Team Skills"
agh package list --collection "Team Skills"
agh package activate acme/reviewer@latest --collection "Team Skills"
agh package deactivate acme/reviewer@latest --collection "Team Skills"
agh package unassign acme/reviewer@latest --collection "Team Skills"
```

Los packages de colección tienen que contener solo skills: AGH rechaza packages que tengan `instructions/AGENTS.md`, `instructions/CLAUDE.md` o ninguna skill, y el CLI muestra esa validación del servidor. Las referencias de package aceptan `pkgv_...`, `domain/name@version` y `name@version` exactos. La asignación requiere tanto la colección como la referencia del package: no hay selector interactivo, dado que solo el servidor puede validar packages de solo skills.

</details>

<details>
<summary><strong>Skills globales</strong></summary>

Las skills globales son herramientas respaldadas por colecciones e instaladas en el directorio global nativo del target elegido. Una colección es un grupo administrado por AGH de packages que contienen solo skills y que el servidor pone a disposición; las skills globales están separadas de las asignaciones de packages del workspace.

| Comando | Qué hace |
|---------|----------|
| `agh skill list` | Lista skills disponibles desde colecciones activas. |
| `agh skill install acme/commenting@latest reviewer --target opencode` | Resuelve, descarga e instala `reviewer` globalmente para el target `opencode`. |

La resolución de target para `skill install` sigue este orden: un `--target` explícito, el target del workspace (`.agh-cache/preferences.toml`), el target global y después un prompt interactivo. En modo no interactivo, AGH sale con código `2` en lugar de promptear.

Si no hay un target guardado y se omite `--target`, AGH muestra este prompt:

```text
Select the target for global skills:
```

Rutas de instalación:

- Skills globales de OpenCode: `~/.config/opencode/skills`
- Skills globales de Claude: `~/.claude/skills`

El estado de skills globales es estado local del usuario bajo `XDG_STATE_HOME/agh` o `~/.local/state/agh`; no cambia el comportamiento de `agh pull` ni `.agh/lock.toml`.

</details>

<details>
<summary><strong>Pull del workspace y estado en Git</strong></summary>

| Comando | Qué hace |
|---------|----------|
| `agh link` | Matchea el remote de git con un proyecto AGH y escribe `.agh/project.toml`. |
| `agh target` | Muestra la selección local de target actual. |
| `agh target set opencode` | Selecciona OpenCode para este workspace. |
| `agh target set claude` | Selecciona Claude Code para este workspace. |
| `agh target clear` | Borra la selección local de target del workspace. |
| `agh pull --dry-run` | Pide el plan al server sin escribir archivos del repo. |
| `agh pull` | Aplica instrucciones y skills del target elegido y escribe `.agh/lock.toml`. |
| `agh pull --force` | Reemplaza bloques AGH o skill targets en conflicto. |

No hay opción `both`. Si no hay target seleccionado, `agh pull` interactivo pregunta cuál usar. Skip sale con código `2` y no escribe nada.

Los archivos de instrucciones usan bloques administrados:

```md
<!-- AGH-BEGIN package="<package-ref>" artifact="instructions/AGENTS.md" checksum="sha256:..." -->
Las instrucciones del proyecto viven acá.
<!-- AGH-END package="<package-ref>" -->
```

Si editás dentro del bloque, el siguiente `agh pull` sale con código de conflicto `3`. Usá `agh pull --force` cuando AGH tenga que reemplazarlo.

Las skills van donde los agentes ya las buscan:

```text
.claude/skills/<skill>/SKILL.md
.opencode/skills/<skill>/SKILL.md
```

AGH intenta usar un symlink relativo a `.agh-cache/packages/...`. Si el SO rechaza symlinks, copia el archivo. El lockfile registra el modo:

```toml
[[packages]]
package_ref = "acme/onboarding@1.0.0"

[[artifacts]]
package_ref = "acme/onboarding@1.0.0"
path = "skills/reviewer/SKILL.md"
target_path = ".opencode/skills/reviewer/SKILL.md"
mode = "symlink" # o mode = "copy"
source = ".agh-cache/packages/acme/onboarding/1.0.0/skills/reviewer/SKILL.md"
```

Commiteá el estado compartido del workspace:

- `.agh/project.toml`
- `.agh/lock.toml`
- `AGENTS.md` / `CLAUDE.md` generados cuando tu equipo quiera revisarlos
- `.claude/skills/` u `.opencode/skills/` generados cuando tu equipo quiera revisar skills

No commitees estado local de cache:

```gitignore
.agh-cache/
```

AGH descarga packages en `.agh-cache/packages/` y guarda la elección de target de cada dev en `.agh-cache/preferences.toml`. Si los skill targets son symlinks, un clone nuevo necesita `agh pull` para reconstruir el cache antes de que esos links resuelvan.

Exit codes:

| Código | Significado |
|--------|-------------|
| `0` | Éxito o sin cambios. |
| `1` | Error runtime/API/download. |
| `2` | Validación local, manifest inválido o selección de target faltante/skipped. |
| `3` | Conflicto. |
| `4` | Error de autenticación/autorización. |
| `5` | Workspace sin link; corré `agh link`. |

</details>

## Operaciones del server

El primer token owner se escribe una sola vez:

```text
/data/secrets/initial_owner_token
```

Guardalo. AGH no lo vuelve a mostrar. El server guarda hashes de tokens, no tokens en texto plano.

| Rol | Uso |
|-----|-----|
| `owner` | Acceso admin completo, incluyendo ownership inicial. |
| `admin` | Gestiona usuarios, proyectos, packages y asignaciones. |
| `member` | Uso diario desde workspaces. |

Comandos admin:

```bash
agh user list
agh user create user@example.com --role admin
agh user describe user@example.com
agh user update usr_... --role member
agh user activate usr_...
agh user deactivate usr_...
agh user token rotate usr_...
agh whoami
agh logout
agh config
agh config clear
```

La rotación de tokens está anidada bajo `user`: `agh user token rotate USER_REF`.

El CLI guarda las credenciales de login localmente; `agh config` muestra solo la URL de la instancia, nunca el token.

El estado runtime vive bajo `/data`:

| Path | Uso |
|------|-----|
| `/data/agh.sqlite3` | Base SQLite. |
| `/data/packages/` | Payloads de packages publicados. |
| `/data/logs/agh.log` | Log del server. |
| `/data/secrets/initial_owner_token` | Primer owner token, creado una vez. |

La imagen deja `/data` como `agh:agh` (`10001:10001`) durante el build.
Los named volumes de Docker se inicializan desde ese árbol `/data` ya preparado en la imagen.
Los bind mounts tienen que ser escribibles previamente por UID/GID `10001:10001`; el container no repara ownership del host.

Docker run directo:

```bash
docker run --rm -p 8912:8912 -v agh-data:/data \
  -e AGH_BOOTSTRAP_OWNER_EMAIL=owner@example.com \
  ghcr.io/giulianotesta7/agent-guidance-hub:0.2.0
```

Healthcheck:

```bash
curl http://127.0.0.1:8912/api/v1/health
```

Backup mínimo:

```text
/data/agh.sqlite3
/data/packages/
/data/secrets/
```

Actualizá pinneando el siguiente image tag y reiniciando:

```bash
AGH_IMAGE_TAG=0.2.0 docker compose pull
AGH_IMAGE_TAG=0.2.0 docker compose up -d
```

## Desarrollo

```bash
uv sync
uv run pytest
uv run uvicorn agh.server.app:app --host 0.0.0.0 --port 8912
```

Los datos locales usan `.agh-data/` por defecto.

Contribución y seguridad:

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
