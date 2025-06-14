from odoo import models, fields

class TiendanubeConfig(models.Model):
    _name = 'tiendanube.config'
    _description = 'Configuración Tiendanube'

    name = fields.Char(string='Nombre')
    client_id = fields.Char(string='Client ID')
    client_secret = fields.Char(string='Client Secret')
    redirect_uri = fields.Char(string='Redirect URI')
    authorization_code = fields.Char(string='Authorization Code')
    access_token = fields.Char(string='Access Token')
    refresh_token = fields.Char(string='Refresh Token')
    token_expiry = fields.Datetime(string='Expiración del Token')
    state = fields.Selection([
        ('disconnected', 'Desconectado'),
        ('pending', 'Pendiente de autorización'),
        ('connected', 'Conectado')
    ], string='Estado', default='disconnected')

    def action_test_oauth(self):
        # Acción de prueba, puedes personalizarla luego
        return True