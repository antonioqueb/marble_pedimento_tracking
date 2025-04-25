# models/stock_move.py
from odoo import models, fields, api
import re, logging
_logger = logging.getLogger(__name__)

_CLEAN  = lambda v: re.sub(r'\D', '', v or '')
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else d

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ---- UX en formulario ----
    @api.onchange('pedimento_number')
    def _onchange_ped(self):
        if self.pedimento_number is None:
            return
        digits = _CLEAN(self.pedimento_number)[:15]
        self.pedimento_number = _PRETTY(digits) if len(digits) == 15 else digits

    # ---- propaga a líneas nuevas ----
    def _prepare_move_line_vals(self, *a, **kw):
        vals = super()._prepare_move_line_vals(*a, **kw)
        vals['pedimento_number'] = self.pedimento_number
        return vals

    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = move.pedimento_number
        return res

    # ---- guarda con formato y propaga a líneas existentes ----
    def write(self, vals):
        if 'pedimento_number' in vals:
            d = _CLEAN(vals['pedimento_number'])
            vals['pedimento_number'] = _PRETTY(d) if len(d) == 15 else d
        res = super().write(vals)
        if 'pedimento_number' in vals:
            for move in self:
                move.move_line_ids.write({'pedimento_number': move.pedimento_number})
        return res
