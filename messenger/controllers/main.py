from odoo import http
from odoo.http import request, Response
import requests
import base64
import urllib.parse
import logging
import json

_logger = logging.getLogger(__name__)


class TwilioWebhookController(http.Controller):

    @http.route('/twilio/sms', type='http', auth='public', methods=['POST'], csrf=False)
    def twilio_webhook(self, **post):
        print(post)
        _logger.info("Twilio POST data: %s", post)

        from_number = post.get("From")
        message_body = post.get("Body")
        media_url = post.get("MediaUrl0")

        if not from_number:
            return request.make_response(
                json.dumps({"error": "Missing required fields"}),
                headers={"Content-Type": "application/json"},
                status=400
            )

        partner = request.env["res.partner"].sudo().search([("mobile", "=", from_number)], limit=1)

        if not partner:
            return request.make_response(
                json.dumps({"error": "Partner not found"}),
                headers={"Content-Type": "application/json"},
                status=404
            )

        chat_channel = partner.twilio_chat_id
        if not chat_channel:
            return request.make_response(
                json.dumps({"error": "No chat linked for this contact"}),
                headers={"Content-Type": "application/json"},
                status=404
            )

        # message = request.env["mail.message"].sudo().create({
        #     "body": message_body,
        #     "author_id": partner.id,
        #     "model": "discuss.channel",
        #     "res_id": chat_channel.id,
        #     "message_type": "comment",
        # })
        message_vals = {
            "body": message_body or '',
            "author_id": partner.id,
            "model": "discuss.channel",
            "res_id": chat_channel.id,
            "message_type": "comment",
        }

        attachment_ids = []
        if media_url:
            try:
                # Twilio credentials
                account_sid = self.env['ir.config_parameter'].sudo().get_param('messenger.account_sid')
                auth_token = self.env['ir.config_parameter'].sudo().get_param('messenger.auth_token')

                # Fetch the image
                response = requests.get(media_url, auth=(account_sid, auth_token))
                if response.status_code == 200:
                    # Get the content type and file data
                    content_type = response.headers.get("Content-Type", "image/jpeg")
                    file_data = response.content

                    # Create an attachment in Odoo
                    attachment = http.request.env["ir.attachment"].sudo().create({
                        "name": f"Twilio_image_{partner.id}.jpg",  # Customize the name as needed
                        "datas": base64.b64encode(file_data),  # Encode the file in base64
                        "res_model": "discuss.channel",
                        "res_id": chat_channel.id,
                        "mimetype": content_type,
                    })
                    attachment_ids.append(attachment.id)
                else:
                    _logger.error("Failed to fetch media from Twilio: %s", response.status_code)
            except Exception as e:
                _logger.error("Error processing Twilio media: %s", str(e))

            # Add attachment IDs to the message if any
        if attachment_ids:
            message_vals["attachment_ids"] = [(6, 0, attachment_ids)]

            # Create the message
        message = http.request.env["mail.message"].sudo().create(message_vals)

        return request.make_response(
            json.dumps({"success": True, "message_id": message.id}),
            headers={"Content-Type": "application/json"},
            status=200
        )


class PublicAttachmentController(http.Controller):

    @http.route(['/public/attachment/<int:attachment_id>'], type='http', auth='public')
    def public_attachment_download(self, attachment_id, **kwargs):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()

        # Кодировка имени файла по стандарту RFC 5987
        filename = attachment.name or 'file'
        encoded_filename = urllib.parse.quote(filename)

        # Чтение файла
        file_content = attachment.sudo().raw or b''
        content_type = attachment.mimetype or 'application/octet-stream'

        headers = [
            ('Content-Type', content_type),
            ('Content-Disposition', f"inline; filename*=utf-8''{encoded_filename}"),
        ]

        return Response(file_content, headers=headers)