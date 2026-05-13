# ntfy para simulaciones SPH

## Topic actual

El proyecto usa `config/notifier_config.json`:

- proyecto: `tesis`
- topic: `sph-kevin-tesis-2026`
- base URL: `https://ntfy.sh`

En el celular hay que suscribirse a ese topic en la app ntfy.

## Corridas futuras

Para que `run_production.py` mande notificaciones nativas, no usar `--no-notify`.

Eventos nativos del runner:

- inicio de produccion;
- inicio de cada caso;
- fin de cada caso;
- error/excepcion;
- abort por tasa de fallos;
- fin de lote;
- GP re-entrenado, si aplica.

Ejemplo:

```powershell
python scripts\run_production.py --prod --matrix config\batchX.csv --max-cases N
```

## Corridas ya lanzadas con `--no-notify`

Si una corrida ya esta viva con `--no-notify`, usar watcher externo:

```powershell
python scripts\watch_production_ntfy.py --project tesis --poll-seconds 60 --heartbeat-minutes 120 --exit-on-complete
```

O en background:

```powershell
$stdout='data\logs\production_ntfy_watch_stdout.log'
$stderr='data\logs\production_ntfy_watch_stderr.log'
$args=@('scripts\watch_production_ntfy.py','--project','tesis','--poll-seconds','60','--heartbeat-minutes','120','--exit-on-complete')
Start-Process -FilePath 'python' -ArgumentList $args -WorkingDirectory 'C:\Users\Admin\Desktop\SPH-Tesis' -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden
```

Eventos del watcher externo:

- monitor activo;
- inicio/cambio de caso detectado por `production_status.json`;
- fin de caso detectado en `production_*.log`;
- errores/abort;
- heartbeat opcional;
- fin de lote.

Logs:

- `data/logs/production_ntfy_watch_stdout.log`
- `data/logs/production_ntfy_watch_stderr.log`
- `data/logs/production_ntfy_watch_YYYYMMDD_HHMMSS.log`

## Prueba manual

```powershell
python scripts\notifier.py notify "SPH ntfy test" "Mensaje de prueba desde WS" --project tesis --priority default --tags bell
```

## Nota metodologica

Las notificaciones son observabilidad operacional. No cambian la simulacion, no clasifican casos y no reemplazan `data/production_status.json`, logs, SQLite ni exports livianos.
