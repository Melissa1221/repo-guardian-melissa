# Repo-Guardian

[![Estado CI](https://github.com/username/repo-guardian/workflows/CI/badge.svg)](https://github.com/username/repo-guardian/actions)
[![Cobertura](https://img.shields.io/badge/cobertura-0%25-red)](https://github.com/username/repo-guardian/)
[![Versión](https://img.shields.io/badge/versión-0.1.0-blue)](https://github.com/username/repo-guardian/releases)

Una herramienta CLI/TUI para auditar, reparar y re-linearizar la integridad de repositorios Git.

## Características (Próximamente)

- **Verificación de Árbol de Merkle**: Validación criptográfica con SHA-256
- **Búsqueda Binaria de Defectos**: Uso integrado de git bisect con heurísticas personalizadas
- **Reconstrucción de Historial**: Detección de historiales reescritos usando distancia Jaro-Winkler
- **Visualización DAG**: Exportación de la estructura del repositorio como GraphML para análisis
- **Reparación Interactiva**: Interfaz TUI con seguimiento de progreso y capacidades de reparación

## Instalación

```bash
# Próximamente
pip install repo-guardian
```

## Uso

```bash
# Escanear un repositorio en busca de problemas
guardian scan /ruta/al/repo

# Exportar DAG del repositorio a GraphML
guardian export-graph --out repo.graphml

# Obtener estadísticas del repositorio
guardian stats /ruta/al/repo

# Reparar repositorio corrupto
guardian repair /ruta/al/repo
```

## Estado del Proyecto

🚧 **En Construcción** 🚧

Este proyecto está en desarrollo activo. Vuelve pronto para ver actualizaciones.

## Licencia

MIT

## Desarrollo

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para instrucciones de desarrollo. 