## Odoo Developer Task

You are required to create a module in Odoo version 15 which handles customer installments and payments. Below are the module specification.

#### note : bold lines are extra features

1. Model
   - Name: installment.installment
   - Fields:
     - Name: Char. Readonly
     - Reference: Char
     - **Active: Boolean**
     - State: Selection = (draft, open , paid) **default="draft"**
     - Date: Date. Default = today
     - Customer: Many2one. Required
     - Journal: Many2one. Required
     - Account: Many2one. Required
     - Analytic account: Many2one
     - Analytic tags: Many2many
     - Amount: Float. Required, positive
     - Notes: Text
     - **remaining amount**
2. Menus
   - Installments: Main menu
   - Customer installments: Sub menu under the Installments menu
3. Views
   - Tree
   - Form
     - Add a tab in the form in which holds a list of all payments that were created.
     - **Add ribbon for Archived invoices**
   - Kanban
   - Search
     - **filter open invoices by default and grouped by each customer**
4. Buttons
   - Open:
     - Creates a customer invoice and generates a sequence for the Name field.
   - Payment:
     - Prompt the user with a wizard by which the user can insert a payment of partial amount or full amount of the requested amount, make sure the State is set to "paid" upon reaching the full amount.
     - **payment is allowed only when state is open**
   - Settlement:
     - Settles the installment with the remaining amount and then set the State to "paid"
5. Access Rights
   - User: Has access to self created entries.
     - **use user demouser pw demo123**
   - Manager: Has access to all entries.
6. Smart button
   - Invoice: Visible only to the Manager group

- Notes:
  - The relationship fields are to be linked with their respective models.
  - Delete and edit is only allowed in "draft" State.
- Bonus:
  Create Pivot and Graph view for the model.

- Extra
  - **Tests**
  - **demo data**
  - **Translation**
  - **Script to extract/replace Translation in i18n folder**
  - **keyboard shortcuts for all added buttons**
