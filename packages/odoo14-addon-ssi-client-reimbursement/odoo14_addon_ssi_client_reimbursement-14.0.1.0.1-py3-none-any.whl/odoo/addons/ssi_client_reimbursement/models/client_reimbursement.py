# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.ssi_decorator import ssi_decorator


class ClientReimbursement(models.Model):
    _name = "client_reimbursement"
    _description = "Client Reimbursement"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_open",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.transaction_date_due",
        "mixin.transaction_untaxed_with_field",
        "mixin.transaction_total_with_field",
        "mixin.transaction_residual_with_field",
        "mixin.company_currency",
        "mixin.transaction_partner",
        "mixin.transaction_account_move_with_field",
        "mixin.account_move_single_line",
        "mixin.localdict",
        "mixin.many2one_configurator",
    ]

    # mixin.multiple_approval attributes
    _approval_from_state = "draft"
    _approval_to_state = "open"
    _approval_state = "confirm"
    _after_approved_method = "action_open"
    _automatically_insert_multiple_approval_page = True

    # mixin.transaction attributes
    _automatically_insert_view_element = True
    _statusbar_visible_label = "draft,confirm,open,done"
    _policy_field_order = [
        "confirm_ok",
        "open_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_open",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # mixin.sequence attribute
    _create_sequence_state = "open"

    # mixin.account_move attribute
    _accounting_date_field_name = "date"

    _account_id_field_name = "account_id"
    _partner_id_field_name = "partner_id"
    _analytic_account_id_field_name = "analytic_account_id"
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _date_due_field_name = "date_due"
    _need_date_due = True
    _normal_amount = "debit"

    # mixin.transaction_residual_with_field attributes
    _amount_residual_sign = 1.0

    type_id = fields.Many2one(
        comodel_name="client_reimbursement_type",
        string="Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    allowed_currency_ids = fields.Many2many(
        comodel_name="res.currency",
        string="Allowed Currencies",
        compute="_compute_allowed_currency_ids",
        store=False,
        compute_sudo=True,
    )
    # Detail
    detail_ids = fields.One2many(
        comodel_name="client_reimbursement.detail",
        inverse_name="client_reimbursement_id",
        string="Details",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # Product
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Allowed Products",
        compute="_compute_allowed_product_ids",
        store=False,
        compute_sudo=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("open", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Reject"),
        ],
        string="Status",
        default="draft",
    )

    @api.model
    def _get_policy_field(self):
        res = super(ClientReimbursement, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "open_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "cancel_ok",
            "restart_ok",
            "done_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.onchange("type_id")
    def onchange_journal_id(self):
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.journal_id.id

    @api.onchange("type_id")
    def onchange_receivable_account_id(self):
        self.account_id = False
        if self.type_id:
            self.account_id = self.type_id.receivable_account_id.id

    @api.depends("type_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.product",
                    method_selection=record.type_id.product_selection_method,
                    manual_recordset=record.type_id.product_ids,
                    domain=record.type_id.product_domain,
                    python_code=record.type_id.product_python_code,
                )
            record.allowed_product_ids = result

    @api.depends("type_id")
    def _compute_allowed_currency_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="res.currency",
                    method_selection=record.type_id.currency_selection_method,
                    manual_recordset=record.type_id.currency_ids,
                    domain=record.type_id.currency_domain,
                    python_code=record.type_id.currency_python_code,
                )
            record.allowed_currency_ids = result

    def action_import_move_line(self):
        for record in self.sudo():
            result = record._import_move_line()
        return result

    def _import_move_line(self):
        self.ensure_one()
        data = {
            "active_model": "client_reimbursement.detail",
            "active_id": self.id,
            "direction": "dr",
            "reconcile": False,
            "field_mapping": self._get_field_mapping(),
            "filter_analytic_ok": True,
            "filter_product_ok": True,
            "product_ids": [(6, 0, self.allowed_product_ids.ids)],
        }
        if self.analytic_account_id:
            data.update(
                {"analytic_account_ids": [(6, 0, [self.analytic_account_id.id])]}
            )
        else:
            analytic_accounts = self.env["account.analytic.account"].search(
                [("partner_id", "=", self.partner_id.id)]
            )
            data.update({"analytic_account_ids": [(6, 0, analytic_accounts.ids)]})

        wizard = self.env["account_move_line_selector"].create(data)
        waction = self.env.ref(
            "ssi_financial_accounting.account_move_line_selector_action"
        ).read()[0]
        waction.update(
            {
                "res_id": wizard.id,
            }
        )
        return waction

    def _get_field_mapping(self):
        result = {
            "client_reimbursement_id": "active_id",
            "account_id": "account_id",
            "name": "name",
            "price_unit": "price_unit",
            "source_move_line_id": "id",
            "product_id": "product_id",
            "uom_quantity": "quantity",
            "uom_id": "product_uom_id",
        }
        return str(result)

    @ssi_decorator.post_open_action()
    def _10_create_accounting_entry(self):
        self.ensure_one()

        if self.move_id:
            return True

        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write(
            {
                "move_line_id": ml.id,
            }
        )

        for detail in self.detail_ids:
            line_ml = detail._create_standard_ml()  # Mixin
            detail.write(
                {
                    "move_line_id": line_ml.id,
                }
            )

        self._post_standard_move()  # Mixin

        for detail in self.detail_ids:
            (detail.source_move_line_id + detail.move_line_id).reconcile()

    @ssi_decorator.post_cancel_action()
    def _delete_accounting_entry(self):
        self.ensure_one()
        for detail in self.detail_ids:
            detail.move_line_id.remove_move_reconcile()
        self._delete_standard_move()  # Mixin
