# Flujo de Desarrollo

Este documento describe el flujo de desarrollo estándar para contribuir al proyecto Repo-Guardian.

## Configuración del Entorno

### Requisitos Previos

- Python 3.8 o superior
- Git 2.20 o superior
- pip y virtualenv

### Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/Melissa1221/repo-guardian.git
cd repo-guardian

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Instalar pre-commit
pip install pre-commit
pre-commit install
```

## Hooks de Pre-commit

El proyecto utiliza hooks de pre-commit para garantizar la calidad del código antes de cada commit.

### Método 1: Script Pre-commit Manual

Hemos configurado un hook de pre-commit básico que verifica:
1. Problemas de linting con ruff (comprobación de estilo y errores de código)

Este hook se instala automáticamente en `.git/hooks/pre-commit` y se ejecuta antes de cada commit.

### Método 2: Framework Pre-commit (Recomendado)

También ofrecemos una configuración más completa usando el framework pre-commit:

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar los hooks en el repositorio local
pre-commit install

# Ejecutar manualmente los hooks en todos los archivos
pre-commit run --all-files
```

Esta configuración incluye:
- Formateador y linter ruff (con auto-fix)
- Ordenación de imports con isort
- Verificación de archivos YAML y TOML
- Detección de conflictos de merge

Para probar la funcionalidad completa, incluyendo tests, se recomienda ejecutar manualmente:
```bash
# Ejecutar pruebas unitarias
pytest

# Ejecutar pruebas con cobertura
pytest --cov=guardian
```

## Flujo de Trabajo Git

Seguimos un flujo de trabajo basado en ramas con convenciones de nomenclatura específicas:

```bash
# Crear una rama para nueva funcionalidad
git checkout -b feature/RX-15-nombre-descriptivo

# Crear una rama para corrección de errores
git checkout -b fix/RX-20-nombre-descriptivo
```

### Convención de Commits

Los mensajes de commit deben seguir este formato:

```
RX-15 feat: breve descripción del cambio

Descripción más detallada si es necesario.
```

Tipos de commit permitidos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `refactor`: Cambios en el código que no añaden funcionalidades ni corrigen errores
- `test`: Adición o modificación de pruebas
- `docs`: Cambios en la documentación
- `chore`: Cambios en el proceso de build o herramientas auxiliares

### Antes de Crear un Pull Request

1. Asegúrate de que todos los hooks de pre-commit pasen sin errores
2. Ejecuta el conjunto completo de pruebas:
   ```bash
   pytest -n auto
   ```
3. Verifica la cobertura de código:
   ```bash
   pytest --cov=guardian
   ```
4. Actualiza la documentación si has añadido o modificado funcionalidades

### Creación de Pull Request

1. Sube tu rama al repositorio remoto:
   ```bash
   git push -u origin feature/RX-15-nombre-descriptivo
   ```
2. Crea un Pull Request en GitHub
3. Completa la plantilla de PR, incluyendo:
   - Descripción de los cambios
   - Referencias a issues relacionados (ej. "Closes #15")
   - Capturas de pantalla o GIFs si es relevante
   - Información sobre la cobertura de pruebas

## CI/CD Pipeline

Nuestro pipeline de CI/CD ejecuta automáticamente las siguientes verificaciones:
1. Linting con ruff
2. Pruebas unitarias con pytest
3. Pruebas de aceptación con behave
4. Análisis de cobertura de código

Para ver el estado de estas verificaciones, visita la [página de Actions](https://github.com/Melissa1221/repo-guardian/actions) del repositorio.
