# Comandos de Desarrollo para Repo-Guardian

Este documento contiene todos los comandos necesarios para el desarrollo, pruebas y mantenimiento del proyecto Repo-Guardian.

## Entorno Virtual

### Crear entorno virtual
```bash
# Crear un nuevo entorno virtual
python -m venv venv

# Activar el entorno virtual (Linux/macOS)
source venv/bin/activate

# Activar el entorno virtual (Windows)
venv\Scripts\activate
```

### Instalación de dependencias
```bash
# Instalar dependencias del proyecto
pip install -r requirements.txt

# Instalar el proyecto en modo desarrollo
pip install -e .

# Actualizar herramientas
python -m pip install --upgrade pip
```

## Linting y Formateo

### Ejecutar linter
```bash
# Ejecutar ruff para lint
ruff src tests

# Ejecutar ruff y corregir automáticamente
ruff src tests --fix

# Verificar un solo archivo
ruff src/guardian/dag_builder.py
```

### Formatear código
```bash
# Formatear el código con ruff
ruff format src tests
```

## Pruebas

### Pruebas unitarias
```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas en paralelo con auto-detección de CPUs
pytest -n auto

# Ejecutar pruebas con reporte de cobertura
pytest --cov=guardian

# Ejecutar pruebas específicas
pytest tests/test_dag_builder.py

# Ejecutar pruebas en modo verboso
pytest -v tests/test_jw_detector.py

# Mostrar razones de skip
pytest -rs
```

### Pruebas BDD
```bash
# Ejecutar todas las features BDD
behave

# Ejecutar con formato de progreso
behave -f progress

# Ejecutar una feature específica
behave features/object_corruption.feature
```

## Comandos de la Aplicación

### Escaneo de repositorio
```bash
# Escanear un repositorio
guardian scan /ruta/al/repo

# Escanear con salida detallada
guardian scan /ruta/al/repo --verbose
```

### Exportación de grafo
```bash
# Exportar grafo en formato GraphML
guardian export-graph --repo /ruta/al/repo --out grafo.graphml

# Exportar en formato GEXF
guardian export-graph --repo . --out grafo.gexf --format gexf

# Exportar en formato JSON
guardian export-graph --repo . --out grafo.json --format json
```

## Integración con Git

### Hook post-merge
```bash
# Instalar el hook post-merge
cp scripts/post-merge .git/hooks/

# Hacer ejecutable el hook
chmod +x .git/hooks/post-merge
```

## CI/CD y Versionado

### Ejecutar el pipeline de CI localmente
```bash
# Ejecutar toda la verificación de CI
ruff src tests && pytest -n auto --cov=guardian && behave -f progress
```

### Crear nuevas versiones
```bash
# Crear una etiqueta de versión
git tag -a v0.5.0-alpha -m "Versión alpha 0.5.0"

# Publicar etiqueta
git push origin v0.5.0-alpha

# Listar versiones
git tag
```

## Mantenimiento

### Limpieza
```bash
# Eliminar archivos de caché de Python
find . -name "__pycache__" -type d -exec rm -rf {} +

# Eliminar archivos .pyc
find . -name "*.pyc" -delete

# Limpiar directorios de cobertura y caché
rm -rf .coverage htmlcov .pytest_cache .ruff_cache
```

### Empaquetado
```bash
# Construir paquete
python -m build

# Verificar paquete
twine check dist/*
```

## Documentación

### Generación de documentación
```bash
# Construir documentación MkDocs
mkdocs build

# Servir documentación localmente
mkdocs serve

# Publicar documentación en GitHub Pages
mkdocs gh-deploy --force
``` 