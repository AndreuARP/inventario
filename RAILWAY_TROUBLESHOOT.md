# Solución para errores de Railway

## Error de pip install

Si recibes este error:
```
process "/bin/bash -ol pipefail -c pip install --upgrade pip" did not complete successfully: exit code: 1
```

## Soluciones implementadas:

### 1. Dockerfile personalizado (RECOMENDADO)
- Creado `Dockerfile` con instalación directa
- Usa Python 3.11 slim oficial
- Instalación simple sin conflictos

### 2. nixpacks.toml actualizado
- Agregado `--break-system-packages` para Nix
- Versiones específicas de paquetes
- Configuración optimizada

### 3. Archivos alternativos
- `railway_requirements.txt` como backup
- `railway.json` simplificado

## Pasos para solucionar:

### Opción 1: Usar Dockerfile (Más estable)
1. Railway detectará automáticamente el `Dockerfile`
2. Usará Docker build en lugar de Nixpacks
3. Instalación más confiable

### Opción 2: Variables de entorno Railway
En Railway Dashboard, añadir:
```
NIXPACKS_BUILD_CMD=python -m pip install streamlit pandas paramiko schedule requests --break-system-packages
```

### Opción 3: Forzar Nixpacks actualizado
1. Borrar `Dockerfile` temporalmente
2. Railway usará `nixpacks.toml` actualizado
3. Con `--break-system-packages` debería funcionar

## Archivos de configuración disponibles:

- `Dockerfile` - Docker build (más estable)
- `nixpacks.toml` - Nixpacks con fixes
- `railway_requirements.txt` - Requirements backup
- `railway.json` - Configuración simplificada

## Recomendación:

**Usar Dockerfile** - Es la opción más estable y confiable para Railway.

Railway detectará automáticamente el Dockerfile y lo usará en lugar de Nixpacks, evitando los conflictos de pip.