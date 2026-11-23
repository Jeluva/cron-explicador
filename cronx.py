#!/usr/bin/env python3
"""cronx: valida, explica y proyecta expresiones cron de 5 campos."""
import argparse
import sys
from datetime import datetime, timedelta

RANGOS = [("minuto", 0, 59), ("hora", 0, 23), ("dia del mes", 1, 31),
          ("mes", 1, 12), ("dia de la semana", 0, 6)]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_EN = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
DIAS = ["domingo", "lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
DIAS_EN = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
ALIAS = {"@hourly": "0 * * * *", "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
         "@weekly": "0 0 * * 0", "@monthly": "0 0 1 * *", "@yearly": "0 0 1 1 *",
         "@annually": "0 0 1 1 *"}


class CronError(ValueError):
    pass


def _valor(txt, idx):
    nombre, lo, hi = RANGOS[idx]
    t = txt.lower()
    if idx == 3 and t in MESES_EN:
        return MESES_EN.index(t) + 1
    if idx == 4 and t in DIAS_EN:
        return DIAS_EN.index(t)
    if not t.isdigit():
        raise CronError(f"valor invalido '{txt}' en {nombre}")
    v = int(t)
    if idx == 4 and v == 7:
        v = 0
    if not lo <= v <= hi:
        raise CronError(f"{nombre}: {v} fuera de rango {lo}-{hi}")
    return v


def parsear_campo(campo, idx):
    """Devuelve (set de valores, es_comodin)."""
    _, lo, hi = RANGOS[idx]
    if idx == 4:
        hi = 6
    valores = set()
    for parte in campo.split(","):
        if not parte:
            raise CronError(f"campo vacio en {RANGOS[idx][0]}")
        base, _, paso = parte.partition("/")
        paso = int(paso) if paso.isdigit() else (1 if not _ else None)
        if paso is None or paso < 1:
            raise CronError(f"paso invalido en '{parte}'")
        if base == "*":
            a, b = lo, hi
        elif "-" in base:
            x, y = base.split("-", 1)
            a, b = _valor(x, idx), _valor(y, idx)
            if a > b:
                raise CronError(f"rango invertido '{base}'")
        else:
            a = _valor(base, idx)
            b = hi if _ else a
        valores.update(range(a, b + 1, paso))
    return valores, campo == "*"


def parsear(expr):
    expr = ALIAS.get(expr.strip().lower(), expr)
    partes = expr.split()
    if len(partes) != 5:
        raise CronError("se esperan 5 campos: min hora dia mes dia-semana")
    return [parsear_campo(p, i) for i, p in enumerate(partes)], partes


def coincide(campos, dt):
    (mi, _), (ho, _), (dm, dm_w), (me, _), (ds, ds_w) = campos
    if dt.minute not in mi or dt.hour not in ho or dt.month not in me:
        return False
    dow = (dt.weekday() + 1) % 7
    # regla de cron: si ambos dia-mes y dia-semana estan restringidos, vale cualquiera
    if not dm_w and not ds_w:
        return dt.day in dm or dow in ds
    return dt.day in dm and dow in ds


def proximas(expr, desde, n=5):
    campos, _ = parsear(expr)
    dt = desde.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limite = dt + timedelta(days=366 * 5)
    res = []
    while len(res) < n and dt < limite:
        if dt.month not in campos[3][0]:
            dt = (dt.replace(day=1, hour=0, minute=0) + timedelta(days=32)).replace(day=1)
            continue
        if dt.hour not in campos[1][0]:
            dt = dt.replace(minute=0) + timedelta(hours=1)
            continue
        if coincide(campos, dt):
            res.append(dt)
        dt += timedelta(minutes=1)
    return res


def _lista(vals, idx):
    nombres = {3: MESES, 4: DIAS}.get(idx)
    off = 1 if idx == 3 else 0
    return ", ".join(nombres[v - off] if nombres else str(v) for v in sorted(vals))


def explicar(expr):
    campos, partes = parsear(expr)
    out = []
    for (vals, comodin), (nombre, lo, hi), i in zip(campos, RANGOS, range(5)):
        if comodin:
            out.append(f"{nombre}: todos")
        else:
            out.append(f"{nombre}: {_lista(vals, i)}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cronx", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre in ("validar", "explicar", "proximas"):
        p = sub.add_parser(nombre)
        p.add_argument("expr", help='ej: "*/15 9-17 * * mon-fri"')
        if nombre == "proximas":
            p.add_argument("-n", type=int, default=5)
            p.add_argument("--desde", help="AAAA-MM-DD HH:MM (default: ahora)")
    p = sub.add_parser("diff", help="compara dos expresiones en los proximos N disparos")
    p.add_argument("a"); p.add_argument("b"); p.add_argument("-n", type=int, default=10)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "validar":
            parsear(a.expr); print("ok")
        elif a.cmd == "explicar":
            print("\n".join(explicar(a.expr)))
        elif a.cmd == "proximas":
            d = datetime.strptime(a.desde, "%Y-%m-%d %H:%M") if a.desde else datetime.now()
            for dt in proximas(a.expr, d, a.n):
                print(dt.strftime("%Y-%m-%d %H:%M (%a)"))
        else:
            d = datetime.now()
            for e in (a.a, a.b):
                print(e, "->", ", ".join(x.strftime("%m-%d %H:%M") for x in proximas(e, d, a.n)))
            ia = {x for x in proximas(a.a, d, a.n)}
            ib = {x for x in proximas(a.b, d, a.n)}
            print("coinciden:", len(ia & ib))
    except (CronError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
