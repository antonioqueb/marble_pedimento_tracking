# models/stock_quant.py
from odoo import models, fields
import re
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else d

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char(string='Número de Pedimento', size=18, copy=False)

    def read(self, fields=None, load='_classic_read'):
        res = super().read(fields=fields, load=load)
        if not fields or 'pedimento_number' in fields:
            for rec in res:
                if rec.get('pedimento_number'):
                    rec['pedimento_number'] = _PRETTY(re.sub(r'\D', '', rec['pedimento_number']))
        return res
