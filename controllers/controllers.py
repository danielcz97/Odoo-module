# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
class MyModule(http.Controller):
    @http.route('/my_module/my_module/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('my_module.listing', {
            'root': '/my_module/my_module',
            'objects': http.request.env['my_module.my_module'].search([]),
        })

    @http.route('/my_module/my_module/objects/<model("my_module.my_module"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('my_module.object', {
            'object': obj
        })

    @http.route('/my/files', type="http", auth='user', website=True)
    def get_user_files(self):
        user = request.env.user
        files = request.env['my_module.my_module'].search([('user_id', '=', user.id)])
        files_data = []
        for file in files:
            file_data = {
                'date': file.date,
                'number': file.number,
                'description': file.description,
                'file_url': file.file_url,
                'dynamic_fields': {f'pole{str(num).zfill(2)}': getattr(file, f'pole{str(num).zfill(2)}') for num in range(100)}
            }
            files_data.append(file_data)
            _logger.info('File data: %s', file_data)

        return request.render('my_module.my_files', {
            'files': files_data
            })

    @http.route('/all/files', type="http", auth='user', website=True)
    def list_all_files(self):
        files = request.env['my_module.my_module'].search([])
        return request.render('my_module.listing', {
            'files': files,})
    
    @http.route(['/my/indeks', '/my/indeks/<int:index>'], auth='user', type='http', website=True)
    def index(self, index=None, search=None, project_id=None, partner_id=None, user_id=None, **kw):
        user = request.env.user
        domain = [('user_id', '=', user.id)]

        if search:
            domain += [('description', 'ilike', search)]
        if project_id:
            domain += [('project_id', '=', int(project_id))]
        if partner_id:
            domain += [('partner_id', '=', int(partner_id))]
        if user_id:
            domain += [('user_id', '=', int(user_id))]

        for num in range(1, 21):
            field_name = f'pole{num:02d}'
            if kw.get(field_name):
                domain += [(field_name, '=', float(kw[field_name]))]

        records = request.env['my_module.my_module'].search(domain)

        projects = request.env['project.project'].search([])
        partners = request.env['res.partner'].search([])
        users = request.env['res.users'].search([])

        if index:
            record = records.filtered(lambda r: r.id == index)
            current_index = records.ids.index(record.id) if record else None
            next_id = records.ids[current_index + 1] if current_index is not None and current_index + 1 < len(records.ids) else None
            prev_id = records.ids[current_index - 1] if current_index is not None and current_index > 0 else None
            return request.render('my_module.detail_template', {
                'record': record,
                'user': user,
                'prev_id': prev_id,
                'next_id': next_id
            })
        else:
            return request.render('my_module.index_template', {
                'records': records,
                'user': user,
                'projects': projects,
                'partners': partners,
                'users': users,
            })
        
    @http.route('/my/local', auth='user', type='http', website=True)
    def local(self, **kw):
        user = request.env.user
        records = request.env['project.project'].search([('user_id', '=', user.id)])
        return request.render('my_module.local_template', {
            'records': records,
            'user': user
        })