# instadump

## Requisitos
1. Cuenta de IG business.
2. Crear app de tipo `business` en https://developers.facebook.com/apps
3. Crear un system user en https://business.facebook.com/settings/system-users
    - Linkear app y cuenta de IG
    - Generar access token (sin expiración) con los permisos:
        - instagram_basic
        - business_management
        - pages_show_list
        - instagram_manage_insights
        - pages_read_engagement
        - pages_read_user_content

```bash
pip install instadump
```
## Crawl
Exportar variables de entorno (ver ejemplo `.env.example`), y luego utilizar el subcommand `crawl`

```bash
❯ instadump crawl --help
Usage: instadump crawl [OPTIONS] COMMAND [ARGS]...

Options:
  --ig-connected-id TEXT          [env var: IG_CONNECTED_ID; required]
  --ig-access-token TEXT          [env var: IG_ACCESS_TOKEN; required]
  -c, --config TEXT               Path to YAML config file
  -u, --username TEXT             Instagram username
  -m, --max-items INTEGER         Maximum number of items to download
  --incremental / --no-incremental
                                  Incremental download  [default: incremental]
  --period TEXT                   Period time, ie 7m, 4w, 10d, etc
  --start-datetime TEXT           Since datetime
  --end-datetime TEXT             Since datetime
  --help                          Show this message and exit.
```

> `--incremental` solo descarga nuevos posts. `--no-incremental` reemplaza el JSON dump y descarga todo nuevamente.

## Download media
Las URLs de media suelen expirar al poco tiempo, con el subcomand `download-media` se puede descargar del JSON obtenido anteriormente.

```bash
❯ instadump download-media --help
Usage: instadump download-media [OPTIONS] FILENAME COMMAND [ARGS]...

Arguments:
  FILENAME  [required]

Options:
  --field TEXT                    [default: media_url]
  --media-type [IMAGE|VIDEO|CAROUSEL_ALBUM]
  --help                          Show this message and exit.
```