from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_sid = fields.Char(string='Account sid', config_parameter='messenger.account_sid')
    auth_token = fields.Char(string='Auth token', config_parameter='messenger.auth_token')
