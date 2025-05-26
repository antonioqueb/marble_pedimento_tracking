# models/stock_quant.py
from odoo import models, fields, api
import re
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else d

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char(
        string='Número de Pedimento', 
        size=18, 
        copy=False,
        compute='_compute_pedimento_number',
        store=True,
        readonly=False
    )

    @api.depends('lot_id', 'location_id.usage')
    def _compute_pedimento_number(self):
        """
        Para ubicaciones de cliente, hereda el pedimento del lote desde ubicaciones internas
        """
        for quant in self:
            if quant.location_id.usage == 'customer' and quant.lot_id and not quant.pedimento_number:
                # Buscar pedimento en ubicaciones internas del mismo lote
                internal_quant = self.search([
                    ('lot_id', '=', quant.lot_id.id),
                    ('location_id.usage', 'in', ['internal', 'transit']),
                    ('pedimento_number', '!=', False)
                ], limit=1)
                if internal_quant:
                    quant.pedimento_number = internal_quant.pedimento_number

    def read(self, fields=None, load='_classic_read'):
        res = super().read(fields=fields, load=load)
        if not fields or 'pedimento_number' in fields:
            for rec in res:
                if rec.get('pedimento_number'):
                    rec['pedimento_number'] = _PRETTY(re.sub(r'\D', '', rec['pedimento_number']))
        return res