# -*- coding: utf-8 -*-
from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', size=15, copy=False)

    @classmethod
    def _update_available_quantity(cls, product_id, location_id, quantity, *args, **kwargs):
        """
        Llama al core sin alterar la lista de argumentos y,
        si viene un move_line con pedimento, lo copia al quant.
        """
        quant = super()._update_available_quantity(
            product_id, location_id, quantity, *args, **kwargs
        )

        move_line = kwargs.get('move_line_id')
        if move_line and getattr(move_line, 'pedimento_number', False):
            quant.pedimento_number = move_line.pedimento_number

        return quant
