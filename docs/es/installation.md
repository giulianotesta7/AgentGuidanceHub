# Instalación

AGH tiene dos partes:

- el server, que corre con Docker;
- el CLI local `agh`, que instalás en tu workstation.

Instalá el CLI primero. Después usalo para login, administración de packs/proyectos y operaciones de workspace.

## Instalar el CLI

Cloná el repo y corré el instalador:

```bash
git clone https://github.com/giulianotesta7/AgentGuidanceHub.git
cd AgentGuidanceHub
./scripts/install.sh
```

El script usa `uv tool install --force .` desde la raíz del repo. No edita archivos de arranque del shell, estado de Docker, config de AGH ni credenciales de login.

Verificá el comando:

```bash
agh --help
```

El instalador deja el binario `agh` disponible en el `PATH` del usuario. Los comandos de workspace resuelven el repo desde el directorio de trabajo actual.

## PATH troubleshooting

Si el script termina pero `agh` no aparece, agregá el bin dir de uv tool al shell:

```bash
uv tool update-shell
```

Reiniciá el shell y probá otra vez:

```bash
agh --help
```

Para ver el directorio de uv tools:

```bash
uv tool dir
```

## Desinstalar

```bash
uv tool uninstall agh
```

## Instalar el server

El server es Docker-first. Buildealo y corrélo con un volumen persistente en `/data`:

```bash
docker build -t agh .
docker run --rm -p 8912:8912 -v agh-data:/data \
  -e AGH_BOOTSTRAP_OWNER_EMAIL=owner@example.com \
  agh
```

Mirá [Operaciones](operations.md) para `/data`, logs, healthcheck, backup y upgrades.
