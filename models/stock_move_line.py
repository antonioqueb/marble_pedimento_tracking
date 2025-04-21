# models/stock_move_line.py
from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']
        for ml in self:
            if ml.pedimento_number:
                quant = Quant.search([
                    ('product_id', '=', ml.product_id.id),
                    ('location_id', '=', ml.location_dest_id.id),
                    ('lot_id', '=', ml.lot_id.id or False),
                    ('package_id', '=', ml.result_package_id.id or False),
                    ('owner_id', '=', ml.owner_id.id or False),
                ], limit=1, order='in_date desc')

                if quant:
                    quant.pedimento_number = ml.pedimento_number
        return res
