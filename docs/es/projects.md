# Proyectos

Un proyecto es un registro de AGH linkeado a un repositorio git. Los proyectos definen qué packs recibe un workspace durante sync y pull.

## Crear un proyecto

Usá la URL del repositorio que los developers tienen en sus git remotes:

```bash
agh project create "<project-name>" --repo-url <git-repo-url>
```

Ejemplo:

```bash
agh project create "Agent Guidance Hub" \
  --repo-url https://github.com/giulianotesta7/AgentGuidanceHub.git
```

Salida de ejemplo:

```text
Created project Agent Guidance Hub (prj_...).
Repo: github.com/giulianotesta7/AgentGuidanceHub
Status: active
```

## Listar e inspeccionar proyectos

```bash
agh project list
agh project get prj_...
```

La lista usa headers tipados:

```text
PROJECT_ID            NAME                REPO                                           STATUS
prj_...               Agent Guidance Hub  github.com/giulianotesta7/AgentGuidanceHub     active
```

`agh project get` muestra un proyecto:

```text
Project: Agent Guidance Hub
Project ID: prj_...
Repo: github.com/giulianotesta7/AgentGuidanceHub
Status: active
```

## Actualizar o desactivar un proyecto

```bash
agh project update prj_... --name "App API"
agh project update prj_... --repo-url git@github.com:acme/app-api.git
agh project delete prj_...
```

`delete` desactiva el proyecto. No borra registros históricos del server.

## Asignar packs

Un project pack assignment conecta un proyecto con un pack reference.

```bash
agh project pack add prj_... acme/onboarding@latest
```

Ejemplo:

```text
Assigned acme/onboarding@latest to project prj_...
Resolved: acme/onboarding@1.0.0
Assignment: asn_...
```

`asn_...` es el assignment id. Identifica la relación proyecto-pack, no el pack.

## Listar assignments

```bash
agh project pack list prj_...
```

Ejemplo:

```text
ASSIGNMENT_ID          PACK_REF                RESOLVED               POSITION  STATUS
asn_...                acme/onboarding@latest  acme/onboarding@1.0.0  0         active
```

## Actualizar o quitar assignments

```bash
agh project pack update prj_... asn_... --pack-ref acme/onboarding@1.0.0
agh project pack update prj_... asn_... --position 10
agh project pack update prj_... asn_... --inactive
agh project pack remove prj_... asn_...
```

## Cómo funciona `latest`

Usá una versión exacta cuando querés que un proyecto quede pinneado en el momento de asignar:

```bash
agh project pack add prj_... acme/onboarding@1.0.0
```

Usá `latest` cuando el proyecto debe resolver a la versión publicada más nueva durante la generación del manifest:

```bash
agh project pack add prj_... acme/onboarding@latest
```

Durante el pull del workspace, AGH escribe la versión concreta resuelta y el checksum en `.agh/lock.toml`.

## Flujo de workspace

Después de configurar el proyecto, ejecutá el flujo de workspace en el repo destino:

```bash
agh sync
agh pull --dry-run
agh pull
```

Mirá [Workspace](workspace.md) para markers, skills, `.agh/lock.toml` y `.agh-cache/`.
