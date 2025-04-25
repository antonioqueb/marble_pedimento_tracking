# models/stock_move_line.py
from odoo import models, fields, api
import re, logging
_logger = logging.getLogger(__name__)

# ───────────────── helpers ─────────────────
_CLEAN  = lambda v: re.sub(r'\D', '', v or '')
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}"   # AA BB CCCC DDDDDDD

_PED_RE = re.compile(r'^\d{15}$')       # exactamente 15 dígitos

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # tamaño 18 (15 dígitos + 3 espacios resultantes)
    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ---- UX: durante la edición ----
    @api.onchange('pedimento_number')
    def _onchange_ped(self):
        """
        • Mientras el usuario escribe: permitimos SÓLO dígitos
        • Si llega a 15 dígitos → formateamos con espacios
        """
        if self.pedimento_number is None:
            return
        digits = _CLEAN(self.pedimento_number)[:15]   # recorta excedente
        self.pedimento_number = _PRETTY(digits) if len(digits) == 15 else digits

    # ---- validación en servidor ----
    @api.constrains('pedimento_number')
    def _check_ped(self):
        for rec in self.filtered('pedimento_number'):
            if not _PED_RE.fullmatch(_CLEAN(rec.pedimento_number)):
                raise models.ValidationError("El pedimento debe contener 15 dígitos numéricos.")

    # ---- create / write: siempre guardamos bonito ----
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('pedimento_number'):
                d = _CLEAN(vals['pedimento_number'])
                vals['pedimento_number'] = _PRETTY(d) if len(d) == 15 else d
        return super().create(vals_list)

    def write(self, vals):
        if 'pedimento_number' in vals:
            d = _CLEAN(vals['pedimento_number'])
            vals['pedimento_number'] = _PRETTY(d) if len(d) == 15 else d
        return super().write(vals)

    # ---- copia al/los stock.quant ----
    def _action_done(self):
        res = super()._action_done()
        Quant = self.env['stock.quant']

        for ml in self:
            ped = ml.pedimento_number or ml.move_id.pedimento_number
            if not _PED_RE.fullmatch(_CLEAN(ped)):
                continue

            domain = [('product_id', '=', ml.product_id.id),
                      ('location_id', '=', ml.location_dest_id.id)]
            if ml.lot_id:
                domain.append(('lot_id', '=', ml.lot_id.id))

            quants = Quant.search(domain)
            if quants:
                quants.write({'pedimento_number': ped})
                _logger.debug("[PED] ML %s → '%s' copiado a %s", ml.id, ped, quants.ids)
        return res
