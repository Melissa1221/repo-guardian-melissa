# Corrupt Blob Test Fixture

Este fixture contiene un repositorio Git con objetos corruptos para pruebas.

## Estructura

- `objects/ab/cdef1234567890abcdef1234567890abcdef12`: Objeto blob con datos comprimidos corrompidos
- `objects/cd/ef1234567890abcdef1234567890abcdef1234`: Objeto con cabecera inválida
- `objects/ef/0123456789abcdef0123456789abcdef012345`: Objeto con desajuste de tamaño

## Patrones de Corrupción

1. **Blob corrompido**: La compresión zlib está dañada en los últimos bytes, causando error CRC.
2. **Cabecera inválida**: El formato de la cabecera no es "tipo tamaño\0", sino solo "tipo\0".
3. **Desajuste de tamaño**: El tamaño declarado en la cabecera no coincide con el contenido real.
