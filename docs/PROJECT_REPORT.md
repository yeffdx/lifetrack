# LifeTrack — documento técnico de apoyo

## Portada editable

- Institución: pendiente de completar.
- Curso: pendiente de completar.
- Integrantes: pendiente de completar; no se infieren nombres ni aportaciones.
- Fecha: pendiente de completar.

## Problema y objetivo

La organización personal suele quedar dividida entre listas, hábitos y metas sin una lectura común de progreso. LifeTrack centraliza registros locales y calcula indicadores reproducibles para que una persona vea qué ocurrió, sin atribuir causas ni inventar productividad.

El objetivo general es implementar una aplicación web mantenible que gestione esos registros y los transforme en indicadores verificables. Los objetivos específicos son administrar tareas, calcular consistencia de hábitos, medir objetivos cuantificables y visualizar datos persistidos.

## Arquitectura y flujo de datos

`Formulario → ruta Flask → servicio/validación → modelos SQLAlchemy → SQLite → analítica Pandas/NumPy → plantilla/Plotly`

La Application Factory evita configuración global implícita. Los modelos almacenan estado; los servicios son el único punto de reglas de negocio; las rutas coordinan HTTP; el módulo analítico no escribe datos. Esta composición aplica SRP y mantiene las dependencias pequeñas.

## Paradigmas utilizados

- Orientado a objetos: `Task`, `Habit`, `Goal` y sus registros asociados encapsulan entidad y comportamiento derivado, como `scheduled_on` y `reached_target`.
- Funcional: la preparación de DataFrames, agregaciones y construcción de indicadores recibe colecciones y devuelve resultados sin cambiar la base de datos.
- Composición: rutas consumen servicios y analítica, sin herencias artificiales ni patrones decorativos.

## Diseño de datos

`Task` tiene muchos `TaskEvent`; `Habit` tiene muchos `HabitCheckin`; `Goal` tiene muchos `GoalUpdate`. Las tres relaciones se borran en cascada para evitar registros huérfanos. El calendario no se persiste: combina fechas existentes de las tres entidades.

## Procesamiento y análisis

Pandas normaliza fechas y agrupa finalizaciones por día y día de semana. NumPy calcula la media de cumplimiento entre hábitos activos. Los valores ausentes se representan como DataFrames vacíos y activan estados vacíos de interfaz. Las fórmulas exactas están en el README.

## Estrategia de pruebas

Las pruebas cubren creación y transición de tareas, validaciones, rachas y cumplimiento de hábitos, progreso creciente/decreciente de metas, agregados analíticos y una ruta esencial. Cada caso usa SQLite temporal, no datos personales ni datos ficticios de producción.

## Limitaciones y exposición

Esta primera versión no autentica usuarios, no sincroniza con calendarios externos y no proporciona causalidad ni predicción. Para defender el proyecto: explicar la separación de capas, las fórmulas, por qué un día omitido rompe una racha, y que todas las visualizaciones se derivan de SQLite.

No se incluyen conclusiones cuantitativas: dependen de los registros que una persona introduzca y de la ejecución real de pruebas.
