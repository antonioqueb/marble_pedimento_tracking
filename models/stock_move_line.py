# models/stock_move_line.py
from odoo import models, fields, api
import re, logging

_logger = logging.getLogger(__name__)

def _clean(v):          # deja solo dígitos
    return re.sub(r'\D', '', v or '')

def _pretty(v):         # AA BB CCCC DDDDDDD  (con espacios)
    d = _clean(v)
    return f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else v

_PED_RE = re.compile(r'^\d{15}$')         # sólo 15 dígitos crudos


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ────────── AUTO-formato al CREAR ──────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('pedimento_number'):
                vals['pedimento_number'] = _pretty(vals['pedimento_number'])
        return super().create(vals_list)

    # ────────── AUTO-formato al EDITAR ──────────
    def write(self, vals):
        if 'pedimento_number' in vals:
            vals['pedimento_number'] = _pretty(vals['pedimento_number'])
        return super().write(vals)

    # ────────── Validación (ya formateada) ──────────
    @api.constrains('pedimento_number')
    def _check_ped(self):
        for rec in self.filtered('pedimento_number'):
            if not _PED_RE.fullmatch(_clean(rec.pedimento_number)):
                raise models.ValidationError(
                    "Un pedimento debe contener exactamente 15 dígitos numéricos."
                )

    # ────────── Copia al/los quant(s) ──────────
    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']

        for ml in self:
            ped = ml.pedimento_number or ml.move_id.pedimento_number
            if not _clean(ped):
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
                _logger.debug("[PEDIMENTO] ML %s → '%s' copiado a %s", ml.id, ped, quants.ids)
        return res
