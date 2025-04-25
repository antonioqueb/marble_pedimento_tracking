# models/stock_quant.py
from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char(
        string='Número de Pedimento',
        size=15,
        copy=False,
        readonly=False,
        help='Número de pedimento aduanal que originó este inventario.'
    )
