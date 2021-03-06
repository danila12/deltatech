# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, datetime
from dateutil import relativedelta

import time
from openerp.exceptions import except_orm, Warning, RedirectWarning
 
from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api

import openerp.addons.decimal_precision as dp


class stock_pack_operation(models.Model):
    _inherit = "stock.pack.operation"

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        if vals.get("picking_id"):
            picking = self.pool.get("stock.picking").browse(cr, uid, vals['picking_id'], context=context)
            vals['date'] = picking.min_date  # trebuie sa fie minimul dintre data curenta si data din picking
        res_id = super(stock_pack_operation, self).create(cr, uid, vals, context=context)
        return res_id


class stock_quant(models.Model):
    _inherit = "stock.quant"
    
    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, force_location_from=False, force_location_to=False, context=None):         
        quant = super(stock_quant, self)._quant_create(cr, uid, qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=force_location_from, force_location_to=force_location_to, context=context)
        self.write(cr, uid, [quant.id], {'in_date': move.date_expected }, context=context)
        return quant    
    
          
                   
    
class stock_move(models.Model):
    _inherit = 'stock.move'

    def write(self, cr, uid, ids, vals, context=None):   
        date_fields = set(['date', 'date_expected'])
        if date_fields.intersection(vals):
            for move in self.browse(cr, uid, ids, context=context):
                today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                if 'date' in vals:
                    if move.date_expected[:10] < today and move.date_expected < vals['date']:
                        vals['date'] =  move.date_expected
                    if move.date[:10] < today and move.date < vals['date']:
                        vals['date'] =  move.date                      
                if 'date_expected' in vals:
                    if move.date[:10] < today and move.date < vals['date_expected']:
                        vals['date_expected'] =  move.date 
                           
        return  super(stock_move, self).write(cr, uid, ids, vals, context=context)     

 
 

 

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    # ajustare automata a monedei de facturare in conformitate cu moneda din jurnal
    @api.multi
    def action_invoice_create(self,  journal_id, group=False, type='out_invoice' ): 
        
        invoices = super(stock_picking,self).action_invoice_create( journal_id, group, type )
        
 
        #this = self.with_context(inv_type=type)  # foarte important pt a determina corect moneda
        
        #self = this
        
        journal = self.env['account.journal'].browse(journal_id)
        obj_invoices = self.env['account.invoice'].browse(invoices)
        
        to_currency = journal.currency or self.env.user.company_id.currency_id

 
        for obj_inv in obj_invoices:
            if to_currency == obj_inv.currency_id:
                continue
            from_currency = obj_inv.currency_id.with_context(date=obj_inv.date_invoice)
 
            for line in obj_inv.invoice_line:
                new_price = from_currency.compute(line.price_unit, to_currency )
                line.write(  {'price_unit': new_price})
                
            obj_inv.write(  {'currency_id': to_currency.id} )
            obj_inv.button_compute()
        return invoices


    @api.model 
    def _create_invoice_from_picking(self,  picking, vals):        
        invoice_id = super(stock_picking, self)._create_invoice_from_picking( picking, vals)
        if picking.sale_id:
            picking.sale_id.write( {'invoice_ids': [(4, invoice_id)]})
        picking.write({'invoice_id':invoice_id})
         
        return invoice_id

 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
