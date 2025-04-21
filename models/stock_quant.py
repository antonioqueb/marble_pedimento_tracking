# -*- coding: utf-8 -*-
from odoo import models, fields, api
class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char('Número de Pedimento', size=15, copy=False)

    @api.model
    def _update_available_quantity(self, product, location, quantity, *args, **kwargs):
        # Llamada al super con todos los argumentos que vengan:
        quant = super()._update_available_quantity(product, location, quantity, *args, **kwargs)

        move_line_id = kwargs.get('move_line_id') or self.env.context.get('move_line_id')
        if move_line_id:
            move_line = self.env['stock.move.line'].browse(move_line_id)
            if move_line and move_line.pedimento_number:
                quant.pedimento_number = move_line.pedimento_number

        return quant
