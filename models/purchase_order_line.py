from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)
