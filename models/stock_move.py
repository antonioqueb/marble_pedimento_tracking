# models/stock_move.py
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals['pedimento_number'] = self.pedimento_number
        _logger.debug(
            "[PEDIMENTO] Move %s → _prepare_move_line_vals: pedimento=%s",
            self.id, self.pedimento_number
        )
        return vals

    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = move.pedimento_number
        return res
