# Repo-Guardian

[![Estado CI](https://github.com/Melissa1221/repo-guardian/workflows/CI/badge.svg)](https://github.com/Melissa1221/repo-guardian/actions)
[![Cobertura](https://img.shields.io/badge/cobertura-83%25-green)](https://github.com/Melissa1221/repo-guardian/)
[![Versión](https://img.shields.io/badge/versión-0.9.0--beta-blue)](https://github.com/Melissa1221/repo-guardian/releases)

Una herramienta CLI/TUI para auditar, reparar y re-linearizar la integridad de repositorios Git.

## Características

- **Verificación de Árbol de Merkle**: Validación criptográfica con SHA-256
- **Búsqueda Binaria de Defectos**: Uso integrado de git bisect con heurísticas personalizadas
- **Reconstrucción de Historial**: Detección de historiales reescritos usando distancia Jaro-Winkler
- **Visualización DAG**: Exportación de la estructura del repositorio como GraphML para análisis
- **Reparación Interactiva**: Interfaz TUI con seguimiento de progreso y capacidades de reparación

## Instalación

### Requisitos previos

- Python 3.8 o superior
- Git 2.20 o superior

### Método 1: Desde PyPI (recomendado)

```bash
# Instalar la última versión estable
pip install repo-guardian
```

### Método 2: Desde el repositorio (desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/Melissa1221/repo-guardian.git
cd repo-guardian

# Instalar dependencias
pip install -r requirements.txt

# Instalar en modo desarrollo
pip install -e .
```

## Uso

### Comandos Básicos

```bash
# Obtener ayuda general
guardian --help

# Obtener ayuda para un comando específico
guardian scan --help
```

### Escaneo de Repositorios

```bash
# Escanear un repositorio en busca de problemas
guardian scan /ruta/al/repo

# Escanear con múltiples hilos para mayor velocidad
guardian scan /ruta/al/repo --threads 4

# Escanear e intentar reparar problemas automáticamente
guardian scan /ruta/al/repo --repair
```

### Interfaz TUI

```bash
# Usar la interfaz gráfica en terminal
guardian scan /ruta/al/repo --tui
```

En la interfaz TUI, puedes usar:
- `↑/↓`: Navegar entre problemas
- `R`: Reparar todos los problemas
- `F`: Arreglar el problema seleccionado
- `E`: Exportar grafo del repositorio
- `S`: Mostrar estadísticas
- `PgUp/PgDn`: Desplazar la lista
- `Q`: Salir

### Exportación y Estadísticas

```bash
# Exportar DAG del repositorio a GraphML
guardian export-graph --repo /ruta/al/repo --out repo.graphml

# Obtener estadísticas básicas
guardian stats /ruta/al/repo

# Obtener estadísticas detalladas
guardian stats /ruta/al/repo --detailed
```

### Script Wrapper

El script wrapper proporciona una interfaz simplificada:

```bash
# Uso básico
scripts/scan-repo.sh /ruta/al/repo

# Uso con opciones
scripts/scan-repo.sh /ruta/al/repo --threads 4 --repair --export

# Mostrar ayuda
scripts/scan-repo.sh --help
```

### Ejemplo Completo

```bash
# Escenario: Auditar un repositorio con posibles problemas
$ guardian scan ~/proyectos/mi-repo --tui

# Resultado: Se abrirá una interfaz TUI mostrando:
# - Barra de progreso durante el escaneo
# - Lista de problemas encontrados (si hay)
# - Panel con comandos disponibles
# - Estado del repositorio en la parte inferior
```

## Completado de Comandos

Para habilitar el autocompletado de comandos:

### Bash

```bash
# Instalar argcomplete si no está instalado
pip install argcomplete

# Método 1: Activación por sesión
eval "$(register-python-argcomplete guardian)"

# Método 2: Activación permanente (añadir al .bashrc)
echo 'eval "$(register-python-argcomplete guardian)"' >> ~/.bashrc
source ~/.bashrc
```

### Zsh

```zsh
# Instalar argcomplete
pip install argcomplete

# Añadir a tu .zshrc
echo 'autoload -U bashcompinit
bashcompinit
eval "$(register-python-argcomplete guardian)"' >> ~/.zshrc

source ~/.zshrc
```

### Fish

```fish
# Instalar argcomplete
pip install argcomplete

# Añadir a tu config.fish
echo 'register-python-argcomplete --shell fish guardian | source' >> ~/.config/fish/config.fish
```

## Desarrollo

### Entorno de Desarrollo

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -r requirements.txt
```

### Linting y Pruebas

```bash
# Ejecutar linter (ruff)
ruff src tests --fix

# Ejecutar pruebas unitarias
pytest

# Ejecutar pruebas con cobertura
pytest --cov=guardian tests/

# Ejecutar pruebas en paralelo
pytest -n auto
```

### Pre-commit Hooks

El proyecto utiliza hooks de pre-commit para garantizar la calidad del código antes de cada commit:

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar los hooks
pre-commit install

# Ejecutar manualmente los hooks
pre-commit run --all-files
```

Para más detalles, consulta [docs/development-workflow.md](docs/development-workflow.md).

### Flujo de Trabajo Git

Seguimos la convención de ramas y commits semánticos:

```bash
# Crear rama para nueva funcionalidad
git checkout -b feature/RX-15-nombre-descriptivo

# Crear rama para corrección de errores
git checkout -b fix/RX-20-nombre-descriptivo

# Formato de commit
git commit -m "RX-15 feat: descripción corta de la funcionalidad"
git commit -m "RX-20 fix: solución para el problema X"
```

Tipos de commit permitidos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

### Pull Requests

Antes de crear un PR, asegúrate de:
1. Pasar todas las pruebas: `pytest -n auto`
2. No tener problemas de linting: `ruff check src tests`
3. Mantener o mejorar la cobertura: `pytest --cov=guardian`

## Estado del Proyecto

🚧 **Beta (v0.9.0)** 🚧

Este proyecto está en fase beta con todas las características principales implementadas.

## Licencia

MIT

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para instrucciones detalladas.
