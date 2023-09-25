# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ClientReimbursementDetail(models.Model):
    _name = "client_reimbursement.detail"
    _description = "Client Reimbursement - Detail"
    _inherit = [
        "mixin.product_line_account",
        "mixin.account_move_single_line_with_field",
    ]

    # Accounting Entry Mixin
    _move_id_field_name = "move_id"
    _account_id_field_name = "account_id"
    _partner_id_field_name = "partner_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"
    _amount_currency_field_name = "price_subtotal"
    _company_id_field_name = "company_id"
    _date_field_name = "date"
    _label_field_name = "name"
    _product_id_field_name = "product_id"
    _uom_id_field_name = "uom_id"
    _quantity_field_name = "uom_quantity"
    _price_unit_field_name = "price_unit"
    _normal_amount = "credit"

    client_reimbursement_id = fields.Many2one(
        comodel_name="client_reimbursement",
        string="# Client Reimbursement",
        required=True,
        ondelete="cascade",
    )

    # Related to header
    # Needed for convinience

    move_id = fields.Many2one(
        related="client_reimbursement_id.move_id",
    )
    currency_id = fields.Many2one(
        related="client_reimbursement_id.currency_id",
    )
    company_id = fields.Many2one(related="client_reimbursement_id.company_id")
    company_currency_id = fields.Many2one(
        related="client_reimbursement_id.company_currency_id"
    )
    partner_id = fields.Many2one(related="client_reimbursement_id.partner_id")
    date = fields.Date(related="client_reimbursement_id.date")
