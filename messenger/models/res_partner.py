from odoo import models, fields, api
from twilio.rest import Client

class ResPartner(models.Model):
    _inherit = 'res.partner'
    twilio_chat_id = fields.Many2one('discuss.channel', string="Twilio Chat", help="Linked chat for Twilio messages")


    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)

        if not partner.twilio_chat_id:
            channel = self.env['discuss.channel'].create({
                'name': f"{partner.name}",
                'channel_type': 'channel',
            })

            if self.env.user.partner_id:
                channel.add_members(partner_ids=[self.env.user.partner_id.id])
            if partner:
                channel.add_members(partner_ids=[partner.id])

            partner.twilio_chat_id = channel.id

        return partner


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    def message_post(self, **kwargs):
        result = super(DiscussChannel, self).message_post(**kwargs)

        if self.channel_type == 'channel':
            current_user_partner = self.env.user.partner_id
            channel_members = self.channel_member_ids.mapped('partner_id') - current_user_partner

            if self.env.user and not self.env.user._is_public():
                external_partners = channel_members.filtered(lambda p: not p.user_ids)
                from_number = external_partners[0].mobile

                mail_message = self.env['mail.message'].browse(result.id)
                attachments = mail_message.attachment_ids

                supported_ext = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4']
                media_urls = []

                for attachment in attachments:
                    if any(attachment.name.lower().endswith(ext) for ext in supported_ext):
                        url = f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/public/attachment/{attachment.id}"
                        media_urls.append(url)

                if from_number:
                    message_body = kwargs.get('body')

                    account_sid = self.env['ir.config_parameter'].sudo().get_param('messenger.account_sid')
                    auth_token = self.env['ir.config_parameter'].sudo().get_param('messenger.auth_token')
                    client = Client(account_sid, auth_token)

                    try:
                        message_data = {
                            'from_': '+17408727638',
                            'to': from_number,
                            'body': message_body,
                        }

                        if media_urls:
                            message_data['media_url'] = media_urls

                        twilio_message = client.messages.create(**message_data)

                    except Exception as e:
                        print(f"Ошибка при отправке SMS: {e}")
            else:
                print("В канале нет других участников")

        return result

