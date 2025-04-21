import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', size=15, copy=False)

    @api.model
    def _update_available_quantity(self, product, location, quantity,
                                   lot_id=None, package_id=None,
                                   owner_id=None, strict=True):
        """Copiar pedimento desde move_line al quant."""
        # Llamada limpia a la firma nativa
        quant = super()._update_available_quantity(
            product, location, quantity,
            lot_id=lot_id, package_id=package_id,
            owner_id=owner_id, strict=strict
        )

        # Tomamos el move_line del contexto (o donde lo hayas guardado)
        move_line_id = self.env.context.get('move_line_id')
        if move_line_id:
            move_line = self.env['stock.move.line'].browse(move_line_id)
            if move_line.exists() and move_line.pedimento_number:
                quant.pedimento_number = move_line.pedimento_number

        return quant
