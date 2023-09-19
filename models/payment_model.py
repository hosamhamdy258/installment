# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InstallmentPayment(models.Model):
    _name = "installment.payment"
    _description = "Installment Payments"

    installment_id = fields.Many2one(
        "installment.installment",
        string=_("Installment"),
        required=True,
        ondelete="cascade",
    )

    amount = fields.Float(string=_("Amount"), digits=(10, 2), required=True)
    payment_date = fields.Date(string=_("Payment Date"), default=fields.Date.today())

    @api.constrains("amount")
    def _check_amount(self):
        if self.amount <= 0:
            raise ValidationError(_("The amount must be positive number"))
        if self.amount > self.installment_id.remaining_amount + self.amount:
            raise ValidationError(_("Payment amount is more than remaining amount"))

    @api.constrains("installment_id")
    def _check_installment_state(self):
        if self.installment_id.state == "draft":
            raise ValidationError(_("Can't Add Payments to draft installments"))
