// ============================================
// ENUMS
// ============================================

export type UserRole = 'super_admin' | 'admin' | 'manager' | 'staff' | 'viewer'

export type CandidateStatus =
  | 'registered'
  | 'presented'
  | 'accepted'
  | 'rejected'
  | 'processing'
  | 'hired'

export type ApplicationStatus = 'pending' | 'accepted' | 'rejected'

export type JoiningNoticeStatus = 'draft' | 'pending' | 'approved' | 'rejected'

export type EmploymentType = 'haken' | 'ukeoi'

export type HousingType = 'shataku' | 'own' | 'rental' | 'other'

export type DocumentType = 'rirekisho' | 'photo' | 'zairyu_card' | 'license' | 'contract' | 'other'

// ============================================
// USER
// ============================================

export interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

// ============================================
// CANDIDATE (履歴書)
// ============================================

export interface FamilyMember {
  name?: string
  relation?: string
  age?: number
  living_together?: boolean
  address?: string
}

export interface WorkHistoryEntry {
  company_name?: string
  position?: string
  start_date?: string
  end_date?: string
  description?: string
}

export interface CandidateDocument {
  id: number
  document_type: DocumentType
  file_name: string
  file_url: string
  file_size: number | null
  mime_type: string | null
  uploaded_at: string
}

export interface Candidate {
  id: number
  legacy_id: number | null
  full_name: string
  name_kana: string | null
  name_romanji: string | null
  gender: string | null
  nationality: string | null
  birth_date: string | null
  marital_status: string | null
  postal_code: string | null
  address: string | null
  building_name: string | null
  phone: string | null
  mobile: string | null
  email: string | null
  visa_type: string | null
  visa_expiry: string | null
  residence_card_number: string | null
  passport_number: string | null
  passport_expiry: string | null
  height: number | null
  weight: number | null
  shoe_size: number | null
  waist: number | null
  uniform_size: string | null
  blood_type: string | null
  vision_right: number | null
  vision_left: number | null
  wears_glasses: boolean | null
  dominant_hand: string | null
  emergency_contact_name: string | null
  emergency_contact_relation: string | null
  emergency_contact_phone: string | null
  japanese_level: string | null
  listening_level: string | null
  speaking_level: string | null
  reading_level: string | null
  writing_level: string | null
  education_level: string | null
  major: string | null
  work_history: WorkHistoryEntry[] | null
  qualifications: string[] | null
  family_members: FamilyMember[] | null
  reason_for_applying: string | null
  self_pr: string | null
  notes: string | null
  status: CandidateStatus
  interview_result: string | null
  interview_notes: string | null
  created_at: string
  updated_at: string | null
  documents: CandidateDocument[]
}

export interface CandidateListResponse {
  items: Candidate[]
  total: number
  page: number
  page_size: number
  pages: number
}

// ============================================
// APPLICATION (申請)
// ============================================

export interface Application {
  id: number
  candidate_id: number
  client_company_id: number | null
  client_company_name: string | null
  presented_at: string | null
  status: ApplicationStatus
  result_at: string | null
  result_notes: string | null
  created_at: string
  created_by: number | null
}

// ============================================
// JOINING NOTICE (入社連絡票)
// ============================================

export interface JoiningNotice {
  id: number
  application_id: number | null
  candidate_id: number
  employment_type: EmploymentType
  full_name: string
  name_kana: string | null
  gender: string | null
  nationality: string | null
  birth_date: string | null
  visa_type: string | null
  visa_expiry: string | null
  postal_code: string | null
  address: string | null
  building_name: string | null
  housing_type: HousingType
  apartment_id: number | null
  move_in_date: string | null
  assignment_company_id: number | null
  assignment_company: string | null
  assignment_location: string | null
  assignment_line: string | null
  job_description: string | null
  hourly_rate: number | null
  billing_rate: number | null
  bank_account_name: string | null
  bank_name: string | null
  branch_number: string | null
  branch_name: string | null
  account_number: string | null
  status: JoiningNoticeStatus
  submitted_at: string | null
  approved_at: string | null
  approved_by: number | null
  rejection_reason: string | null
  created_at: string
  updated_at: string | null
  created_by: number | null
}

// ============================================
// EMPLOYEE (社員)
// ============================================

export interface HakenAssignment {
  id: number
  employee_id: number
  status: string
  client_company_id: number | null
  client_company: string | null
  assignment_location: string | null
  assignment_line: string | null
  job_description: string | null
  hourly_rate: number | null
  hourly_rate_history: string | null
  billing_rate: number | null
  billing_rate_history: string | null
  profit_margin: number | null
  standard_salary: number | null
  health_insurance: number | null
  nursing_insurance: number | null
  pension: number | null
  social_insurance_enrolled: boolean | null
  apartment_name: string | null
  move_in_date: string | null
  move_out_date: string | null
  start_date: string | null
  end_date: string | null
  current_hire_date: string | null
  visa_alert: string | null
  license_type: string | null
  license_expiry: string | null
  commute_method: string | null
  optional_insurance_expiry: string | null
  japanese_certification: string | null
  career_up_5th_year: string | null
  entry_request: string | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface UkeoiAssignment {
  id: number
  employee_id: number
  status: string
  job_type: string | null
  hourly_rate: number | null
  hourly_rate_history: string | null
  profit_margin: number | null
  standard_salary: number | null
  health_insurance: number | null
  nursing_insurance: number | null
  pension: number | null
  social_insurance_enrolled: boolean | null
  commute_distance: number | null
  transport_allowance: number | null
  apartment_name: string | null
  move_in_date: string | null
  move_out_date: string | null
  start_date: string | null
  end_date: string | null
  visa_alert: string | null
  bank_account_name: string | null
  bank_name: string | null
  branch_number: string | null
  branch_name: string | null
  account_number: string | null
  entry_request: string | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface Employee {
  id: number
  employee_number: number
  joining_notice_id: number | null
  candidate_id: number | null
  status: string
  office: string | null
  full_name: string
  name_kana: string | null
  gender: string | null
  nationality: string | null
  birth_date: string | null
  visa_expiry: string | null
  visa_type: string | null
  has_spouse: boolean | null
  postal_code: string | null
  address: string | null
  building_name: string | null
  hire_date: string | null
  termination_date: string | null
  photo_url: string | null
  employment_type: EmploymentType
  housing_type: HousingType | null
  apartment_id: number | null
  created_at: string
  updated_at: string | null
  haken_assignment: HakenAssignment | null
  ukeoi_assignment: UkeoiAssignment | null
}

// ============================================
// DASHBOARD
// ============================================

export interface DashboardStats {
  candidates: {
    total: number
    new: number
    pending: number
  }
  applications: {
    pending: number
  }
  joining_notices: {
    pending_approval: number
    draft: number
  }
  employees: {
    total_active: number
    haken: number
    ukeoi: number
  }
  alerts: {
    visa_expiring_soon: number
  }
}

export interface RecentActivity {
  recent_candidates: ActivityItem[]
  recent_applications: ActivityItem[]
  recent_approvals: ActivityItem[]
}

export interface ActivityItem {
  type: string
  id: number
  name?: string
  company?: string
  status: string
  timestamp: string | null
}
