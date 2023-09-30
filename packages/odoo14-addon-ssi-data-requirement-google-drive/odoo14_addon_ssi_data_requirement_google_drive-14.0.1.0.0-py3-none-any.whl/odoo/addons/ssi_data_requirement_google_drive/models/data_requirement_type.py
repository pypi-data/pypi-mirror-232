# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


class DataRequirementType(models.Model):
    _name = "data_requirement_type"
    _inherit = [
        "data_requirement_type",
    ]

    google_docs_template_id = fields.Char(
        string="Google Docs Template ID",
    )
    google_docs_new_name = fields.Char(
        string="Google Docs New Name",
    )
