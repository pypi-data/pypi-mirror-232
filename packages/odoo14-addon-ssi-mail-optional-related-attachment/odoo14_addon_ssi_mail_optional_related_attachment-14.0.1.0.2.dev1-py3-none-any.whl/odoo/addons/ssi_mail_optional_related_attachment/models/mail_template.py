# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.exceptions import UserError


class MailTemplate(models.Model):
    _name = "mail.template"
    _inherit = "mail.template"

    related_attachment_category_ids = fields.One2many(
        string="Related Attachment Categories To Be Sent",
        comodel_name="mail.template_related_attachment_category",
        inverse_name="template_id",
    )

    def generate_email(self, res_ids, fields):
        _super = super(MailTemplate, self)
        results = _super.generate_email(res_ids, fields)
        if self.related_attachment_category_ids:
            try:
                record = self.env[results["model"]].browse(results["res_id"])
                related_attachments = record.related_attachment_ids
            except Exception:
                error_msg = (
                    "Object %s is not inherited from mixin.related_attachment"
                    % (results["model"])
                )
                raise UserError(str(error_msg))
            else:
                for category in self.related_attachment_category_ids:
                    attachments = related_attachments.filtered(
                        lambda r: r.category_id.id == category.category_id.id
                    )
                    if len(attachments) > 0:
                        sent_ok = False
                        if (
                            category.sent_option == "verified"
                            and attachments[0].verified
                        ):
                            sent_ok = True
                        elif (
                            category.sent_option == "not_verfied"
                            and not attachments[0].verified
                        ):
                            sent_ok = True
                        elif category.sent_option == "any":
                            sent_ok = True

                        if sent_ok:
                            results["attachment_ids"].append(
                                attachments[0].attachment_id.id
                            )
        return results
