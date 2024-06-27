from odoo import models, fields, api, exceptions
from urllib.parse import quote
import logging
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(base_dir, 'logs')
log_file_path = os.path.join(base_dir, 'import_my_module.log')  
logger = logging.getLogger(__name__)
handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MyModule(models.Model):
    _name = 'my_module.my_module'
    _description = 'My Module Description'

    external_id = fields.Char(string="External ID", size=12)
    date = fields.Date(string="Date")
    number = fields.Char(string="Number", size=12)
    description = fields.Text(string="Description")
    file = fields.Binary(string="File")
    file_name = fields.Char(string="File Name")
    file_url = fields.Char(string="File URL", compute='_compute_file_url')

    partner_id = fields.Many2one('res.partner', string="Contact")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
    project_id = fields.Many2one('project.project', string="Project")

    for num in range(1, 21):
        locals()[f'pole{num:02d}'] = fields.Float(string=f'Pole {num:02d}', digits=(16, 2))

    @api.constrains('external_id')
    def _check_external_id(self):
        for record in self:
            if record.external_id and (not record.external_id.isdigit() or len(record.external_id) != 12):
                raise exceptions.ValidationError("External ID must be numeric and exactly 12 digits long.")
                
    @api.constrains('number')
    def _check_number(self):
        for record in self:
            if record.number and not record.number.isdigit():
                raise exceptions.ValidationError("Number must be numeric.")

    @api.depends('file')
    def _compute_file_url(self):
        for record in self:
            if record.file:
                record.file_url = '/web/content?model=%s&id=%s&field=file&download=true&filename=%s' % (
                    record._name, record.id, quote(record.file_name))
            else:
                record.file_url = None

    @api.model
    def load(self, fields, data):
        context = self.env.context.copy()
        context['importing'] = True
        self = self.with_context(context)
        self.search([]).unlink()
        logger.info("START IMPORT")

        ids = []
        messages = []
        nextrow = None

        for index, row in enumerate(data):
            external_id = row[0] if row[0].isdigit() and len(row[0]) == 12 else None  
            date = row[1]
            number = row[2] if row[2].isdigit() else None 

            partner_id = int(row[4]) if row[4].isdigit() else None
            user_id = int(row[5]) if row[5].isdigit() else None
            project_id = int(row[6]) if row[6].isdigit() else None

            if partner_id and not self.env['res.partner'].search([('id', '=', partner_id)]):
                logger.warning(f"Row {index} skipped: Partner ID {partner_id} does not exist.")
                continue

            if user_id and not self.env['res.users'].search([('id', '=', user_id)]):
                logger.warning(f"Row {index} skipped: User ID {user_id} does not exist.")
                continue

            if project_id and not self.env['project.project'].search([('id', '=', project_id)]):
                logger.warning(f"Row {index} skipped: Project ID {project_id} does not exist.")
                continue

            if external_id is None:
                logger.warning(f"Row {index} skipped: External ID must be numeric and exactly 12 digits long.")
                continue  

            vals = {
                'external_id': external_id, 
                'date': date,  
                'number': number,
                'description': row[3],
                'partner_id': partner_id,  
                'user_id': user_id,     
                'project_id': project_id,  
                'file_name': row[7],
            }

            try:
                new_record = self.create(vals)
                ids.append(new_record.id)
                logger.info(f"Successfully created record for row {index} with ID {new_record.id}")
            except Exception as e:
                logger.info(f"Error creating record for row {index}: {str(e)}")
                messages.append(f"Error in row {index}: {str(e)}")
                continue

            if index == len(data) - 1:
                nextrow = 0 

        return {'ids': ids if ids else False, 'messages': messages, 'nextrow': nextrow}
