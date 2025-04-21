from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)
