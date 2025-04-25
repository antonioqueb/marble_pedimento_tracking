# models/stock_move.py
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    # ─────── Se propaga cuando Odoo crea la línea por primera vez ───────
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals['pedimento_number'] = self.pedimento_number
        _logger.debug(
            "[PEDIMENTO] Move %s → _prepare_move_line_vals: pedimento=%s",
            self.id, self.pedimento_number
        )
        return vals

    # ─────── Complementa líneas ya existentes que estuvieran vacías ───────
    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = move.pedimento_number
        return res

    # ─────── NUEVO ─ Propaga el valor editado manualmente en el albarán ───────
    def write(self, vals):
        res = super().write(vals)
        if 'pedimento_number' in vals:
            for move in self:
                move.move_line_ids.write({
                    'pedimento_number': vals['pedimento_number']
                })
                _logger.debug(
                    "[PEDIMENTO] Move %s → write(): pedimento=%s copiado a %s líneas",
                    move.id, vals['pedimento_number'], len(move.move_line_ids)
                )
        return res
