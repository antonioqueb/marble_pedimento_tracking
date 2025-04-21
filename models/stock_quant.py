from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', related='move_line_id.pedimento_number', store=True)
