# Workspace

Un workspace es un repo git linkeado a un proyecto AGH. El repo recibe los packs asignados a ese proyecto.

## Comandos

| Comando | Qué hace | Escribe archivos? |
|---------|----------|-------------------|
| `agh sync` | Matchea el git remote con un proyecto AGH y escribe `.agh/project.toml`. | Sí |
| `agh pull --dry-run` | Pide el plan al server y descarga archivos en memoria. | No |
| `agh pull` | Aplica instrucciones y skills, refresca `.agh-cache/packs/` y escribe `.agh/lock.toml`. | Sí |
| `agh pull --force` | Reemplaza bloques AGH o skill targets en conflicto. | Sí |
| `agh agent` | Muestra si los paths de Claude Code/OpenCode parecen disponibles. | No |

## Flujo de pull

```text
1. Read .agh/project.toml
2. Ask the server what this project should use
3. Download pack files through relative /api/v1/... URLs
4. Check each checksum
5. Apply instructions and skills
6. Write .agh/lock.toml
```

AGH escribe el lockfile solo después de actualizar los archivos del repo.

## Las instrucciones usan markers

`AGENTS.md` y `CLAUDE.md` pueden contener texto propio más bloques administrados por AGH. AGH solo actualiza el bloque que administra.

```md
<!-- AGH-BEGIN pack="<pack-ref>" artifact="instructions/AGENTS.md" checksum="sha256:..." -->
Project instructions from AGH live here.
<!-- AGH-END pack="<pack-ref>" -->
```

Si editás dentro del bloque, el próximo `agh pull` sale con código de conflicto `3`. Usá `agh pull --force` cuando quieras que AGH reemplace ese bloque.

## Las skills quedan limpias

Las skills no usan markers AGH. AGH las escribe o linkea en los paths que los agents ya esperan:

```text
.claude/skills/<skill>/SKILL.md
.opencode/skills/<skill>/SKILL.md
```

AGH intenta un symlink relativo a `.agh-cache/packs/...`. Si el sistema operativo rechaza symlinks, AGH copia el archivo. El lockfile registra qué pasó:

```toml
mode = "symlink" # or mode = "copy"
source = ".agh-cache/packs/<domain>/<name>/<version>/skills/<skill>/SKILL.md"
```

AGH solo escribe estos skill targets en el MVP:

- `.claude/skills/<skill>/SKILL.md`
- `.opencode/skills/<skill>/SKILL.md`

No escribe paths de Cursor, Codex, Pi ni paths globales de agents.

## Cache y lockfile

| Path | Propósito | Commit? |
|------|-----------|---------|
| `.agh/project.toml` | Linkea el repo a un proyecto AGH. | Sí |
| `.agh/lock.toml` | Registra versiones, checksums, source paths y placement modes. | Sí |
| `.agh-cache/packs/` | Archivos de pack descargados. AGH puede reconstruirlo. | No |
| `.claude/skills/`, `.opencode/skills/` | Skill targets generados. Commitelos solo si tu equipo quiere revisarlos en Git. | Decisión del equipo |

Agregá esto a `.gitignore`:

```gitignore
.agh-cache/
```

Después de un pull exitoso sin `--dry-run`, AGH muestra un hint si el repo no ignora `.agh-cache/`.

Si los skill targets son symlinks, un clone nuevo necesita refrescar el workspace para reconstruir `.agh-cache/packs/` antes de que esos links resuelvan.

Si este repo tiene un cache viejo pre-release en `.agh/packs/`, se puede borrar después de correr un pull actual.

## Exit codes

| Código | Significado |
|--------|-------------|
| `0` | Éxito o sin cambios. |
| `1` | Falla runtime/API/download. |
| `2` | Validación local o manifest mal formado. |
| `3` | Conflicto. |
| `4` | Falla de autenticación/autorización. |
| `5` | Workspace no linkeado; corré `agh sync`. |
