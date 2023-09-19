from datetime import date, datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestInstallmentModel(TransactionCase):
    def setUp(self):
        super().setUp()
        self.installment_model = self.env["installment.installment"]
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.journal = self.env["account.journal"].search([("name", "=", "Bank")])
        self.account = self.env["account.account"].search([("name", "=", "Bank")])

    def test_create_installment(self):
        fields = self.installment_model._fields.keys()
        installment = self.installment_model.create(
            {
                "name": "test name",
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
                **self.installment_model.default_get(fields),
            }
        )

        self.assertEqual(installment.state, "draft")
        self.assertEqual(installment.name, "New")
        self.assertEqual(installment.date, date.today())
        self.assertEqual(installment.remaining_amount, 0)

    def test_positive_amount_constraint(self):
        with self.assertRaises(ValidationError):
            self.installment_model.create(
                {
                    "customer_id": self.partner.id,
                    "journal_id": self.journal.id,
                    "account_id": self.account.id,
                    "amount": -1,
                }
            )

    def test_open_installment(self):
        installment = self.installment_model.create(
            {
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
            }
        )

        installment.open()
        self.assertEqual(installment.remaining_amount, installment.amount)
        self.assertEqual(installment.state, "open")
        self.assertNotEqual(installment.name, "New")

    def test_remaining_amount_computation(self):
        installment = self.installment_model.create(
            {
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
            }
        )
        installment.open()

        self.env["installment.payment"].create(
            {
                "installment_id": installment.id,
                "amount": installment.amount / 2,
            }
        )
        self.assertEqual(installment.remaining_amount, installment.amount / 2)
        self.assertEqual(installment.state, "open")

        self.env["installment.payment"].create(
            {
                "installment_id": installment.id,
                "amount": installment.amount / 2,
            }
        )
        self.assertEqual(installment.remaining_amount, 0)
        self.assertEqual(installment.state, "paid")

    def test_settlement_installment(self):
        installment = self.installment_model.create(
            {
                "customer_id": self.partner.id,
                "journal_id": self.journal.id,
                "account_id": self.account.id,
                "amount": 10,
            }
        )
        installment.open()
        installment.settlement()
        self.assertEqual(installment.remaining_amount, 0)
        self.assertEqual(installment.state, "paid")
