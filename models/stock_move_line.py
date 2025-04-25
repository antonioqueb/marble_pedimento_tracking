# models/stock_move_line.py
from odoo import models, fields, api
import re
import logging

_logger = logging.getLogger(__name__)

_PED_RE = re.compile(r'^\d{2}\s?\d{2}\s?\d{4}\s?\d{7}$')   # admite espacios o sin ellos


# ─────────────────────────────────────────────────────────────
def _clean_ped(value):
    """Quita cualquier cosa que no sea dígito."""
    return re.sub(r'\D', '', value or '')


def _pretty_ped(value):
    """
    Formatea 15 dígitos como  AA BB CCCC DDDDDDD
    Devuelve tal cual si no son 15 dígitos.
    """
    digits = _clean_ped(value)
    if len(digits) == 15:
        return f"{digits[:2]} {digits[2:4]} {digits[4:8]} {digits[8:]}"
    return value
# ─────────────────────────────────────────────────────────────


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ---------- UX: formateo en cuanto el usuario escribe ----------
    @api.onchange('pedimento_number')
    def _onchange_pedimento(self):
        for rec in self:
            if rec.pedimento_number:
                rec.pedimento_number = _pretty_ped(rec.pedimento_number)

    # ---------- validación extra opcional ----------
    @api.constrains('pedimento_number')
    def _check_pedimento_format(self):
        for rec in self.filtered(lambda r: r.pedimento_number):
            if not _PED_RE.fullmatch(rec.pedimento_number):
                raise models.ValidationError(
                    "El número de pedimento debe contener 15 dígitos "
                    "seguros (puede llevar espacios intermedios)."
                )

    # ---------- Copia el pedimento al/los quant(s) ----------
    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']

        for ml in self:
            ped = _pretty_ped(ml.pedimento_number or ml.move_id.pedimento_number)
            if not _clean_ped(ped):
                continue

            domain = [
                ('product_id', '=', ml.product_id.id),
                ('location_id', '=', ml.location_dest_id.id),
            ]
            if ml.lot_id:
                domain.append(('lot_id', '=', ml.lot_id.id))

            quants = Quant.search(domain)
            if quants:
                quants.write({'pedimento_number': ped})
                _logger.debug(
                    "[PEDIMENTO] ML %s → escrito '%s' en quants %s",
                    ml.id, ped, quants.ids
                )
        return res
