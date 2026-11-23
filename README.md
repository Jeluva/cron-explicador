# cron-explicador (cronx)

Proyecto de práctica: una CLI en Python (solo biblioteca estándar, sin dependencias) para trabajar con expresiones cron de 5 campos.

## Qué hace
- `validar`: dice `ok` o el error (código de salida 1).
- `explicar`: lista qué valores toma cada campo (minuto, hora, día del mes, mes, día de la semana).
- `proximas`: calcula los próximos N disparos desde ahora o desde una fecha.
- `diff`: compara dos expresiones en sus próximos N disparos y cuenta cuántos coinciden.

Soporta `*`, listas (`1,15`), rangos (`9-17`), pasos (`*/15`, `1-30/5`), nombres (`jan`, `mon-fri`), `7` como domingo y alias (`@daily`, `@weekly`, `@monthly`, `@yearly`, `@hourly`). Si día del mes y día de la semana están ambos restringidos, dispara con cualquiera de los dos (como cron real).

## Cómo correrlo
Requiere Python 3.8+.

```bash
python3 cronx.py explicar "*/15 9-17 * * mon-fri"
python3 cronx.py proximas "30 2 1,15 * *" -n 3 --desde "2026-11-23 10:00"
python3 cronx.py diff "0 * * * *" "*/30 * * * *" -n 4
python3 cronx.py validar "61 * * * *"
```

Tests: `python3 -m unittest discover tests`

## Limitaciones
- Sin segundos ni extensiones tipo `L`, `W`, `#`.
- Sin zonas horarias: usa la hora local de la máquina.
- La explicación es una lista de valores, no una frase en lenguaje natural.
