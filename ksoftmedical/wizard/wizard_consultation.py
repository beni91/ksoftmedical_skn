from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class wizard_report_consultation(models.TransientModel):
    _name = 'wizard.report.consultation'

    start_date = fields.Date('Date Debut')
    end_date = fields.Date('Date Fin')

    def get_report_values(self):
        appointments = self.env['ksoft.appointment'].search([
            ('date_rdv', '>=', self.start_date),
            ('date_rdv', '<=', self.end_date),
            ('type_rdv', 'in', ['cons','urg']),
            ('categorie', '=', 'prive'),
            ('status', 'not in', ['home','valid','invoicing']),
        ]).sorted(key=lambda r: (r.date_rdv, r.speciality.name, r.product_id.name, r.appointment_move_id.name))

        data = {}
        daily_totals = {}

        for appointment in appointments:
            day_key = appointment.date_rdv.date()

            if day_key not in daily_totals:
                daily_totals[day_key] = {'date': day_key, 'services': {}, 'total_amount': 0}

            service_key = appointment.speciality.name
            produit = appointment.product_id.name

            if service_key not in daily_totals[day_key]['services']:
                daily_totals[day_key]['services'][service_key] = {'service': service_key, 'name': produit, 'amount': 0}

            amount = appointment.product_id.list_price
            daily_totals[day_key]['services'][service_key]['amount'] += amount
            daily_totals[day_key]['total_amount'] += amount

        report_data = {
            'current_date': fields.Datetime.now(),
            'daily_totals': list(daily_totals.values())
        }

        periode = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }


        data['periode'] = periode
        data['records'] = report_data

        # _logger.warning('sssssss')
        # _logger.warning(report_data)
        # _logger.warning('sssssss')

        return self.env.ref('ksoftmedical.report_financier_consultation').report_action(self, data=data)

    def get_report_labo_values(self):
        docs = self.env['account.move'].search([
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
            ('libelle', '=', 'laboratoire'),
            ('categorie', '=', 'prive'),
            # ('state', 'not in=', 'paid'),
        ])

        # Organiser les données pour le rapport
        report_data = {}
        report= []
        reports = []

        data = {}
        # for move in docs.sorted(key=lambda x: (x.invoice_date, x.service_id2.name, x.categorie, x.name)):
        #     key = (move.invoice_date, move.service_id2.name, move.categorie)
        #     if key not in report_data:
        #         report_data[key] = {
        #             'service': move.service_id2.name,
        #             'categorie': move.categorie,
        #             'lines': [],
        #             'total_amount': 0,
        #         }
        #     report_data[key]['lines'].append({
        #         'name': move.name,
        #         'amount': move.amount_total,
        #         'invoice_date': move.invoice_date,
        #     })
        #     report_data[key]['total_amount'] += move.amount_total

        # # Calculer la somme générale
        # total_general = sum(entry['total_amount'] for entry in report_data.values())

        for move in docs:
            som +=move.amount_total
            vals = {
                'service': move.service,
                'categorie': move.categorie,
                'somme': som
            }

            val = {
                'name': move.name,
                'montant': move.amount_total
            }

            report.append(val)
            reports.append(vals)

        periode = {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

        data['periode'] = periode
        data['records'] = report
        data['records2'] = reports

        return self.env.ref('ksoftmedical.report_financier_laboratoire').report_action(self, data=data)

