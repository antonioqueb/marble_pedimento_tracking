-e ### models/stock_move_line.py
```
from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pedimento_number = fields.Char('Número de Pedimento', size=15)
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
from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    pedimento_number = fields.Char('Número de Pedimento', size=15)

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(quantity, reserved_quant)
        vals.update({'pedimento_number': self.pedimento_number})
        return vals
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
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
```
