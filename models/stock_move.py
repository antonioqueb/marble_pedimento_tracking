# models/stock_move.py
from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    # ─────────── Propaga el dato a la move-line al crearla ───────────
    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals['pedimento_number'] = self.pedimento_number
        return vals

    # ─────────── Rellena líneas existentes que hayan quedado vacías ───────────
    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = move.pedimento_number
        return res
