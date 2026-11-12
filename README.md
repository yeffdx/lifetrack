# LifeTrack

Aplicación web local para organizar tareas, seguir hábitos, registrar objetivos medibles y analizar los registros reales. No carga datos de ejemplo ni genera recomendaciones predictivas.

## Alcance de esta versión

- Tareas: crear, buscar, filtrar, editar, completar, reabrir y eliminar; cada cambio de finalización queda en historial.
- Hábitos: frecuencia diaria o días concretos, registros de cumplimiento, racha actual y máxima, y porcentaje de consistencia.
- Objetivos: valor inicial, valor objetivo, unidad, mediciones y evolución persistente.
- Calendario mensual: vencimientos, hábitos programados y fechas objetivo.
- Dashboard y análisis: indicadores de SQLite procesados con Pandas y NumPy, y visualizaciones interactivas Plotly.

Es una versión local monousuario. No implementa cuentas ni sincronización externa porque no son necesarias para el alcance inicial; si se agregan cuentas, cada consulta deberá aislar los datos por usuario.

## Instalación y ejecución

Se requiere Python 3.11 o superior. En PowerShell, abre la carpeta del proyecto. Comprueba primero el intérprete:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Abre `http://127.0.0.1:5000`; detén el servidor con Ctrl+C. En siguientes sesiones solo ejecuta el último comando. No es necesario activar el entorno ni cambiar la política de PowerShell. Si `python` no existe, instala Python 3.11 o superior antes de crear `.venv`.

`ModuleNotFoundError: No module named 'flask'` indica que el intérprete usado no encuentra Flask. Instala con el comando de `.venv` anterior y ejecuta con ese mismo Python; no uses un `pip` global. Puedes verificarlo con `.\.venv\Scripts\python.exe -m pip check`. Para conservar las sesiones entre reinicios, define una clave privada estable en `LIFETRACK_SECRET_KEY`; si falta, la aplicación genera una clave aleatoria al arrancar.

La base de datos SQLite se crea automáticamente como `lifetrack.sqlite3`; no se versiona.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas emplean una base de datos SQLite temporal y aislada. Consulta el resultado real del comando en tu entorno; este repositorio no declara resultados no ejecutados.

Verificación realizada en Windows con Python 3.11.9: `pip check` sin incompatibilidades, 13 pruebas Pytest aprobadas y arranque de `run.py` confirmado en localhost. Las comprobaciones de apariencia (`node --test tests/appearance.test.cjs`, si dispones de Node) aprobaron 2 pruebas de cambio de tema y contraste. Los tres temas se revisaron en el navegador; los gráficos con datos no se revisaron visualmente.

## Fórmulas y supuestos

- Tareas completadas: tareas cuyo estado actual es `completed`.
- Cumplimiento de tareas: `tareas completadas / total de tareas registradas × 100`.
- Días aplicables a un hábito: días desde su inicio hasta hoy (sin días futuros) que coincidan con su frecuencia.
- Cumplimiento de hábito: `check-ins completados / días aplicables × 100`. Un día aplicable sin registro cuenta como incumplimiento.
- Racha: número de días aplicables consecutivos completados. Los días no programados no rompen una racha; uno programado sin check-in sí.
- Progreso de objetivo: `(valor actual − valor inicial) / (valor objetivo − valor inicial) × 100`. La fórmula funciona con metas crecientes y decrecientes. Los objetivos con valor inicial igual al objetivo se rechazan.

Las recomendaciones aparecen únicamente cuando existe evidencia comparable. Una menor cantidad de tareas completadas no se presenta como una causa, solo como un cambio observado.

## Arquitectura

La fábrica de aplicación registra blueprints HTTP. Los modelos SQLAlchemy representan persistencia; los servicios validan y aplican reglas de negocio; `app/analytics` contiene transformaciones de datos y cálculos sin efectos de escritura; las plantillas solo presentan resultados.

| Criterio | Evidencia en el código |
| --- | --- |
| Paradigmas | Entidades y servicios orientados a objetos; métricas y transformaciones con funciones sin escritura. |
| Diseño | Application Factory, modelos, servicios, rutas, analítica, plantillas y pruebas separados. |
| Datos | DataFrames de Pandas, limpieza de fechas, agrupaciones y `numpy.mean` para métricas agregadas. |
| Resultados | Pytest, base aislada, estados vacíos y gráficos Plotly basados en persistencia. |
| Documentación | Este README y `docs/PROJECT_REPORT.md`. |
| Exposición | Fórmulas, flujo de datos, decisiones y limitaciones documentados. |

## Seguridad y limitaciones

Las mutaciones mediante formularios requieren token CSRF, la validación ocurre en el servidor y SQLAlchemy parametriza las consultas. La clave de sesión debe proporcionarse mediante `LIFETRACK_SECRET_KEY` fuera del código. La configuración por defecto existe solo para iniciar localmente y no debe usarse en producción.

No hay autenticación, adjuntos, notificaciones ni sincronización de calendarios externos. Plotly y Bootstrap se solicitan desde CDN; para uso sin red pueden servirse localmente en una futura mejora justificada.

## Fuentes técnicas

- [Flask documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM documentation](https://docs.sqlalchemy.org/)
- [pandas documentation](https://pandas.pydata.org/docs/)
- [NumPy documentation](https://numpy.org/doc/)
- [Plotly Python documentation](https://plotly.com/python/)
- [pytest documentation](https://docs.pytest.org/)
