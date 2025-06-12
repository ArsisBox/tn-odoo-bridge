# Memoria técnica para asistentes de IA – Estado de infraestructura y restauración

## Contexto general

- **Proyecto:** Tiendanube Odoo Bridge
- **Repositorio:** https://github.com/ArsisBox/tn-odoo-bridge.git
- **Desarrollo local:** Windows + Docker Desktop
- **Producción:** VPS (Dattaweb) con Docker

---

## Estructura de carpetas local

- Módulo Odoo:  
  `C:\developer\arsis\mantelitos\tn-odoo-bridge`
- Entorno Docker:  
  `C:\developer\arsis\mantelitos\odoo_docker_local`
- Addons locales:  
  `C:\developer\arsis\mantelitos\odoo_docker_local\extra-addons`
- Backup local de base de datos:  
  `C:\developer\arsis\mantelitos\odoo_docker_local\MantelitosDB.backup`
- Filestore local (adjuntos):  
  `C:\developer\arsis\mantelitos\odoo_docker_local\odoo\filestore\MantelitosDB`

---

## Docker Compose (resumen relevante)

- **Servicio db (PostgreSQL):**
  - Volumen: `odoo-db-data:/var/lib/postgresql/data`
- **Servicio odoo:**
  - Volúmenes:
    - `./extra-addons:/mnt/extra-addons`
    - `./odoo:/etc/odoo`
    - `odoo-web-data:/var/lib/odoo`
    - `./odoo/filestore:/var/lib/odoo/filestore`
  - Puertos: 8069, 8072

---

## VPS (producción)

- Staging: `/root/app/staging/tn_odoo_bridge`
- Producción: `/root/app/extra-addons/tn_odoo_bridge`
- Backup en VPS: `/root/MantelitosDB.backup`
- Filestore en VPS: `/app/web-data/filestore/MantelitosDB`

---

## Flujo de restauración aplicado

1. **Restaurar base de datos:**
   - Copiar backup desde VPS a local.
   - Restaurar con `pg_restore` dentro del contenedor PostgreSQL.
2. **Restaurar filestore:**
   - Copiar carpeta filestore desde VPS a local.
   - Asegurar mapeo en `docker-compose.yml`:  
     `./odoo/filestore:/var/lib/odoo/filestore`
   - Reiniciar contenedores.
3. **Verificar en Odoo:**
   - Acceso a http://localhost:8069
   - Módulo `tn-odoo-bridge` visible y listo para instalar.

---

## Archivo .env relevante

```
HOST=db
USER=odoo
PASSWORD=rupe53TEku
POSTGRES_PASSWORD=rupe53TEku
POSTGRES_DB=MantelitosDB
POSTGRES_USER=odoo
```

---

## Notas para IA

- Este archivo es para uso de asistentes de IA: usar siempre estos datos como referencia.
- No repetir preguntas sobre rutas, nombres, flujos o comandos ya definidos aquí.
- Si la sesión se reinicia, leer este archivo para restaurar el contexto y continuar el flujo sin pérdida de información.

---

## Leyes de interacción para asistentes de IA

- **No pasar comandos juntos ni en bloque**:  
  Siempre entregar los comandos de terminal de a uno, en bloques separados, para que el usuario pueda copiarlos y ejecutarlos individualmente usando el botón "escribir en terminal directo".

---