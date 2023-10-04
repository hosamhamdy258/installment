# -*- coding: utf-8 -*-
{
    "name": "installment",
    "summary": """
    handles customer installments and payments
    """,
    "description": """
    user friendly module to handle all required operations for clients payments
    """,
    "author": "Hossam Hamdy",
    "website": "https://github.com/hosamhamdy258",
    "category": "Services/installment",
    "version": "0.1",
    "depends": ["base", "account"],
    "license": "LGPL-3",
    "data": [
        "security/installment_security.xml",
        "security/ir.model.access.csv",
        "views/installment_form.xml",
        "views/installment_kanban.xml",
        "views/installment_search.xml",
        "views/installment_tree.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
