<a href="https://www.islas.org.mx/"><img src="https://www.islas.org.mx/img/logo.svg" align="right" width="256" /></a>
# Jinja Render

Base functinos to use Jinja2

Here we use the `jinja_render` module, as example, from `robinson_code` repo
# Example
This example is from [muestreo-aves-marinas-ipbc](https://bitbucket.org/IslasGECI/muestreo-aves-marinas-ipbc/src/43dba1b46b492393baa508fbbb73d3ff9ade42be/Makefile#lines-946)
``` sh
typer jinja_render run \
--report-name="time_series_results_section" \
--summary-path="tests/data/mergulo_punta.json"
```
