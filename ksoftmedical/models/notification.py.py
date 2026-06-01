# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class Notifications(models.Model):
	_inherit = 'sh.announcement'

	#@api.multi
	#def NotifShop(self):
	#	users = [(4, 11), (4, 6)]
	#	notif = self.create({
	#		'name': "Notification Shop",
	#		'date': fields.Date.today(),
	#		'is_popup_notification': True,
	#		'simple_text': True,
	#		'notification_type': 'warning',
	#		'description_text': "NOUVELLE DEMANDE",
	#		'user_ids': users
	#	})
		#notif.write()
	#	notif.notify_user()

		#raise Exception(_("##### %s", notif))

	def NotifShop(self):
		#users = [(4, 11), (4, 6)]
		#vals = {
		#	'name': 'Notification Shop',
		#	'date': fields.Date.today(),
		#	'is_popup_notification': True,
		#	'simple_text': True,
		#	'notification_type': 'warning',
		#	'description_text': "NOUVELLE DEMANDE",
		#	'user_ids': users
		#}
		#res = super(Notifications, self).create(vals)
		#res.notify_user()

		domain = [('name', '=', 'Notification Shop')]
		annonce = self.env['sh.announcement'].search(domain)
		for rec in annonce:
			rec.notify_user()

	def notifmedecins(self):
		domain = [('name', '=', 'Notification medecin')]
		annonce = self.env['sh.announcement'].search(domain)
		for rec in annonce:
			rec.notify_user()

	def notifTriage(self):
		domain = [('name', '=', 'Notification triage')]
		annonce = self.env['sh.announcement'].search(domain)
		for rec in annonce:
			rec.notify_user()

	def notifPharmacie(self):
		domain = [('name', '=', 'Notification pharmacie')]
		annonce = self.env['sh.announcement'].search(domain)
		for rec in annonce:
			rec.notify_user()

	def notifShopRec(self):
		domain = [('name', '=', 'Notification Shop Reception')]
		annonce = self.env['sh.announcement'].search(domain)
		for rec in annonce:
			rec.notify_user()