# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ClientReimbursementType(models.Model):
    _name = "client_reimbursement_type"
    _description = "Client Reimbursement Type"
    _inherit = ["mixin.master_data"]

    # Accounting
    journal_id = fields.Many2one(
        comodel_name="account.journal", string="Journal", required=True
    )
    receivable_account_id = fields.Many2one(
        comodel_name="account.account", string="Payable Account", required=True
    )
    product_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Product Selection Method",
        required=True,
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="rel_client_reimbursement_type_2_product",
        column1="type_id",
        column2="product_id",
        string="Products",
    )
    product_domain = fields.Text(default="[]", string="Product Domain")
    product_python_code = fields.Text(
        default="result = []", string="Product Python Code"
    )
    # Currency
    currency_selection_method = fields.Selection(
        default="domain",
        selection=[("manual", "Manual"), ("domain", "Domain"), ("code", "Python Code")],
        string="Currency Selection Method",
        required=True,
    )
    currency_ids = fields.Many2many(
        comodel_name="res.currency",
        relation="rel_client_reimbursement_type_2_currency",
        column1="type_id",
        column2="currency_id",
        string="Currencies",
    )
    currency_domain = fields.Text(default="[]", string="Currency Domain")
    currency_python_code = fields.Text(
        default="result = []", string="Currency Python Code"
    )
