# Hoja de Ruta de Repo-Guardian

Este documento describe la hoja de ruta de desarrollo para el proyecto Repo-Guardian.

## Épicas e Historias

| Épica | Historia | Tarea | Prioridad | Etiqueta Kanban |
|------|-------|------|----------|--------------|
| **E-01 Configuración** | RX-01 Crear repo | Crear repositorio con reglas de protección | Alta | Pendiente |
| **E-01 Configuración** | RX-02 Configurar CI | Configurar GitHub Actions CI | Alta | Pendiente |
| **E-01 Configuración** | RX-03 Plantillas | Crear plantillas de issues/PR | Media | Pendiente |
| **E-01 Configuración** | RX-04 Hoja de Ruta | Crear hoja de ruta del proyecto | Media | Pendiente |
| **E-02 Funcionalidad Principal** | RX-10 Escáner de Objetos | Implementar lectura de objetos sueltos | Alta | Pendiente |
| **E-02 Funcionalidad Principal** | RX-11 Escáner de Objetos | Añadir soporte para packfiles | Alta | Pendiente |
| **E-02 Funcionalidad Principal** | RX-12 Pruebas BDD | Crear primer escenario BDD | Media | Pendiente |
| **E-02 Funcionalidad Principal** | RX-13 Diseño DAG | Crear diagrama de estructura DAG | Media | Pendiente |
| **E-02 Funcionalidad Principal** | RX-14 Constructor DAG | Implementar esqueleto del constructor DAG | Alta | Pendiente |
| **E-02 Funcionalidad Principal** | RX-15 Constructor DAG | Completar implementación DAG | Alta | Pendiente |
| **E-02 Funcionalidad Principal** | RX-16 Detector JW | Implementar detector Jaro-Winkler | Alta | Pendiente |
| **E-02 Funcionalidad Principal** | RX-17 Hook Git | Crear hook post-merge | Media | Pendiente |
| **E-02 Funcionalidad Principal** | RX-18 Versión Alpha | Crear versión v0.5.0-alpha | Alta | Pendiente |
| **E-03 Interfaz de Usuario** | RX-20 Diseño TUI | Crear wireframe TUI | Media | Pendiente |
| **E-03 Interfaz de Usuario** | RX-21 Estructura CLI | Implementar comandos CLI | Alta | Pendiente |
| **E-03 Interfaz de Usuario** | RX-22 Implementación TUI | Completar funcionalidad TUI | Alta | Pendiente |
| **E-03 Interfaz de Usuario** | RX-23 Script Envolvente | Crear wrapper scan-repo.sh | Media | Pendiente |
| **E-03 Interfaz de Usuario** | RX-24 Autocompletado | Añadir integración argcomplete | Baja | Pendiente |
| **E-03 Interfaz de Usuario** | RX-25 Versión Beta | Crear versión v0.9.0-beta | Alta | Pendiente |
| **E-04 Documentación y Final** | RX-30 Benchmarking | Crear script de benchmark | Media | Pendiente |
| **E-04 Documentación y Final** | RX-31 Documentación | Completar documentación MkDocs | Alta | Pendiente |
| **E-04 Documentación y Final** | RX-32 Publicación de Sitio | Publicar sitio de documentación | Media | Pendiente |
| **E-04 Documentación y Final** | RX-33 Versión Final | Crear versión v1.0.0 | Alta | Pendiente |
| **E-04 Documentación y Final** | RX-34 Video Demo | Crear video de demostración | Alta | Pendiente |

## Cronograma

El proyecto se completará en 8 días de la siguiente manera:

- **Día 0**: E-01 (Configuración)
- **Días 1-2**: RX-10, RX-11, RX-12 (Escáner de Objetos + BDD)
- **Días 3-4**: RX-13, RX-14, RX-15, RX-16, RX-17, RX-18 (DAG + JW + Alpha)
- **Días 5-6**: RX-20, RX-21, RX-22, RX-23, RX-24, RX-25 (UI + Beta)
- **Días 7-8**: RX-30, RX-31, RX-32, RX-33, RX-34 (Docs + Versión Final)
