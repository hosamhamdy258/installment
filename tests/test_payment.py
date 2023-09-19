from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPaymentModel(TransactionCase):
    def setUp(self):
        super().setUp()
        self.installment_model = self.env["installment.installment"]
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.journal = self.env["account.journal"].search([("name", "=", "Bank")])
        self.account = self.env["account.account"].search([("name", "=", "Bank")])

    def test_create_payment(self):
        installment = self.installment_model.create(
            {
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
            }
        )
        installment.open()
        payment = self.env["installment.payment"].create(
            {
                "installment_id": installment.id,
                "amount": installment.amount / 2,
            }
        )
        self.assertEqual(payment.payment_date, date.today())
        self.assertEqual(payment.installment_id.state, "open")

    def test_check_amount(self):
        installment = self.installment_model.create(
            {
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
            }
        )
        installment.open()
        with self.assertRaises(ValidationError):
            self.env["installment.payment"].create(
                {
                    "installment_id": installment.id,
                    "amount": -1,
                }
            )
        with self.assertRaises(ValidationError):
            self.env["installment.payment"].create(
                {
                    "installment_id": installment.id,
                    "amount": installment.amount + 1,
                }
            )

    def test_check_installment_state(self):
        with self.assertRaises(ValidationError):
            installment = self.installment_model.create(
                {
                    "customer_id": self.partner.id,
                    "journal_id": self.journal.id,
                    "account_id": self.account.id,
                    "amount": 10,
                }
            )
            self.env["installment.payment"].create(
                {
                    "installment_id": installment.id,
                    "amount": installment.amount / 2,
                }
            )
