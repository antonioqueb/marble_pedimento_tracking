# models/stock_move.py
from odoo import models, fields, api
import logging, re

_logger = logging.getLogger(__name__)

def _clean_ped(v): return re.sub(r'\D', '', v or '')
def _pretty_ped(v):
    d = _clean_ped(v)
    return f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else v


class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # -------- formato inmediato en la vista --------
    @api.onchange('pedimento_number')
    def _onchange_pedimento(self):
        if self.pedimento_number:
            self.pedimento_number = _pretty_ped(self.pedimento_number)

    # -------- se propaga al crear líneas --------
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals['pedimento_number'] = _pretty_ped(self.pedimento_number)
        return vals

    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            ped = _pretty_ped(move.pedimento_number)
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = ped
        return res

    # -------- cuando editas el campo en el albarán --------
    def write(self, vals):
        if 'pedimento_number' in vals:
            vals['pedimento_number'] = _pretty_ped(vals['pedimento_number'])
        res = super().write(vals)
        if 'pedimento_number' in vals:
            for move in self:
                move.move_line_ids.write({'pedimento_number': vals['pedimento_number']})
        return res
