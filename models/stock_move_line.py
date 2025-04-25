# models/stock_move_line.py
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    # ─────── Copia el pedimento al/los quant(s) creados ───────
    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']

        for ml in self:
            # ① toma el de la línea; ② si está vacío, toma el del movimiento
            ped = ml.pedimento_number or ml.move_id.pedimento_number
            if not ped:
                continue

            domain = [
                ('product_id', '=', ml.product_id.id),
                ('location_id', '=', ml.location_dest_id.id),
            ]
            if ml.lot_id:
                domain.append(('lot_id', '=', ml.lot_id.id))

            quants = Quant.search(domain)
            _logger.debug(
                "[PEDIMENTO] ML %s pedimento=%s → quants %s",
                ml.id, ped, quants.ids
            )

            if quants:
                quants.write({'pedimento_number': ped})
            else:
                _logger.warning(
                    "[PEDIMENTO] ML %s: sin quant para actualizar (dominio %s)",
                    ml.id, domain
                )

        return res
