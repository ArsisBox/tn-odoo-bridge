import json
import logging
import requests 
import werkzeug.utils
from datetime import datetime, timedelta 

from odoo import http, fields 
from odoo.http import request
from odoo.exceptions import UserError, AccessError 

_logger = logging.getLogger(__name__)

class TiendanubeOAuthController(http.Controller):

    @http.route('/tiendanube_connector_test/oauth_callback', type='http', auth='user', website=True, csrf=False)
    def tiendanube_oauth_callback(self, **kwargs):
        _logger.info("Tiendanube OAuth Callback recibido con params: %s", kwargs)
        
        received_code = kwargs.get('code')
        received_state = kwargs.get('state')

        if not received_code or not received_state:
            _logger.error("Callback de Tiendanube sin código o estado. Code: %s, State: %s", received_code, received_state)
            return request.render("http_routing.http_error", {'status_code': 'Error', 'status_message': 'Respuesta inválida de Tiendanube.'})

        config_model = request.env['tiendanube.config'].sudo() 
        config = config_model.search([('oauth_state_value', '=', received_state)], limit=1)

        if not config:
            _logger.error("No se encontró configuración de Tiendanube para el estado OAuth: %s", received_state)
            return request.render("http_routing.http_error", {'status_code': 'Error', 'status_message': 'Estado OAuth inválido o expirado.'})
        
        config.write({'oauth_state_value': False}) # Limpiar el state

        # URL del Token de Tiendanube
        token_url = "https://www.tiendanube.com/apps/authorize/token" 
        
        payload = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'grant_type': 'authorization_code', # Práctica estándar de OAuth2
            'code': received_code,
            'redirect_uri': config.redirect_uri, # Práctica estándar de OAuth2
        }
        
        _logger.info("Solicitando access token de Tiendanube. URL: %s, Payload: %s", token_url, payload)

        try:
            response = requests.post(token_url, data=payload, timeout=20) 
            response.raise_for_status() 
            token_data = response.json()
            _logger.info("Respuesta de token de Tiendanube: %s", token_data)

            access_token = token_data.get('access_token')
            tiendanube_user_id = token_data.get('user_id') # Extraer user_id
            # scope_received = token_data.get('scope') # Scope concedido

            if access_token and tiendanube_user_id: # Asegurarse de que ambos estén presentes
                vals_to_write = {
                    'access_token': access_token,
                    'authorization_code': received_code, 
                    'tiendanube_user_id': str(tiendanube_user_id), # Guardar user_id
                    # 'scope_conceded': scope_received, # Podrías guardar el scope concedido si quieres
                    'state': 'connected',
                    # Como los tokens no expiran, podemos usar token_expiry para la fecha de obtención
                    'token_expiry': fields.Datetime.now() 
                }
                # La documentación no menciona 'expires_in' ni 'refresh_token' en la respuesta del token.
                
                config.write(vals_to_write)
                _logger.info("Conexión con Tiendanube exitosa para config: %s", config.name)
                
            else:
                error_description = token_data.get('error_description', 'Access token o User ID no encontrado en la respuesta.')
                _logger.error("Error al obtener access token/user_id de Tiendanube: %s. Respuesta completa: %s", error_description, token_data)
                config.write({'state': 'error'})
                return request.render("http_routing.http_error", {'status_code': 'Error de Autenticación', 'status_message': error_description})

        except requests.exceptions.HTTPError as e:
            _logger.error("Error HTTP solicitando access token de Tiendanube: %s. Respuesta: %s", e, e.response.text if e.response else "Sin respuesta")
            config.write({'state': 'error'})
            return request.render("http_routing.http_error", {'status_code': 'Error de Servidor Tiendanube', 'status_message': f"Error: {e.response.status_code}. Detalle: {e.response.text if e.response else ''}"})
        except requests.exceptions.RequestException as e:
            _logger.error("Error de red solicitando access token de Tiendanube: %s", e)
            config.write({'state': 'error'})
            return request.render("http_routing.http_error", {'status_code': 'Error de Red', 'status_message': 'No se pudo conectar con el servidor de Tiendanube.'})
        except Exception as e:
            _logger.exception("Error inesperado durante el intercambio de token con Tiendanube:")
            config.write({'state': 'error'})
            return request.render("http_routing.http_error", {'status_code': 'Error Inesperado', 'status_message': 'Ocurrió un error procesando la respuesta de Tiendanube.'})

        action_id = request.env.ref('tn_odoo_bridge.action_tiendanube_config').id
        menu = request.env['ir.ui.menu'].search([('action', '=', f'ir.actions.act_window,{action_id}')], limit=1)
        menu_id_param = f"&menu_id={menu.id}" if menu else ""
            
        redirect_url = f"/web#id={config.id}&action={action_id}&model=tiendanube.config&view_type=form{menu_id_param}"
        return werkzeug.utils.redirect(redirect_url)