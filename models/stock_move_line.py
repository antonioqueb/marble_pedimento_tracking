from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _action_done(self):
        res = super()._action_done()
        for ml in self:
            if ml.pedimento_number:
                ml.write({'move_id': ml.move_id.id})  # Asegura que move_id está vinculado
                quants = ml.env['stock.quant']._gather(ml.product_id, ml.location_dest_id, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, strict=True)
                quants.write({'pedimento_number': ml.pedimento_number})
        return res
