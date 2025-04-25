# models/stock_move.py
from odoo import models, fields, api
import re, logging
_logger = logging.getLogger(__name__)

def _clean(v):  return re.sub(r'\D', '', v or '')
def _pretty(v): return f"{_clean(v)[:2]} {_clean(v)[2:4]} {_clean(v)[4:8]} {_clean(v)[8:]}" if len(_clean(v)) == 15 else v


class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ---------- formato inmediato en vista ----------
    @api.onchange('pedimento_number')
    def _onchange_ped(self):
        if self.pedimento_number:
            self.pedimento_number = _pretty(self.pedimento_number)

    # ---------- se propaga al crear líneas ----------
    def _prepare_move_line_vals(self, *a, **kw):
        vals = super()._prepare_move_line_vals(*a, **kw)
        vals['pedimento_number'] = _pretty(self.pedimento_number)
        return vals

    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            ped = _pretty(move.pedimento_number)
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = ped
        return res

    # ---------- AUTO-formato y propagación ----------
    def write(self, vals):
        if 'pedimento_number' in vals:
            vals['pedimento_number'] = _pretty(vals['pedimento_number'])
        res = super().write(vals)
        if 'pedimento_number' in vals:
            for move in self:
                move.move_line_ids.write({'pedimento_number': vals['pedimento_number']})
        return res
