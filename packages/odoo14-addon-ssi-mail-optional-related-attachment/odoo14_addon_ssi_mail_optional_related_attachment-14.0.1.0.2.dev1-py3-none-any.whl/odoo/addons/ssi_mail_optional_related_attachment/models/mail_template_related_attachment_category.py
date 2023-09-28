# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MailTemplateRelatedAttachmentCategory(models.Model):
    _name = "mail.template_related_attachment_category"
    _description = "Mail Template Related Attachment Category"

    template_id = fields.Many2one(
        string="Email Template",
        comodel_name="mail.template",
        ondelete="cascade",
    )
    category_id = fields.Many2one(
        string="Category",
        comodel_name="attachment.related_attachment_category",
        ondelete="restrict",
        required=True,
    )
    sent_option = fields.Selection(
        string="Sent Option",
        selection=[
            ("not_verfied", "Not Verified"),
            ("verified", "Verified"),
            ("any", "Any"),
        ],
        required=True,
        default="verified",
    )
