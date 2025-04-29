from odoo import models, fields, SUPERUSER_ID


class SmsExting(models.TransientModel):
    _name = 'sms.exting'
    _description = 'Sms Exting'

    name = fields.Text(string="SMS", required=True)

    def action_send_messages(self):
        partners = self.env['res.partner'].search([('twilio_chat_id', '!=', False)])
        admin = self.env.user
        print(admin)

        for partner in partners:
            channel = partner.twilio_chat_id
            if channel:
                channel.message_post(
                    body=self.name,
                    author_id=admin.partner_id.id,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                )