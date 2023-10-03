# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class installment(models.Model):
    _name = _("installment.installment")
    _description = _("installment manager")

    name = fields.Char(
        string=_("Name"), readonly=True, copy=False, default=lambda self: _("New")
    )
    reference = fields.Char(string=_("Reference"))
    state = fields.Selection(
        string=_("State"),
        selection=[("draft", _("Draft")), ("open", _("Open")), ("paid", _("Paid"))],
        default="draft",
        readonly=True,
    )

    date = fields.Date(string=_("Date"), default=fields.Date.today())

    analytic_account_id = fields.Many2one(
        "account.analytic.account", string=_("Analytic Account")
    )
    analytic_tags_ids = fields.Many2many(
        "account.account.tag", string=_("Analytic Tags")
    )

    amount = fields.Float(string=_("Amount"), digits=(10, 2), required=True)
    notes = fields.Text(string=_("Notes"))
    active = fields.Boolean(string=_("Active"), default=True)

    customer_id = fields.Many2one("res.partner", string=_("Customer"), required=True)
    journal_id = fields.Many2one("account.journal", string=_("Journal"), required=True)
    account_id = fields.Many2one("account.account", string=_("Account"), required=True)

    account_move_id = fields.One2many(
        "account.move", "installment_id", string=_("Account Moves")
    )

    payment_state = fields.Selection(
        selection=lambda self: self.env["account.move"]
        ._fields["payment_state"]
        .selection,
        string=_("Payment Status"),
        store=True,
        readonly=True,
        copy=False,
        compute="_compute_payment_state",
    )
    payments = fields.Binary(
        compute="_compute_payments",
        exportable=False,
        string=_("Payments"),
    )

    remaining_amount = fields.Float(
        string=_("Remaining Amount"),
        compute="_compute_amount",
        store=True,
        digits=(10, 2),
    )

    @api.depends("account_move_id.amount_residual")
    def _compute_amount(self):
        for invoice in self:
            invoice.remaining_amount = invoice.account_move_id.amount_residual

    @api.depends("account_move_id.invoice_payments_widget")
    def _compute_payments(self):
        for invoice in self:
            invoice.payments = invoice.account_move_id.invoice_payments_widget

    @api.depends("account_move_id.payment_state")
    def _compute_payment_state(self):
        for invoice in self:
            invoice.payment_state = invoice.account_move_id.payment_state or "not_paid"
            if invoice.payment_state == "paid":
                invoice.state = "paid"
            elif invoice.payment_state == "partial":
                invoice.state = "open"

    @api.constrains("amount")
    def positive_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("The amount must be positive number"))

    def open(self):
        for invoice in self:
            if invoice.state == "draft":
                move = self.env["account.move"].create(
                    {
                        "partner_id": invoice.customer_id.id,
                        "journal_id": invoice.journal_id.id,
                        "ref": invoice.reference,
                        "installment_id": invoice.id,
                        "invoice_date": invoice.date,
                        "move_type": "out_invoice",
                        "invoice_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": "Installment Invoice",
                                    "account_id": invoice.account_id.id,
                                    "quantity": 1,
                                    "price_unit": invoice.amount,
                                    "tax_ids": [],
                                },
                            )
                        ],
                    }
                )

                invoice.account_move_id.action_post()
                invoice.name = move.name
                invoice.state = "open"

    def settlement(self):
        for invoice in self:
            if invoice.state == "open":
                remaining_amount = invoice.remaining_amount

                move_vals = {
                    "partner_id": invoice.customer_id.id,
                    "journal_id": invoice.journal_id.id,
                    "ref": "Settlement for " + invoice.name,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Settlement for " + invoice.name,
                                "account_id": invoice.account_id.id,
                                "debit": remaining_amount,
                                "credit": 0.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "Settlement for " + invoice.name,
                                "account_id": 6,  # ReceivableAccount
                                "debit": 0.0,
                                "credit": remaining_amount,
                            },
                        ),
                    ],
                }

                move = self.env["account.move"].create(move_vals)
                move.action_post()

                invoice_lines = invoice.account_move_id.line_ids
                settlement_lines = move.line_ids
                for invoice_line in invoice_lines:
                    for settlement_line in settlement_lines:
                        if invoice_line.account_id == settlement_line.account_id:
                            invoice.account_move_id.js_assign_outstanding_line(
                                settlement_line.id
                            )

    def invoice(self):
        for invoice in self:
            return invoice.customer_id.action_view_partner_invoices()

    def payment(self):
        for invoice in self:
            return {
                "name": _("Register Payment"),
                "res_model": "account.payment.register",
                "view_mode": "form",
                "context": {
                    "active_model": "account.move",
                    "active_ids": invoice.account_move_id.ids,
                    "dont_redirect_to_payments": True,
                },
                "target": "new",
                "type": "ir.actions.act_window",
            }
        return True


class AccountMove(models.Model):
    _inherit = "account.move"

    installment_id = fields.Many2one(
        "installment.installment",
        string=_("installment"),
        ondelete="restrict",
        copy=False,
        readonly=True,
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    installment_id = fields.Many2one("installment.installment", string=_("installment"))
