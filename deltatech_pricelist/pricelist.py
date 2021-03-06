# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
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

from openerp import models, fields, api, tools, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp
from openerp.api import Environment

class product_pricelist(models.Model):
    _inherit = "product.pricelist"  
    code = fields.Char(string="Code") # folosit pt a putea face reguli de acces

class product_pricelist_item(models.Model):
    _inherit = "product.pricelist.item"  

 
    @api.one
    @api.depends('base','price_discount', 'price_surcharge' )
    def _compute_text_price(self):
        # todo: de convertit in format local
        value = (1 + self.price_discount) 
        
        self.price_text = self._price_field_get()[self.base-1][1] +' * '+str(value)
        if self.price_surcharge:      
            self.price_text +=  str(self.price_surcharge)
 
    
    price_text = fields.Char(string="Text Price",  readonly=True, compute='_compute_text_price' )    
    
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





