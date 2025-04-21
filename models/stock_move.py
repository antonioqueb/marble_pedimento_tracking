from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals.update({'pedimento_number': self.pedimento_number})
        return vals
