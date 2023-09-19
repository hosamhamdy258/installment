# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class installment(models.Model):
    _name = "installment.installment"
    _description = "installment manager"

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

    customer_id = fields.Many2one("res.partner", string=_("Customer"), required=True)
    journal_id = fields.Many2one("account.journal", string=_("Journal"), required=True)
    account_id = fields.Many2one("account.account", string=_("Account"), required=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string=_("Analytic Account")
    )
    analytic_tags_ids = fields.Many2many(
        "account.account.tag", string=_("Analytic Tags")
    )

    amount = fields.Float(string=_("Amount"), digits=(10, 2), required=True)
    notes = fields.Text(string=_("Notes"))
    active = fields.Boolean(string=_("Active"), default=True)

    payment_ids = fields.One2many(
        "installment.payment", "installment_id", string=_("Payments")
    )
    remaining_amount = fields.Float(
        string=_("Remaining Amount"),
        digits=(10, 2),
        compute="_compute_remaining_amount",
        store=True,
        search=True,
    )

    @api.depends("amount", "payment_ids", "state")
    def _compute_remaining_amount(self):
        for rec in self:
            if rec.state in ["open", "paid"]:
                rec.remaining_amount = rec.amount - sum(
                    [p.amount for p in rec.payment_ids]
                )
                rec._onchange_state()
            else:
                rec.remaining_amount = 0

    def _onchange_state(self):
        for rec in self:
            if rec.state != "draft":
                if rec.remaining_amount == 0 and len(rec.payment_ids) != 0:
                    rec.state = "paid"
                else:
                    rec.state = "open"

    @api.constrains("amount")
    def positive_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("The amount must be positive number"))

    def open(self):
        self["name"] = self.env["ir.sequence"].next_by_code("installment.installment")
        self.state = "open"
        return True

    def payment(self):
        return {
            "name": _("Register Payment"),
            "res_model": "installment.payment.wizard",
            "view_mode": "form",
            "target": "new",
            "type": "ir.actions.act_window",
            "context": {
                "default_installment_id": self.ids[0],
                "default_amount": self.remaining_amount,
            },
        }

    def settlement(self):
        self.env["installment.payment"].create(
            {
                "installment_id": self.ids[0],
                "payment_date": self.date,
                "amount": self.remaining_amount,
            }
        )
        return True

    def invoice(self):
        return True
