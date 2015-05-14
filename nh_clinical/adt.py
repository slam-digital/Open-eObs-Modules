# -*- coding: utf-8 -*-

from datetime import datetime as dt
import logging

from openerp.osv import orm, fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID

from openerp.addons.nh_activity.activity import except_if

_logger = logging.getLogger(__name__)


class nh_clinical_adt_patient_register(orm.Model):
    """
    Registers a new patient into the system.
     patient_identifier: String - NHS Number
     other_identifier: String - Hospital Number
     given_name: String - First name
     family_name: String - Last name
     middle_names: String - Middle names
     dob: String - Date of Birth, have to be in format '%Y-%m-%d %H:%M:%S'
     gender: String - 'BOTH','F','I','M','NSP','U'
     sex: String - Same values as gender.
     ethnicity: String - Look at patient class for the list of allowed values.
    """
    _name = 'nh.clinical.adt.patient.register'
    _inherit = ['nh.activity.data']   
    _description = 'ADT Patient Register'

    _gender = [['BOTH', 'Both'], ['F', 'Female'], ['I', 'Intermediate'],
               ['M', 'Male'], ['NSP', 'Not Specified'], ['U', 'Unknown']]
    _ethnicity = [
        ['A', 'White - British'], ['B', 'White - Irish'], ['C', 'White - Other background'],
        ['D', 'Mixed - White and Black Caribbean'], ['E', 'Mixed - White and Black African'],
        ['F', 'Mixed - White and Asian'], ['G', 'Mixed - Other background'], ['H', 'Asian - Indian'],
        ['J', 'Asian - Pakistani'], ['K', 'Asian - Bangladeshi'], ['L', 'Asian - Other background'],
        ['M', 'Black - Caribbean'], ['N', 'Black - African'], ['P', 'Black - Other background'], ['R', 'Chinese'],
        ['S', 'Other ethnic group'], ['Z', 'Not stated']
    ]

    _columns = { 
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'patient_identifier': fields.char('NHS Number', size=10),
        'other_identifier': fields.char('Hospital Number', size=20),
        'family_name': fields.char('Last Name', size=200),
        'given_name': fields.char('First Name', size=200),
        'middle_names': fields.char('Middle Names', size=200),
        'dob': fields.datetime('Date of Birth'),
        'gender': fields.selection(_gender, string='Gender'),
        'sex': fields.selection(_gender, string='Sex'),
        'ethnicity': fields.selection(_ethnicity, string='Ethnicity'),
        'title': fields.many2one('res.partner.title', 'Title')
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        data = vals.copy()
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_data(cr, uid, data, context=context)
        return super(nh_clinical_adt_patient_register, self).submit(cr, uid, activity_id, data, context)
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        patient_pool = self.pool['nh.clinical.patient']
        vals = {
            'title': activity.data_ref.title.id,
            'patient_identifier': activity.data_ref.patient_identifier,
            'other_identifier': activity.data_ref.other_identifier,
            'family_name': activity.data_ref.family_name,
            'given_name': activity.data_ref.given_name,
            'middle_names': activity.data_ref.middle_names,
            'dob': activity.data_ref.dob,
            'gender': activity.data_ref.gender,
            'sex': activity.data_ref.sex,
            'ethnicity': activity.data_ref.ethnicity
        }
        patient_id = patient_pool.create(cr, uid, vals, context)
        self.write(cr, uid, activity.data_ref.id, {'patient_id': patient_id}, context=context)
        super(nh_clinical_adt_patient_register, self).complete(cr, uid, activity_id, context)
        return patient_id


class nh_clinical_adt_patient_update(orm.Model):
    """
    Update patient information. It will overwrite every single field in the target patient.
    Same fields as patient register.
    """
    _name = 'nh.clinical.adt.patient.update'
    _inherit = ['nh.activity.data']
    _description = 'ADT Patient Update'

    _gender = [['BOTH', 'Both'], ['F', 'Female'], ['I', 'Intermediate'],
               ['M', 'Male'], ['NSP', 'Not Specified'], ['U', 'Unknown']]
    _ethnicity = [
        ['A', 'White - British'], ['B', 'White - Irish'], ['C', 'White - Other background'],
        ['D', 'Mixed - White and Black Caribbean'], ['E', 'Mixed - White and Black African'],
        ['F', 'Mixed - White and Asian'], ['G', 'Mixed - Other background'], ['H', 'Asian - Indian'],
        ['J', 'Asian - Pakistani'], ['K', 'Asian - Bangladeshi'], ['L', 'Asian - Other background'],
        ['M', 'Black - Caribbean'], ['N', 'Black - African'], ['P', 'Black - Other background'], ['R', 'Chinese'],
        ['S', 'Other ethnic group'], ['Z', 'Not stated']
    ]

    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'patient_identifier': fields.char('NHS Number', size=10),
        'other_identifier': fields.char('Hospital Number', size=20),
        'family_name': fields.char('Last Name', size=200),
        'given_name': fields.char('First Name', size=200),
        'middle_names': fields.char('Middle Names', size=200),
        'dob': fields.datetime('Date of Birth'),
        'gender': fields.selection(_gender, string='Gender'),
        'sex': fields.selection(_gender, string='Sex'),
        'ethnicity': fields.selection(_ethnicity, string='Ethnicity'),
        'title': fields.many2one('res.partner.title', 'Title')
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        data = vals.copy()
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_data(cr, uid, data, create=False, context=context)
        return super(nh_clinical_adt_patient_update, self).submit(cr, uid, activity_id, data, context)

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        patient_pool = self.pool['nh.clinical.patient']
        vals = {
            'title': activity.data_ref.title.id,
            'patient_identifier': activity.data_ref.patient_identifier,
            'other_identifier': activity.data_ref.other_identifier,
            'family_name': activity.data_ref.family_name,
            'given_name': activity.data_ref.given_name,
            'middle_names': activity.data_ref.middle_names,
            'dob': activity.data_ref.dob,
            'gender': activity.data_ref.gender,
            'sex': activity.data_ref.sex,
            'ethnicity': activity.data_ref.ethnicity
        }
        res = patient_pool.write(cr, uid, activity.data_ref.patient_id.id, vals, context=context)
        super(nh_clinical_adt_patient_update, self).complete(cr, uid, activity_id, context)
        return res


class nh_clinical_adt_patient_admit(orm.Model):
    """
        Generates a patient Admission to the provided Location.
        It will generate a new ward location if it does not exist.
            
       consulting and referring doctors are expected in the submitted values on key='doctors' in format:
       [...
       {
       'type': 'c' or 'r',
       'code': code string,
       'title':, 'given_name':, 'family_name':, }
       ...]
       
       if doctor doesn't exist, we create partner, but don't create user
    """
    
    _name = 'nh.clinical.adt.patient.admit'
    _inherit = ['nh.activity.data']      
    _description = 'ADT Patient Admit'    
    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Admission Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'location': fields.char('Location', size=256),
        'code': fields.char("Code", size=256),
        'start_date': fields.datetime("Admission Date"),
        'other_identifier': fields.char('Hospital Number', size=20),
        'doctors': fields.text("Doctors")
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if not user.pos_id or not user.pos_id.location_id:
            raise osv.except_osv('POS Missing Error!', "POS location is not set for user.login = %s!" % user.login)
        if not vals.get('location'):
            raise osv.except_osv('Admission Error!', 'Location must be set for admission!')
        if not vals.get('other_identifier'):
            raise osv.except_osv('Admission Error!', 'Patient must be set for admission!')
        location_pool = self.pool['nh.clinical.location']
        location_id = location_pool.get_by_code(cr, uid, vals['location'], auto_create=True, context=context)
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        data = vals.copy()
        data.update({
            'location_id': location_id,
            'patient_id': patient_id,
            'pos_id': user.pos_id.id
        })
        return super(nh_clinical_adt_patient_admit, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_admit, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        admission_pool = self.pool['nh.clinical.patient.admission']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        admission_data = {
            'pos_id': activity.data_ref.pos_id.id,
            'patient_id': activity.data_ref.patient_id.id,
            'location_id': activity.data_ref.location_id.id,
            'code': activity.data_ref.code,
            'start_date': activity.data_ref.start_date
        }
        if activity.data_ref.doctors:
            doctor_pool = self.pool['nh.clinical.doctor']
            admission_data.update({'doctors': activity.data_ref.doctors})
            doctor_pool.evaluate_doctors_dict(cr, uid, admission_data, context=context)
            del admission_data['doctors']
        admission_id = admission_pool.create_activity(cr, uid, {'creator_id': activity_id}, admission_data,
                                                      context=context)
        activity_pool.complete(cr, uid, admission_id, context=context)
        spell_id = activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.spell'], ['creator_id', '=', admission_id]], context=context)[0]
        activity_pool.write(cr, SUPERUSER_ID, activity_id, {'parent_id': spell_id})
        return res  

    
class nh_clinical_adt_patient_cancel_admit(orm.Model):
    """
    Cancels the last admission of the patient which cancels the current patient spell.
    """
    _name = 'nh.clinical.adt.patient.cancel_admit'
    _inherit = ['nh.activity.data']  
    _description = 'ADT Cancel Patient Admit'    
    _columns = {
        'other_identifier': fields.char('Hospital Number', size=20, required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'admission_id': fields.many2one('nh.activity', 'Admission Activity')
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        if not vals.get('other_identifier'):
            raise osv.except_osv('Cancel Admit Error!', 'Patient must be set!')
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        spell_pool = self.pool['nh.clinical.spell']
        activity_pool = self.pool['nh.activity']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, exception='False', context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        activity_pool.write(cr, uid, activity_id, {'parent_id': spell.activity_id.id}, context=context)
        admission_pool = self.pool['nh.clinical.patient.admission']
        admission_id = admission_pool.get_last(cr, uid, patient_id, exception='False', context=context)
        data = vals.copy()
        data.update({'patient_id': patient_id, 'admission_id': admission_id})
        return super(nh_clinical_adt_patient_cancel_admit, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_cancel_admit, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        activity_pool.cancel(cr, uid, activity.data_ref.admission_id.id, context=context)
        return res


class nh_clinical_adt_patient_discharge(orm.Model):
    """
    Discharge a patient from the hospital. Completes the patient spell.
    """
    _name = 'nh.clinical.adt.patient.discharge'
    _inherit = ['nh.activity.data']  
    _description = 'ADT Patient Discharge'
    _columns = {
        'other_identifier': fields.char('Hospital Number', size=20, required=True),
        'discharge_date': fields.datetime('Discharge Date'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True)
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        if not vals.get('other_identifier'):
            raise osv.except_osv('Discharge Error!', 'Patient must be set!')
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        discharge_date = vals.get('discharge_date') if vals.get('discharge_date') else dt.now().strftime(DTF)
        spell_pool = self.pool['nh.clinical.spell']
        activity_pool = self.pool['nh.activity']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, exception='False', context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        data = vals.copy()
        data.update({'patient_id': patient_id, 'discharge_date': discharge_date})
        activity_pool.write(cr, uid, activity_id, {'parent_id': spell.activity_id.id}, context=context)
        return super(nh_clinical_adt_patient_discharge, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_discharge, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        discharge_pool = self.pool['nh.clinical.patient.discharge']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        discharge_data = {
            'patient_id': activity.data_ref.patient_id.id,
            'discharge_date': activity.data_ref.discharge_date
        }
        discharge_id = discharge_pool.create_activity(cr, uid, {'creator_id': activity_id}, discharge_data,
                                                      context=context)
        activity_pool.complete(cr, uid, discharge_id, context=context)
        return res


class nh_clinical_adt_patient_cancel_discharge(orm.Model):
    """
    Cancels the last patient discharge. The spell will be reopened. This will fail if the patient has already been
    admitted again.
    """
    _name = 'nh.clinical.adt.patient.cancel_discharge'
    _inherit = ['nh.activity.data']
    _description = 'ADT Cancel Patient Discharge'
    _columns = {
        'other_identifier': fields.char('Hospital Number', size=20, required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'discharge_id': fields.many2one('nh.activity', 'Discharge Activity')
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        if not vals.get('other_identifier'):
            raise osv.except_osv('Cancel Discharge Error!', 'Patient must be set!')
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        discharge_pool = self.pool['nh.clinical.patient.discharge']
        discharge_id = discharge_pool.get_last(cr, uid, patient_id, exception='False', context=context)
        data = vals.copy()
        data.update({'patient_id': patient_id, 'discharge_id': discharge_id})
        return super(nh_clinical_adt_patient_cancel_discharge, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_cancel_discharge, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        activity_pool.cancel(cr, uid, activity.data_ref.discharge_id.id, context=context)
        activity_pool.write(cr, uid, activity_id, {'parent_id': activity.data_ref.discharge_id.parent_id.id},
                            context=context)
        return res


class nh_clinical_adt_patient_transfer(orm.Model):
    """
    Transfers a patient from a location to another location.
    It will trigger admission policy in the destination location.
    """
    _name = 'nh.clinical.adt.patient.transfer'
    _inherit = ['nh.activity.data']
    _description = 'ADT Patient Transfer'      
    _columns = {
        'other_identifier': fields.char('Hospital Number', size=20, required=True),
        'location': fields.char('Location', size=256),
        'location_id': fields.many2one('nh.clinical.location', 'Transfer Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True)
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if not user.pos_id or not user.pos_id.location_id:
            raise osv.except_osv('POS Missing Error!', "POS location is not set for user.login = %s!" % user.login)
        if not vals.get('location'):
            raise osv.except_osv('Transfer Error!', 'Location must be set for transfer!')
        if not vals.get('other_identifier'):
            raise osv.except_osv('Transfer Error!', 'Patient must be set for transfer!')
        location_pool = self.pool['nh.clinical.location']
        location_id = location_pool.get_by_code(cr, uid, vals['location'], auto_create=True, context=context)
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        spell_pool = self.pool['nh.clinical.spell']
        activity_pool = self.pool['nh.activity']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, exception='False', context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        activity_pool.write(cr, uid, activity_id, {'parent_id': spell.activity_id.id}, context=context)
        data = vals.copy()
        data.update({
            'location_id': location_id,
            'patient_id': patient_id
        })
        return super(nh_clinical_adt_patient_transfer, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        transfer_pool = self.pool['nh.clinical.patient.transfer']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        transfer = activity.data_ref
        transfer_data = {
            'patient_id': transfer.patient_id.id,
            'location_id': transfer.location_id.id
        }
        transfer_id = transfer_pool.create_activity(cr, uid, {'creator_id': activity_id}, transfer_data,
                                                    context=context)
        activity_pool.complete(cr, uid, transfer_id, context=context)
        return res


class nh_clinical_adt_patient_cancel_transfer(orm.Model):
    """
    Cancels the last patient transfer. Effectively moving the patient back to the origin location.
    """
    _name = 'nh.clinical.adt.patient.cancel_transfer'
    _inherit = ['nh.activity.data']
    _description = 'ADT Cancel Patient Transfer'
    _columns = {
        'other_identifier': fields.char('Hospital Number', size=20, required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'transfer_id': fields.many2one('nh.activity', 'Transfer Activity')
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        if not vals.get('other_identifier'):
            raise osv.except_osv('Cancel Transfer Error!', 'Patient must be set!')
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        transfer_pool = self.pool['nh.clinical.patient.transfer']
        transfer_id = transfer_pool.get_last(cr, uid, patient_id, exception='False', context=context)
        data = vals.copy()
        data.update({'patient_id': patient_id, 'transfer_id': transfer_id})
        return super(nh_clinical_adt_patient_cancel_transfer, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_patient_cancel_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        cancel = activity.data_ref
        activity_pool.cancel(cr, uid, cancel.transfer_id.id, context=context)
        activity_pool.write(cr, uid, activity_id, {'parent_id': cancel.transfer_id.parent_id.id},
                            context=context)
        return res


class nh_clinical_adt_spell_update(orm.Model):
    """
    Update patient spell information.
    """
    _name = 'nh.clinical.adt.spell.update'
    _inherit = ['nh.activity.data']
    _description = 'ADT Spell Update'
    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Admission Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'location': fields.char('Location', size=256),
        'code': fields.char("Code", size=256),
        'start_date': fields.datetime("Admission Date"),
        'other_identifier': fields.char('Hospital Number', size=20),
        'doctors': fields.text("Doctors"),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if not user.pos_id or not user.pos_id.location_id:
            raise osv.except_osv('POS Missing Error!', "POS location is not set for user.login = %s!" % user.login)
        if not vals.get('location'):
            raise osv.except_osv('Update Error!', 'Location must be set for spell update!')
        if not vals.get('other_identifier'):
            raise osv.except_osv('Update Error!', 'Patient must be set for spell update!')
        location_pool = self.pool['nh.clinical.location']
        location_id = location_pool.get_by_code(cr, uid, vals['location'], auto_create=True, context=context)
        patient_pool = self.pool['nh.clinical.patient']
        patient_pool.check_hospital_number(cr, uid, vals['other_identifier'], exception='False', context=context)
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals['other_identifier']]],
                                         context=context)[0]
        spell_pool = self.pool['nh.clinical.spell']
        activity_pool = self.pool['nh.activity']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, exception='False', context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        activity_pool.write(cr, uid, activity_id, {'parent_id': spell.activity_id.id}, context=context)
        data = vals.copy()
        data.update({
            'location_id': location_id,
            'patient_id': patient_id,
            'pos_id': user.pos_id.id
        })
        return super(nh_clinical_adt_spell_update, self).submit(cr, uid, activity_id, data, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        res = super(nh_clinical_adt_spell_update, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        update = activity.data_ref
        update_data = {
            'pos_id': update.pos_id.id,
            'code': update.code,
            'start_date': update.start_date
        }
        if update.doctors:
            doctor_pool = self.pool['nh.clinical.doctor']
            update_data.update({'doctors': update.doctors})
            doctor_pool.evaluate_doctors_dict(cr, uid, update_data, context=context)
            del update_data['doctors']
        else:
            update_data.update({'con_doctor_ids': [[5]], 'ref_doctor_ids': [[5]]})
        activity_pool.submit(cr, uid, activity.parent_id.id, update_data, context=context)
        location_pool = self.pool['nh.clinical.location']
        if not location_pool.is_child_of(cr, uid, activity.parent_id.location_id.id, update.location, context=context):
            move_pool = self.pool['nh.clinical.patient.move']
            move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID, {
                'parent_id': activity.parent_id.id,
                'creator_id': activity_id
            }, {
                'patient_id': update.patient_id.id,
                'location_id': update.location_id.id
            }, context=context)
            activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context=context)
            # trigger transfer policy activities
            self.trigger_policy(cr, uid, activity_id, location_id=update.location_id.id, context=context)
        return res
        

class nh_clinical_adt_patient_merge(orm.Model):
    """
    Merges a patient into another patient making the resulting patient own all activities.
    """
    _name = 'nh.clinical.adt.patient.merge'
    _inherit = ['nh.activity.data'] 
    _description = 'ADT Patient Merge'
    _columns = {
        'from_identifier': fields.text('From patient Identifier'),
        'into_identifier': fields.text('Into Patient Identifier'),        
    }

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_patient_merge, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        merge_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        except_if(not (merge_activity.data_ref.from_identifier and merge_activity.data_ref.into_identifier), msg="from_identifier or into_identifier not found in submitted data!")
        patient_pool = self.pool['nh.clinical.patient']
        from_id = patient_pool.search(cr, uid, [('other_identifier', '=', merge_activity.data_ref.from_identifier)])
        into_id = patient_pool.search(cr, uid, [('other_identifier', '=', merge_activity.data_ref.into_identifier)])
        except_if(not(from_id and into_id), msg="Source or destination patient not found!")
        from_id = from_id[0]
        into_id = into_id[0]
        # compare and combine data. may need new cursor to have the update in one transaction
        for model_name in self.pool.models.keys():
            model_pool = self.pool[model_name]
            if model_name.startswith("nh.clinical") and model_pool._auto and 'patient_id' in model_pool._columns.keys() and model_name != self._name and model_name != 'nh.clinical.notification' and model_name != 'nh.clinical.patient.observation':
                ids = model_pool.search(cr, uid, [('patient_id', '=', from_id)], context=context)
                if ids:
                    model_pool.write(cr, uid, ids, {'patient_id': into_id}, context=context)
        activity_ids = activity_pool.search(cr, uid, [('patient_id', '=', from_id)], context=context)
        activity_pool.write(cr, uid, activity_ids, {'patient_id': into_id}, context=context)
        from_data = patient_pool.read(cr, uid, from_id, context)
        into_data = patient_pool.read(cr, uid, into_id, context)
        vals_into = {}
        for fk, fv in from_data.iteritems():
            if not fv:
                continue
            if fv and into_data[fk] and fv != into_data[fk]:
                pass
            if fv and not into_data[fk]:
                if '_id' == fk[-3:]:
                    vals_into.update({fk: fv[0]})
                else:
                    vals_into.update({fk: fv})
        res['merge_into_update'] = patient_pool.write(cr, uid, into_id, vals_into, context)
        res['merge_from_deactivate'] = patient_pool.write(cr, uid, from_id, {'active': False}, context)
        return res