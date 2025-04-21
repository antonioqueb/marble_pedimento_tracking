# -*- coding: utf-8 -*-
from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', size=15, copy=False)

    #  Nota: aceptamos **kwargs para que futuros cambios en Odoo no rompan la herencia
    @classmethod
    def _update_available_quantity(
        cls, product_id, location_id, quantity,
        lot_id=None, package_id=None, owner_id=None,
        strict=False, inventory_id=False, in_date=False, **kwargs
    ):
        """
        Extiende el método core para copiar el número de pedimento del move‑line
        (cuando venga en los kwargs) al quant resultante.
        """
        quant = super()._update_available_quantity(
            product_id, location_id, quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            inventory_id=inventory_id,
            in_date=in_date,
            **kwargs
        )

        move_line = kwargs.get('move_line_id')
        if move_line and move_line.pedimento_number:
            quant.pedimento_number = move_line.pedimento_number
        return quant
