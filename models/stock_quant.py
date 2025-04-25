# models/stock_quant.py
from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    # CHANGED: quitamos readonly y añadimos ayuda + tracking
    pedimento_number = fields.Char(
        string='Número de Pedimento',
        size=15,
        copy=False,
        readonly=False,
        tracking=True,
        help='Número de pedimento aduanal que originó este inventario.'
    )
