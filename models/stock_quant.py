from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    @classmethod
    def _update_available_quantity(cls, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, move_line_id=None):
        res = super()._update_available_quantity(product_id, location_id, quantity, lot_id, package_id, owner_id, move_line_id)
        if move_line_id and move_line_id.pedimento_number:
            res.pedimento_number = move_line_id.pedimento_number
        return res
