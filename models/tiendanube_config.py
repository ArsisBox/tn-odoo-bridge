from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import secrets
import urllib.parse

_logger = logging.getLogger(__name__)

class TiendanubeConfig(models.Model):
    _name = 'tiendanube.config'
    _description = 'Configuración Tiendanube'

    name = fields.Char(string='Nombre', required=True)
    client_id = fields.Char(string='Client ID (App ID de Tiendanube)') # Clarificar que es el App ID
    client_secret = fields.Char(string='Client Secret')
    redirect_uri = fields.Char(string='Redirect URI', readonly=True, 
                               default='https://vps-4729448-x.dattaweb.com/tiendanube_connector_test/oauth_callback', 
                               required=True)
    authorization_code = fields.Char(string='Authorization Code', readonly=True, copy=False)
    access_token = fields.Char(string='Access Token', readonly=True, copy=False)
    
    # No se menciona refresh_token en la documentación, y los tokens no expiran por tiempo.
    # refresh_token = fields.Char(string='Refresh Token', readonly=True, copy=False) 
    
    # Si la API devuelve 'expires_in', podemos guardarlo, pero no es para un refresco activo.
    token_expiry = fields.Datetime(string='Fecha de "Expiración" (Obtención)', readonly=True, copy=False) 
    
    tiendanube_user_id = fields.Char(string='Tiendanube User ID (ID de Tienda)', readonly=True, copy=False) # NUEVO CAMPO

    state = fields.Selection([
        ('disconnected', 'Desconectado'),
        ('pending', 'Pendiente de autorización'),
        ('connected', 'Conectado'),
        ('error', 'Error de Conexión')
    ], string='Estado', default='disconnected', readonly=True, copy=False)
    tiendanube_api_url = fields.Char(string='API URL Base', default='https://api.tiendanube.com/v1/')
    oauth_state_value = fields.Char(string='OAuth State Temp', readonly=True, copy=False)

    def action_connect_tiendanube(self):
        self.ensure_one()
        if not self.client_id or not self.redirect_uri:
            raise UserError("Client ID (App ID de Tiendanube) y Redirect URI son necesarios para conectar.")

        generated_state = secrets.token_urlsafe(32)
        self.write({'oauth_state_value': generated_state, 'state': 'pending'})

        authorization_base_url = f"https://www.tiendanube.com/apps/{self.client_id}/authorize"
        
        # --- SCOPES DEFINIDOS SEGÚN LA DOCUMENTACIÓN DE TIENDANUBE ---
        # Para el objetivo inicial de conectarse y realizar una consulta simple de órdenes:
        scopes = "read_orders" # MODIFICADO

        params = {
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scopes,
            'state': generated_state,
        }
        
        authorization_url = f"{authorization_base_url}?{urllib.parse.urlencode(params)}"
        _logger.info("Redirigiendo a Tiendanube para autorización: %s", authorization_url)

        return {
            'type': 'ir.actions.act_url',
            'url': authorization_url,
            'target': 'self',
        }

    # ... (método action_test_oauth sin cambios por ahora) ...
    def action_test_oauth(self):
        self.ensure_one()
        _logger.info("Prueba de conexión para '%s'. Estado: %s", self.name, self.state)
        message = f"Configuración: {self.name}\nEstado: {self.state}"
        if self.access_token:
            message += f"\nAccess Token: Presente\nTiendanube User ID: {self.tiendanube_user_id or 'No guardado'}"
        else:
            message += "\nAccess Token: Ausente"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Prueba Conexión',
                'message': message,
                'sticky': False,
                'type': 'info',
            }
        }