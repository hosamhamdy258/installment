# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PaymentRegister(models.TransientModel):
    _name = "installment.payment.wizard"
    _inherit = "installment.payment"
    _description = "Register Installment Payment"

    def action_confirm_payment(self):
        self.env["installment.payment"].create(
            {
                "installment_id": self.installment_id.id,
                "payment_date": self.payment_date,
                "amount": self.amount,
            }
        )
        return {"type": "ir.actions.act_window_close"}
