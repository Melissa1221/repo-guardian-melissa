## Día 3: Implementación del Diseño DAG

### Completado Hoy
- Creado diagrama Mermaid en `docs/dag.mmd` mostrando la estructura DAG de commits de Git
- Documentados componentes clave del DAG:
  - Representación de vértices para commits
  - Relaciones de bordes (hijo a padre)
  - Mecanismo de cálculo del número de generación
  - Concepto de ordenamiento topológico
- Implementado el esqueleto para `dag_builder.py` con API pública completa
- Creados tests iniciales en `tests/test_dag_builder.py`

### Decisiones de Diseño
1. **Representación del Grafo**: Usando `networkx.DiGraph` como estructura de datos subyacente:
   - Nodos representan commits (identificados por su hash)
   - Bordes representan relaciones padre-hijo
   - La dirección del borde sigue el modelo de Git (hijo → padre)

2. **Número de Generación**: Calculando números de generación usando un enfoque de abajo hacia arriba:
   - GN = 0 para commits raíz (sin padres)
   - GN = max(GN de padres) + 1 para otros commits

3. **Funciones Utilitarias Adicionales**:
   - Añadido `get_commit_path` para trazar caminos desde un commit a una raíz
   - Añadido `get_common_ancestor` para encontrar bases de fusión

### Desafíos
- Determinar la forma más eficiente de analizar la información de padres del contenido de commits
- Asegurar el manejo adecuado de estructuras DAG complejas con múltiples raíces y commits de fusión
- Decidir el mejor enfoque para ordenamiento topológico con números de generación

### Próximos Pasos
- Implementar la función principal `build_graph`
- Añadir lógica para analizar información de padres de objetos commit
- Implementar cálculo de número de generación usando BFS
- Completar las funciones utilitarias restantes (find_roots, find_heads, etc.)
- Implementar completamente las pruebas con aserciones reales 