"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'admin', 'manager', 'staff', 'viewer')")
    op.execute("CREATE TYPE candidatestatus AS ENUM ('registered', 'presented', 'accepted', 'rejected', 'processing', 'hired')")
    op.execute("CREATE TYPE applicationstatus AS ENUM ('pending', 'accepted', 'rejected')")
    op.execute("CREATE TYPE joiningnoticestatus AS ENUM ('draft', 'pending', 'approved', 'rejected')")
    op.execute("CREATE TYPE employmenttype AS ENUM ('haken', 'ukeoi')")
    op.execute("CREATE TYPE housingtype AS ENUM ('shataku', 'own', 'rental', 'other')")
    op.execute("CREATE TYPE documenttype AS ENUM ('rirekisho', 'photo', 'zairyu_card', 'license', 'contract', 'other')")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('role', postgresql.ENUM('super_admin', 'admin', 'manager', 'staff', 'viewer', name='userrole', create_type=False), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'])

    # Candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('legacy_id', sa.Integer(), nullable=True),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('name_kana', sa.String(100), nullable=True),
        sa.Column('name_romanji', sa.String(100), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('marital_status', sa.String(20), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('building_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('mobile', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('visa_type', sa.String(50), nullable=True),
        sa.Column('visa_expiry', sa.Date(), nullable=True),
        sa.Column('residence_card_number', sa.String(20), nullable=True),
        sa.Column('passport_number', sa.String(20), nullable=True),
        sa.Column('passport_expiry', sa.Date(), nullable=True),
        sa.Column('height', sa.Numeric(5, 1), nullable=True),
        sa.Column('weight', sa.Numeric(5, 1), nullable=True),
        sa.Column('shoe_size', sa.Numeric(4, 1), nullable=True),
        sa.Column('waist', sa.Numeric(5, 1), nullable=True),
        sa.Column('uniform_size', sa.String(10), nullable=True),
        sa.Column('blood_type', sa.String(5), nullable=True),
        sa.Column('vision_right', sa.Numeric(3, 1), nullable=True),
        sa.Column('vision_left', sa.Numeric(3, 1), nullable=True),
        sa.Column('wears_glasses', sa.Boolean(), nullable=True),
        sa.Column('dominant_hand', sa.String(10), nullable=True),
        sa.Column('emergency_contact_name', sa.String(100), nullable=True),
        sa.Column('emergency_contact_relation', sa.String(50), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(20), nullable=True),
        sa.Column('japanese_level', sa.String(10), nullable=True),
        sa.Column('listening_level', sa.String(10), nullable=True),
        sa.Column('speaking_level', sa.String(10), nullable=True),
        sa.Column('reading_level', sa.String(10), nullable=True),
        sa.Column('writing_level', sa.String(10), nullable=True),
        sa.Column('education_level', sa.String(50), nullable=True),
        sa.Column('major', sa.String(100), nullable=True),
        sa.Column('work_history', postgresql.JSONB(), nullable=True),
        sa.Column('qualifications', postgresql.JSONB(), nullable=True),
        sa.Column('family_members', postgresql.JSONB(), nullable=True),
        sa.Column('reason_for_applying', sa.Text(), nullable=True),
        sa.Column('self_pr', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('registered', 'presented', 'accepted', 'rejected', 'processing', 'hired', name='candidatestatus', create_type=False), server_default='registered', nullable=False),
        sa.Column('interview_result', sa.String(50), nullable=True),
        sa.Column('interview_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidates_full_name', 'candidates', ['full_name'])
    op.create_index('ix_candidates_status', 'candidates', ['status'])
    op.create_index('ix_candidates_legacy_id', 'candidates', ['legacy_id'])

    # Candidate documents table
    op.create_table(
        'candidate_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('document_type', postgresql.ENUM('rirekisho', 'photo', 'zairyu_card', 'license', 'contract', 'other', name='documenttype', create_type=False), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidate_documents_candidate_id', 'candidate_documents', ['candidate_id'])

    # Client companies table
    op.create_table(
        'client_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_kana', sa.String(200), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('fax', sa.String(20), nullable=True),
        sa.Column('contact_person', sa.String(100), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('billing_rate_default', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_client_companies_name', 'client_companies', ['name'])

    # Applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('client_company_id', sa.Integer(), nullable=True),
        sa.Column('client_company_name', sa.String(200), nullable=True),
        sa.Column('presented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'accepted', 'rejected', name='applicationstatus', create_type=False), server_default='pending', nullable=False),
        sa.Column('result_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_company_id'], ['client_companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_applications_candidate_id', 'applications', ['candidate_id'])
    op.create_index('ix_applications_status', 'applications', ['status'])

    # Company apartments table
    op.create_table(
        'company_apartments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('building_name', sa.String(100), nullable=True),
        sa.Column('room_number', sa.String(20), nullable=True),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_occupants', sa.Integer(), server_default='0', nullable=False),
        sa.Column('monthly_rent', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_company_apartments_name', 'company_apartments', ['name'])

    # Joining notices table
    op.create_table(
        'joining_notices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('employment_type', postgresql.ENUM('haken', 'ukeoi', name='employmenttype', create_type=False), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('name_kana', sa.String(100), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('visa_type', sa.String(50), nullable=True),
        sa.Column('visa_expiry', sa.Date(), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('building_name', sa.String(100), nullable=True),
        sa.Column('housing_type', postgresql.ENUM('shataku', 'own', 'rental', 'other', name='housingtype', create_type=False), server_default='rental', nullable=False),
        sa.Column('apartment_id', sa.Integer(), nullable=True),
        sa.Column('move_in_date', sa.Date(), nullable=True),
        sa.Column('assignment_company_id', sa.Integer(), nullable=True),
        sa.Column('assignment_company', sa.String(200), nullable=True),
        sa.Column('assignment_location', sa.String(200), nullable=True),
        sa.Column('assignment_line', sa.String(100), nullable=True),
        sa.Column('job_description', sa.String(200), nullable=True),
        sa.Column('hourly_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('billing_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('bank_account_name', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('branch_number', sa.String(10), nullable=True),
        sa.Column('branch_name', sa.String(100), nullable=True),
        sa.Column('account_number', sa.String(20), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'approved', 'rejected', name='joiningnoticestatus', create_type=False), server_default='draft', nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id']),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id']),
        sa.ForeignKeyConstraint(['apartment_id'], ['company_apartments.id']),
        sa.ForeignKeyConstraint(['assignment_company_id'], ['client_companies.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_joining_notices_status', 'joining_notices', ['status'])
    op.create_index('ix_joining_notices_candidate_id', 'joining_notices', ['candidate_id'])

    # Employees table
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_number', sa.Integer(), nullable=False),
        sa.Column('joining_notice_id', sa.Integer(), nullable=True),
        sa.Column('candidate_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('office', sa.String(50), nullable=True),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('name_kana', sa.String(100), nullable=True),
        sa.Column('gender', sa.String(10), nullable=True),
        sa.Column('nationality', sa.String(50), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('visa_expiry', sa.Date(), nullable=True),
        sa.Column('visa_type', sa.String(50), nullable=True),
        sa.Column('has_spouse', sa.Boolean(), nullable=True),
        sa.Column('postal_code', sa.String(10), nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('building_name', sa.String(100), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('employment_type', postgresql.ENUM('haken', 'ukeoi', name='employmenttype', create_type=False), nullable=False),
        sa.Column('housing_type', postgresql.ENUM('shataku', 'own', 'rental', 'other', name='housingtype', create_type=False), nullable=True),
        sa.Column('apartment_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['joining_notice_id'], ['joining_notices.id']),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id']),
        sa.ForeignKeyConstraint(['apartment_id'], ['company_apartments.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_number')
    )
    op.create_index('ix_employees_employee_number', 'employees', ['employee_number'])
    op.create_index('ix_employees_full_name', 'employees', ['full_name'])
    op.create_index('ix_employees_status', 'employees', ['status'])
    op.create_index('ix_employees_employment_type', 'employees', ['employment_type'])

    # Haken assignments table
    op.create_table(
        'haken_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('client_company_id', sa.Integer(), nullable=True),
        sa.Column('client_company', sa.String(200), nullable=True),
        sa.Column('assignment_location', sa.String(200), nullable=True),
        sa.Column('assignment_line', sa.String(100), nullable=True),
        sa.Column('job_description', sa.String(200), nullable=True),
        sa.Column('hourly_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('hourly_rate_history', sa.Text(), nullable=True),
        sa.Column('billing_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('billing_rate_history', sa.Text(), nullable=True),
        sa.Column('profit_margin', sa.Numeric(5, 2), nullable=True),
        sa.Column('standard_salary', sa.Numeric(10, 2), nullable=True),
        sa.Column('health_insurance', sa.Numeric(10, 2), nullable=True),
        sa.Column('nursing_insurance', sa.Numeric(10, 2), nullable=True),
        sa.Column('pension', sa.Numeric(10, 2), nullable=True),
        sa.Column('social_insurance_enrolled', sa.Boolean(), nullable=True),
        sa.Column('apartment_name', sa.String(100), nullable=True),
        sa.Column('move_in_date', sa.Date(), nullable=True),
        sa.Column('move_out_date', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('current_hire_date', sa.Date(), nullable=True),
        sa.Column('visa_alert', sa.String(50), nullable=True),
        sa.Column('license_type', sa.String(50), nullable=True),
        sa.Column('license_expiry', sa.Date(), nullable=True),
        sa.Column('commute_method', sa.String(50), nullable=True),
        sa.Column('optional_insurance_expiry', sa.Date(), nullable=True),
        sa.Column('japanese_certification', sa.String(20), nullable=True),
        sa.Column('career_up_5th_year', sa.String(50), nullable=True),
        sa.Column('entry_request', sa.String(200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['client_company_id'], ['client_companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_haken_assignments_employee_id', 'haken_assignments', ['employee_id'])

    # Ukeoi assignments table
    op.create_table(
        'ukeoi_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), server_default='active', nullable=False),
        sa.Column('job_type', sa.String(100), nullable=True),
        sa.Column('hourly_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('hourly_rate_history', sa.Text(), nullable=True),
        sa.Column('profit_margin', sa.Numeric(5, 2), nullable=True),
        sa.Column('standard_salary', sa.Numeric(10, 2), nullable=True),
        sa.Column('health_insurance', sa.Numeric(10, 2), nullable=True),
        sa.Column('nursing_insurance', sa.Numeric(10, 2), nullable=True),
        sa.Column('pension', sa.Numeric(10, 2), nullable=True),
        sa.Column('social_insurance_enrolled', sa.Boolean(), nullable=True),
        sa.Column('commute_distance', sa.Numeric(6, 1), nullable=True),
        sa.Column('transport_allowance', sa.Numeric(10, 2), nullable=True),
        sa.Column('apartment_name', sa.String(100), nullable=True),
        sa.Column('move_in_date', sa.Date(), nullable=True),
        sa.Column('move_out_date', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('visa_alert', sa.String(50), nullable=True),
        sa.Column('bank_account_name', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('branch_number', sa.String(10), nullable=True),
        sa.Column('branch_name', sa.String(100), nullable=True),
        sa.Column('account_number', sa.String(20), nullable=True),
        sa.Column('entry_request', sa.String(200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ukeoi_assignments_employee_id', 'ukeoi_assignments', ['employee_id'])

    # Audit log table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_table_name', 'audit_logs', ['table_name'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('ukeoi_assignments')
    op.drop_table('haken_assignments')
    op.drop_table('employees')
    op.drop_table('joining_notices')
    op.drop_table('company_apartments')
    op.drop_table('applications')
    op.drop_table('client_companies')
    op.drop_table('candidate_documents')
    op.drop_table('candidates')
    op.drop_table('refresh_tokens')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE documenttype")
    op.execute("DROP TYPE housingtype")
    op.execute("DROP TYPE employmenttype")
    op.execute("DROP TYPE joiningnoticestatus")
    op.execute("DROP TYPE applicationstatus")
    op.execute("DROP TYPE candidatestatus")
    op.execute("DROP TYPE userrole")
