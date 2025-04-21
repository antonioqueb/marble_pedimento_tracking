from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        for move_vals in res:
            po_line = self.order_line.filtered(lambda l: l.id == move_vals.get('purchase_line_id'))
            if po_line:
                move_vals.update({'pedimento_number': po_line.pedimento_number})
        return res
