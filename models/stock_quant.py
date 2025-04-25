# models/stock_quant.py
from odoo import models, fields
import re

def _pretty_ped(v):
    d = re.sub(r'\D', '', v or '')
    return f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else v


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char(
        string='Número de Pedimento',
        size=18,
        copy=False,
        readonly=False,
        help='Número de pedimento aduanal que originó este inventario.'
    )

    # Mostrar siempre formateado en la vista (lectura)
    def read(self, fields=None, load='_classic_read'):
        res = super().read(fields=fields, load=load)
        if not fields or 'pedimento_number' in fields:
            for rec in res:
                if rec.get('pedimento_number'):
                    rec['pedimento_number'] = _pretty_ped(rec['pedimento_number'])
        return res
