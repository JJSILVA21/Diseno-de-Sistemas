# ReservaU — PSet 2

Este proyecto amplía la implementación de ReservaU realizada en PSet 1.

La implementación se desarrollará dentro de la carpeta `implementacion/`. Parte del código de PSet 1 y agrega las reglas de sedes, reservas recurrentes, bloqueos, suspensión y concurrencia.

El sistema permitirá crear reservas regulares para estudiantes y reservas de equipo oficial para capitanes. Cada tipo de reserva tendrá su propia política de cancelación.

Las sedes Campus Norte y Campus Sur tendrán sus propias reglas de horario y su propio canal de notificación. De esta forma, no se podrán mezclar las reglas de una sede con las de otra.

Las reservas recurrentes permitirán a un capitán reservar la misma cancha y franja entre dos y ocho semanas. La operación será todo o nada: si una semana tiene conflicto, no se creará ninguna reserva.

Los bloqueos administrativos podrán clonarse para aplicarse a distintas canchas y fechas. Se utilizará una copia profunda para que cambiar el equipo de un bloqueo no afecte la plantilla ni otros bloqueos.

La configuración del sistema se mantendrá en una única instancia. Allí estarán las ventanas de cancelación, el límite de no-shows, los días de suspensión y las reglas de prioridad. Esto evita repetir valores en diferentes partes del código, aunque requiere cuidado porque es un estado compartido.

El sistema protegerá la confirmación de reservas con un bloqueo en la sección crítica. Así, dos solicitudes simultáneas para la misma cancha, fecha y franja solo podrán producir una reserva confirmada.

La simulación mostrará reservas en ambas sedes, rechazos por horario, reservas recurrentes, cancelaciones, suspensión por no-shows, bloqueos y solicitudes simultáneas.

## Ejecución

```bash
cd psets/pset-02/implementacion
docker build -t reservau-v2 .
docker run --rm reservau-v2
```