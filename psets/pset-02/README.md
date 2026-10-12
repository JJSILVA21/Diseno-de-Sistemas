# ReservaU — PSet 2

Este proyecto extiende la solución de ReservaU realizada en el PSet 1.

La implementación incluye reservas regulares para estudiantes, reservas de equipos oficiales para capitanes, reservas recurrentes, bloqueos administrativos, suspensión por no-shows, reglas por sede y protección contra reservas simultáneas.

## Ejecución

Desde la raíz del repositorio:

```bash
cd "psets/pset-02/implementación"
docker build -t reservau-v2 .
docker run --rm reservau-v2
```

## Patrones utilizados

| Patrón o decisión | Requerimiento que lo justifica | Problema que resuelve | Clases y métodos |
|---|---|---|---|
| Factory Method | RF-10, RF-17, RF-18 y RF-19 | Crea una reserva regular o de equipo oficial según el tipo de solicitante y asigna su política de cancelación. | `FabricaReservas`, `CreadorReservaRegular`, `CreadorReservaEquipo` |
| Abstract Factory | RF-34, RF-35, RF-36 y RNF-06 | Evita combinar validadores y notificadores de sedes diferentes. | `FabricaSedeNorte`, `FabricaSedeSur`, `FabricaSedes` |
| Builder | RF-23, RF-24 y RF-25 | Construye una reserva recurrente con datos obligatorios y opcionales. | `ReservaRecurrenteBuilder` |
| Prototype | RF-30, RF-31, RF-32, RF-33 y RNF-07 | Replica una plantilla de bloqueo en varias canchas y fechas. | `Bloqueo.clonar()` |
| Singleton | RNF-05 | Mantiene las reglas configurables en una sola instancia. | `ConfiguracionReservaU.obtener_instancia()` |
| Strategy | RF-05, RF-06, RF-17, RF-18 y RF-19 | Permite aplicar reglas diferentes de prioridad y cancelación sin condicionales dentro de `Reserva`. | `ReglaPrioridad`, `PoliticaCancelacion` |
| Facade | RF-08, RF-10, RF-23, RF-25, RF-26 y RF-33 | Centraliza las operaciones principales del sistema. | `ReservaUFacade` |
| Concurrencia | RF-09 y RNF-04 | Evita que dos solicitudes simultáneas confirmen la misma cancha, fecha y franja. | `GestorReservas.confirmar_reserva()` |

## Justificación de Prototype

Se utilizó `deepcopy` al clonar un bloqueo porque el equipo que debe montarse es una lista mutable. Así, modificar el equipo de un clon no modifica la plantilla original ni los demás bloqueos clonados.

## Justificación de Singleton

La configuración guarda en un único lugar la hora de prioridad, las reglas de cancelación, el límite de no-shows y los días de suspensión. Esto facilita cambiar reglas sin buscar valores repetidos en varias clases. El costo aceptado es que se trata de un estado compartido por todo el sistema.

## Justificación de concurrencia

Se utilizó un bloqueo pesimista con `Lock` para proteger la verificación de disponibilidad y la creación de una reserva como una sola sección crítica. De esta manera, cuando dos solicitudes llegan al mismo tiempo para la misma cancha y franja, solo una puede quedar confirmada. Las consultas normales no necesitan bloquearse; el bloqueo se usa únicamente al momento de confirmar.

## Simulación

La simulación ejecuta los siguientes escenarios:

1. Reserva válida en Campus Norte y Campus Sur.
2. Rechazo por horario no permitido de la sede.
3. Reserva recurrente exitosa y otra rechazada por conflicto.
4. Cancelación de estudiante, no-show de capitán y anulación administrativa.
5. Suspensión después de tres no-shows en el mismo mes.
6. Bloqueo clonado en dos canchas y anulación de una reserva afectada.
7. Dos solicitudes simultáneas para la misma cancha y franja, con una sola reserva confirmada.