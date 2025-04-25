-e ### models/stock_move_line.py
```
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
```

-e ### models/purchase_order_line.py
```
from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)
```

-e ### models/stock_quant.py
```
# models/stock_quant.py
from odoo import models, fields
import re
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else d

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    pedimento_number = fields.Char(string='Número de Pedimento', size=18, copy=False)

    def read(self, fields=None, load='_classic_read'):
        res = super().read(fields=fields, load=load)
        if not fields or 'pedimento_number' in fields:
            for rec in res:
                if rec.get('pedimento_number'):
                    rec['pedimento_number'] = _PRETTY(re.sub(r'\D', '', rec['pedimento_number']))
        return res
```

-e ### models/__init__.py
```
from . import purchase_order
from . import purchase_order_line
from . import stock_move
from . import stock_move_line
from . import stock_quant
```

-e ### models/purchase_order.py
```
from odoo import models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        for move_vals in res:
            po_line = self.order_line.filtered(lambda l: l.id == move_vals.get('purchase_line_id'))
            if po_line:
                move_vals.update({'pedimento_number': po_line.pedimento_number})
        return res
```

-e ### models/stock_move.py
```
# models/stock_move.py
from odoo import models, fields, api
import re, logging
_logger = logging.getLogger(__name__)

_CLEAN  = lambda v: re.sub(r'\D', '', v or '')
_PRETTY = lambda d: f"{d[:2]} {d[2:4]} {d[4:8]} {d[8:]}" if len(d) == 15 else d

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=18)

    # ---- UX en formulario ----
    @api.onchange('pedimento_number')
    def _onchange_ped(self):
        if self.pedimento_number is None:
            return
        digits = _CLEAN(self.pedimento_number)[:15]
        self.pedimento_number = _PRETTY(digits) if len(digits) == 15 else digits

    # ---- propaga a líneas nuevas ----
    def _prepare_move_line_vals(self, *a, **kw):
        vals = super()._prepare_move_line_vals(*a, **kw)
        vals['pedimento_number'] = self.pedimento_number
        return vals

    def _create_move_lines(self):
        res = super()._create_move_lines()
        for move in self:
            for line in move.move_line_ids.filtered(lambda l: not l.pedimento_number):
                line.pedimento_number = move.pedimento_number
        return res

    # ---- guarda con formato y propaga a líneas existentes ----
    def write(self, vals):
        if 'pedimento_number' in vals:
            d = _CLEAN(vals['pedimento_number'])
            vals['pedimento_number'] = _PRETTY(d) if len(d) == 15 else d
        res = super().write(vals)
        if 'pedimento_number' in vals:
            for move in self:
                move.move_line_ids.write({'pedimento_number': move.pedimento_number})
        return res
```

-e ### views/stock_picking_views.xml
```
<odoo>
    <record id="stock_picking_form_pedimento" model="ir.ui.view">
        <field name="name">stock.picking.form.pedimento</field>
        <field name="model">stock.picking</field>
        <field name="inherit_id" ref="stock.view_picking_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='move_ids_without_package']/list//field[@name='product_id']" position="after">
                <field name="pedimento_number"/>
            </xpath>
        </field>
    </record>
</odoo>
```

-e ### views/stock_quant_views.xml
```
<odoo>
    <record id="view_stock_quant_tree_pedimento_inherit" model="ir.ui.view">
        <field name="name">stock.quant.tree.pedimento</field>
        <field name="model">stock.quant</field>
        <field name="inherit_id" ref="stock.view_stock_quant_tree_editable"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='lot_id']" position="after">
                <!-- CHANGED: lo mostramos sólo de lectura -->
                <field name="pedimento_number" readonly="1"/>
            </xpath>
        </field>
    </record>
</odoo>
```

-e ### views/stock_move_line_views.xml
```
<odoo>
    <record id="view_move_line_list_inherit_pedimento" model="ir.ui.view">
        <field name="name">stock.move.line.list.pedimento</field>
        <field name="model">stock.move.line</field>
        <field name="inherit_id" ref="stock.view_move_line_tree"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='lot_id']" position="after">
                <field name="pedimento_number"/>
            </xpath>
        </field>
    </record>
</odoo>
```

### __init__.py
```
from . import models
```
### __manifest__.py
```
{
    'name': 'Pedimento Tracking',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Track Customs Pedimento Number from Purchase to Stock',
    'author': 'ALPHAQUEB CONSULTING',
    'website': 'https://alphaqueb.com',
    'company': 'ALPHAQUEB CONSULTING S.A.S.',
    'maintainer': 'ANTONIO QUEB',
    'depends': ['purchase', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
```
