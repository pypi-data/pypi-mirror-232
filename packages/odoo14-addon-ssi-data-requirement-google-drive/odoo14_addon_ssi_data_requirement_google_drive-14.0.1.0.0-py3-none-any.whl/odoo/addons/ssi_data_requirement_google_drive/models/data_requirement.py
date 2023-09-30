# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class DataRequirement(models.Model):
    _name = "data_requirement"
    _inherit = [
        "data_requirement",
    ]

    google_docs_folder_id = fields.Char(
        string="Google Docs Folder ID",
    )

    def action_create_google_doc(self):
        for record in self.sudo():
            result = record._create_google_doc()
        return result

    def _create_google_doc(self):
        self.ensure_one()
        google_docs_template_id = self._get_google_docs_template_id()
        new_google_doc_name = self._get_new_google_doc_name()
        google_docs_folder_id = self._get_google_docs_folder_id()
        gdocs_url = (
            "https://docs.google.com/spreadsheets/d/%s/copy?id=%s&title=%s&copyDestination=%s"
            % (
                google_docs_template_id,
                google_docs_template_id,
                new_google_doc_name,
                google_docs_folder_id,
            )
        )

        return {
            "name": "New Google Docs",
            "type": "ir.actions.act_url",
            "url": gdocs_url,
            "target": "new",
        }

    def _get_new_google_doc_name(self):
        self.ensure_one()

        if not self.type_id.google_docs_new_name:
            result = self.type_id.name
        else:
            result = self.type_id.google_docs_new_name

            result.replace("", "%C2%A0")

        return result

    def _get_google_docs_template_id(self):
        self.ensure_one()

        if not self.type_id.google_docs_template_id:
            error_message = """
            Context: Create new google doc from data requirement
            Database ID: %s
            Problem: No google docs template ID
            Solution: Insert google docs template ID on data requirement type
            """ % (
                self.id,
            )
            raise UserError(_(error_message))

        return self.type_id.google_docs_template_id

    def _get_google_docs_folder_id(self):
        self.ensure_one()

        if not self.google_docs_folder_id:
            error_message = """
            Context: Create new google doc from data requirement
            Database ID: %s
            Problem: No google docs folder ID
            Solution: Insert google docs folder ID on data requirement
            """ % (
                self.id,
            )
            raise UserError(_(error_message))

        return self.google_docs_folder_id
