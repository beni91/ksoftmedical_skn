
# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class RapportMoveStock(models.TransientModel):
    _name = 'rapport.move.stock'

    date_debut = fields.Date('Date Début', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_fin = fields.Date('Date Fin', required=True,
                          default=lambda self: fields.Date.to_string(date.today()))
    warehouse_id = fields.Many2one('stock.warehouse', 'Entrepôt', required=True)

    def _get_stock_moves(self, warehouse_id, date_debut, date_fin):
        stock_moves = self.env['stock.move'].search([
                                                    ('warehouse_id','=',warehouse_id),
                                                    ('date','>=',date_debut),
                                                    ('date','<=',date_fin),
                                                    ])
        return stock_moves

    def _generate_report_data_detaille(self, stock_moves):
        report_data = []

        # Utilisez un dictionnaire pour accumuler les quantités par produit, date
        stock_quantities = {}

        # Première itération pour accumuler les quantités
        for move in stock_moves:
            article_name = move.product_id.name
            date = move.date
            quantity_in = 0
            quantity_out = 0

            if move.location_dest_id.usage == 'internal':
                quantity_in = move.product_qty
                source_location = move.location_id.name
                dest_location = move.location_dest_id.name
            elif move.location_id.usage == 'internal':
                quantity_out = move.product_qty
                source_location = move.location_id.name
                dest_location = move.location_dest_id.name
            stock_quantities.setdefault(article_name, {})
            stock_quantities[article_name].setdefault(date, {
                'quantity_in': 0,
                'quantity_out': 0,
                'remaining_stock': 0,
                'source_location': '',
                'dest_location': '',
            })

            stock_quantities[article_name][date]['quantity_in'] += quantity_in
            stock_quantities[article_name][date]['quantity_out'] += quantity_out
            stock_quantities[article_name][date]['remaining_stock'] += quantity_in - quantity_out
            
            stock_quantities[article_name][date]['source_location'] = source_location
            stock_quantities[article_name][date]['dest_location'] = dest_location

        # Deuxième itération pour créer le rapport au format demandé
        for article_name, dates_data in stock_quantities.items():
            total_quantity_in = 0
            total_quantity_out = 0

            for date, quantities in dates_data.items():
                total_quantity_in += quantities['quantity_in']
                total_quantity_out += quantities['quantity_out']

                data = {
                    'article': '',
                    'date': date,
                    'qte_in': quantities['quantity_in'],
                    'qte_out': quantities['quantity_out'],
                    'qte_restant': quantities['remaining_stock'],
                    'source_location': quantities['source_location'],
                    'dest_location': quantities['dest_location'],
                    'difference': '',
                }
                report_data.append(data)

            # Ajouter la ligne avec la différence après avoir parcouru toutes les dates pour un article
            report_data.append({
                'article': article_name,
                'date': 'Total',
                'qte_in': total_quantity_in,
                'qte_out': total_quantity_out,
                'qte_restant': '',
                'source_location': '',
                'dest_location': '',
                'difference': total_quantity_in - total_quantity_out,
            })

        return report_data


    def _generate_report_data(self, stock_moves):
        report_data = []
        stock_quantities = {}

        for move in stock_moves:
            article_name = move.product_id.name
            quantity_in = 0
            quantity_out = 0

            if move.location_dest_id.usage == 'internal':
                quantity_in = move.product_qty
            elif move.location_id.usage == 'internal':
                quantity_out = move.product_qty

            stock_quantities.setdefault(article_name, {
                'quantity_in': 0,
                'quantity_out': 0,
                'remaining_stock': 0,
            })

            stock_quantities[article_name]['quantity_in'] += quantity_in
            stock_quantities[article_name]['quantity_out'] += quantity_out
            stock_quantities[article_name]['remaining_stock'] += quantity_in - quantity_out

        for article_name, quantities in stock_quantities.items():
            data = {
                'article': article_name,
                'qte_in': quantities['quantity_in'],
                'qte_out': quantities['quantity_out'],
                'qte_restant': quantities['remaining_stock'],
            }
            report_data.append(data)

        return report_data
        
    def _generate_report_valorisation_stock(self, stock_moves):
        report_data = []
        stock_quantities = {}

        for move in stock_moves:
            article_name = move.product_id.name
            quantity_in = 0
            quantity_out = 0
            unit_price = move.product_id.standard_price

            if move.location_dest_id.usage == 'internal':
                quantity_in = move.product_qty
            elif move.location_id.usage == 'internal':
                quantity_out = move.product_qty
                
            #stock_quantities.setdefault(article_name, {})

            stock_quantities.setdefault(article_name, {
                'quantity_in': 0,
                'quantity_out': 0,
                'remaining_stock': 0,
                'unit_price': unit_price,
            })

            stock_quantities[article_name]['quantity_in'] += quantity_in
            stock_quantities[article_name]['quantity_out'] += quantity_out
            stock_quantities[article_name]['remaining_stock'] += quantity_in - quantity_out
            stock_quantities[article_name]['unit_price'] += unit_price

        for article_name, quantities in stock_quantities.items():
            data = {
                'article': article_name,
                'qte_in': quantities['quantity_in'],
                'qte_out': quantities['quantity_out'],
                'qte_restant': quantities['remaining_stock'],
                'prix_achat': quantities['unit_price'],
            }
            report_data.append(data)

        return report_data


    def generate_report_mov_stock(self):
        data = {}
        stock_moves = self._get_stock_moves(self.warehouse_id.id, self.date_debut, self.date_fin)
        report_data = self._generate_report_data(stock_moves)

        periode = {
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'entrepot': self.warehouse_id.name,
        }

        data['records'] = report_data
        data['periode'] = periode

        return self.env.ref('stock_ngaliema.report_stock_movement').report_action(self, data=data)
    
    def generate_report_mov_stock_detail(self):
        data = {}
        stock_moves = self._get_stock_moves(self.warehouse_id.id, self.date_debut, self.date_fin)
        report_data = self._generate_report_data_detaille(stock_moves) 

        periode = {
                    'date_debut': self.date_debut,
                    'date_fin': self.date_fin,
                    'entrepot': self.warehouse_id.name,
                }

        data['records'] = report_data
        data['periode'] = periode

        return self.env.ref('stock_ngaliema.report_stock_movement_detaille').report_action(self, data=data)
        
        
    def generate_report_valorisation_stock(self):
        data = {}
        stock_moves = self._get_stock_moves(self.warehouse_id.id, self.date_debut, self.date_fin)
        report_data = self._generate_report_valorisation_stock(stock_moves) 

        periode = {
                    'date_debut': self.date_debut,
                    'date_fin': self.date_fin,
                    'entrepot': self.warehouse_id.name,
                }

        data['records'] = report_data
        data['periode'] = periode

        return self.env.ref('stock_ngaliema.report_stock_valorisation_stock').report_action(self, data=data)