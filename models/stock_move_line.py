# models/stock_move_line.py
from odoo import models, fields, _
import logging

_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']

        for ml in self.filtered(lambda l: l.pedimento_number):
            # ───────────── Dominio mínimo: producto + ubicación + (lote si existe) ─────────────
            domain = [
                ('product_id', '=', ml.product_id.id),
                ('location_id', '=', ml.location_dest_id.id),
            ]
            if ml.lot_id:
                domain.append(('lot_id', '=', ml.lot_id.id))

            quants = Quant.search(domain)
            _logger.debug(
                "[PEDIMENTO] ML %s pedimento=%s → quants encontrados: %s",
                ml.id, ml.pedimento_number, quants.ids
            )

            if quants:
                quants.write({'pedimento_number': ml.pedimento_number})
            else:
                _logger.warning(
                    "[PEDIMENTO] ML %s: NO se encontró quant para actualizar (dominio %s)",
                    ml.id, domain
                )

        return res
