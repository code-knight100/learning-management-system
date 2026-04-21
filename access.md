# 1. USER ✅
- register/login/logout route 
    - anyone can register
    - registered user can login with credentials and get token 
    - logged-in user can use token to logout or to access other APIs

- manage_user route: 
  - Student / Instructor / Sponsor:
    - view own user only
    - update own user (except role)
    - delete own account

  - Admin:
    - full CRUD on all users
    - can change role


# 2. PROFILE ✅
## Purpose
User personal information (OneToOne with User)

## Rules
- One user = One profile only

- Student / Instructor / Sponsor:
  - can view own profile only
  - can create only once 
  - can update own profile
  - cannot access others

- Admin:
  - full CRUD on all profiles
  - can assign profile to any user

## Validation
- Prevent duplicate profile per user
- Prevent changing user ownership (except admin)
- Protect OneToOne integrity

---

# 3. COURSE ✅
## Purpose
Main learning content

## Rules

- Instructor:
  - create courses, only own (not for other instructor)
  - view all courses
  - update/delete only own courses

- Student:
  - view all courses

- Sponsor:
  - view all courses

- Admin:
  - C (for instructor only), R (all), U (all), D (all)

## Validation
- Instructor must be course owner
- Prevent editing others’ courses

---

# 4. ENROLLMENT ✅
## Purpose
Student-course mapping

## Rules

- Student:
  - can create enrollment (can enroll in courses)
  - can view only own enrollments
  - cannot update/delete enrollments

- Instructor:
  - can view enrollments of their courses only

- Sponsor:
  - view all enrolments (bec. he is a sponsor)

- Admin:
  - C (for student only), R(all), U (any), D (any)

## Validation
- Prevent duplicate enrollment (student + course)
- Only students can create enrollment
- Enrollment must reference valid course + student

---

# 5. LESSON ✅
## Purpose
Course content structure

## Rules

- Instructor:
  - create/read/update/delete lessons of own course only

- Student:
  - view lessons of enrolled courses only

- Sponsor:
  - view lessons of courses 

- Admin:
  - full access

## Validation
- Lesson must belong to valid course
- Course ownership must match instructor
- Prevent unauthorized lesson creation outside course

---

# 6. ASSIGNMENT
## Purpose
Tasks for students

## Rules

- Instructor:
  - create assignments for own courses
  - update/delete own assignments

- Student:
  - view only assignments of enrolled courses
  - cannot create/update/delete

- Sponsor:
  - no access

- Admin:
  - full access

## Validation
- Assignment must belong to instructor’s course
- Prevent cross-course assignment creation
- Validate course ownership before creation

---

# 7. SUBMISSION
## Purpose
Student assignment submission

## Rules

- Student:
  - create submission
  - view own submissions only
  - cannot edit submission after deadline
  - canoot delete submission 

- Instructor:
  - view submissions of own assignments
  - grade submissions

- Sponsor:
  - no access 
- Admin:
  - full access

## Validation
- One submission per student per assignment
- Must belong to enrolled course
- Cannot submit after deadline
- Only enrolled students can submit

---

# 8. SPONSOR ✅
## Purpose
External funding entity

## Rules

- Sponsor:
  - can create own sponsor profile (if self-registration enabled)
  - can view own profile only
  - can update own profile
  - cannot delete own profile

- Admin:
  - full CRUD on all sponsor profiles

- Student:
  - no access

- Instructor:
  - no access


## Validation
- Sponsor linked to exactly one user (OneToOne, one user can have only one sponsor account)
- Prevent duplicate sponsor profiles
- Ensure sponsor role is assigned via group

---

# 9. SPONSORSHIP ✅
## Purpose
Funding relationship between sponsor, student, course

## Rules

- Sponsor:
  - can create own sponsorships
  - view own sponsorships
  - can create for  multiple students
  - can create for  multiple courses
  - cannot access sponsorships of other sponsors

- Student:
  - can view only their own sponsorships

- Instructor:
  - can view sponsorships related to their courses (read-only)

- Admin:
  - full access

## Validation
- Prevent duplicate sponsorship (same sponsor + student + course)
- Status must follow lifecycle (Pending → Active → Finished)
- Validate all foreign keys exist
- Sponsor must own the sponsorship record
- Student must exist and be valid user
- Course must exist and be valid course

---

# 10. PAYMENT ✅
## Purpose
Financial transaction tracking

## Rules

- Student:
  - can create payment (for course enrollment)
  - can view only their own payments
  - cannot edit payment 
  - cannot delete payment 

- Sponsor:
  - can create payment (for own sponsored students/courses)
  - can view only their own payments
  - cannot edit payment 
  - cannot delete payment 

- Instructor:
  - no access

- Admin:
  - can make payment for students only
  - can view all payments
  - cannot edit payment after creation
  - cannot delete payment (prevent fraud detection, auditing corectiness and legal reason )


## Validation
- transaction_id must be unique
- Payment must link to valid course/user/sponsorship
- Amount must be positive
- Status must follow payment lifecycle
- Only Student or Sponsor can create payments
- Prevent payment creation by Instructor
- Validate course or sponsorship linkage before payment save

---

# 11. NOTIFICATION ✅
## Purpose
System messaging

## Rules

- Instructor
 - create, view only own, edit , delete 

---

- Sponsor
 - create, view only own, edit , delete 

---

- Student
   - cannot create 
   - can read only related to his enrolled course 
   - can edit only marks as read field 

---

- Admin
    - can create notifications for any user 
    - can view all notifications
    - can edit notifications 
    - can delete notifications 


## Validation
- Notification must belong to valid user
- No cross-user access allowed
- Ensure recipient exists and is active user
- Prevent invalid role-based targeting
- Validate message content is not empty

---

# 12. EMAIL LOG 
## Purpose
Track system emails

## Rules

- Admin:
  - full access to email logs

- Student:
  - 

- Instructor:
  - no access

- Sponsor:
  - no access

## Validation
- Must be system-generated
- Cannot be manually modified by users
- Must reference valid user
- Ensure status is only system-controlled (Pending/Sent)

---

# FINAL ARCHITECTURE RULE

## Core System Flow

### Authentication
- User login → token/session

### Authorization
- Django Groups → role detection:
  - Student
  - Instructor
  - Sponsor
  - Admin

### Ownership Control
- user → Profile, Notification, Payment
- course.instructor → Course, Lesson, Assignment
- enrollment.student → Enrollment, Submission
- sponsorship.sponsor → Sponsorship, Payments (optional link)

### Data Access Control
- get_queryset() filtering
- object-level permission checks
- serializer validation rules

---

# GLOBAL VALIDATION PRINCIPLES

## Must ALWAYS enforce
- No duplicate ownership where OneToOne exists
- No cross-user data access
- Role-based access control (RBAC)
- Ownership-based filtering (request.user)
- Strict separation of roles even if all are "users"

## Security Layers
- 1. Permission classes (role check)
- 2. Queryset filtering (data visibility)
- 3. Serializer validation (data correctness)
- 4. Model constraints (final database safety)

---

# FINAL RESULT

This design ensures:
- Fully role-based LMS backend
- Strong data isolation between users
- Secure sponsorship + payment system
- Clean DRF architecture
- Production-level scalability for frontend integration



































# LMS Backend Authorization + Validation Plan (Based on Your Exact Models)

---

# 1. USER (AUTH SYSTEM)
## Purpose
- Core authentication model (Django User)
- Role system via Django Groups (Admin, Instructor, Student, Sponsor)

## Rules
- Only Admin manages users
- Users authenticate via token/session
- Roles define access (NOT is_staff)

## Validation
- Must belong to at least one group
- No direct frontend role manipulation

---

# 2. PROFILE
## Purpose
User personal information (OneToOne with User)

## Rules
- One user = One profile only
- Student:
  - can view own profile only
  - can create only once OR auto-created
  - can update own profile
  - cannot access others

- Admin:
  - full CRUD on all profiles
  - can assign profile to any user

## Validation
- Prevent duplicate profile per user
- Prevent changing user ownership (except admin)
- Protect OneToOne integrity

---

# 3. COURSE
## Purpose
Main learning content

## Rules
- Instructor:
  - create courses
  - update/delete only own courses
  - view own + public courses

- Student:
  - view only
  - cannot create/update/delete

- Sponsor:
  - view only (or sponsored courses if linked)

- Admin:
  - full CRUD

## Validation
- Instructor must be course owner
- Prevent editing others’ courses

---

# 4. ENROLLMENT
## Purpose
Student-course mapping

## Rules
- Student:
  - can enroll in courses
  - can view only own enrollments
  - cannot update/delete enrollments

- Instructor:
  - can view enrollments of their courses only

- Sponsor:
  - optional access to sponsored students only

- Admin:
  - full access

## Validation
- Prevent duplicate enrollment (student + course)
- Only students can create enrollment
- Enrollment must reference valid course + student

---

# 5. LESSON
## Purpose
Course content structure

## Rules
- Instructor:
  - create/update/delete lessons of own course only

- Student:
  - view lessons of enrolled courses only

- Admin:
  - full access

## Validation
- Lesson must belong to valid course
- Course ownership must match instructor

---

# 6. ASSIGNMENT
## Purpose
Tasks for students

## Rules
- Instructor:
  - create assignments for own courses
  - update/delete own assignments

- Student:
  - view only
  - cannot create/update/delete

- Admin:
  - full access

## Validation
- Assignment must belong to instructor’s course
- Prevent cross-course assignment creation

---

# 7. SUBMISSION
## Purpose
Student assignment submission

## Rules
- Student:
  - create submission
  - view own submissions only
  - cannot edit after submission (optional rule)

- Instructor:
  - view submissions of own assignments
  - grade submissions

- Admin:
  - full access

## Validation
- One submission per student per assignment (optional rule)
- Must belong to enrolled course
- Cannot submit after deadline

---

# 8. SPONSOR
## Purpose
External funding entity

## Rules
- Sponsor:
  - view own profile only
  - cannot access LMS academic data directly

- Admin:
  - full control

## Validation
- Sponsor linked to exactly one user (OneToOne,  one user can(sponsor) have only one sponsor account)
- Prevent duplicate sponsor profiles

---

# 9. SPONSORSHIP
## Purpose
Funding relationship between sponsor, student, course

## Rules
- Sponsor:
  - can create/view own sponsorships
  - cannot access others

- Admin:
  - full access

## Validation
- Prevent duplicate sponsorship (same sponsor + student + course)
- Status must follow lifecycle (Pending → Active → Finished)
- Validate all foreign keys exist

---

# 10. PAYMENT
## Purpose
Financial transaction tracking

## Rules
- Student:
  - can create payment (for course enrollment)
  - can view only their own payments

- Sponsor:
  - can create payment (for funding students/courses)
  - can view only their own payments

- Instructor:
  - cannot create payments
  - cannot view payments (unless explicitly allowed for reporting)

- Admin:
  - full access to all payments (create, view, update, delete)

## Validation
- transaction_id must be unique
- Payment must link to valid course/user/sponsorship
- Amount must be positive
- Status must follow payment lifecycle

---

# 11. NOTIFICATION
## Purpose
System messaging

## Rules
- User(instructor, stu, sponsor):
  - can view own notifications only
  - can mark as read

- Admin:
  - can send notifications to any user

## Validation
- Notification must belong to valid user
- No cross-user access allowed

---

# 12. EMAIL LOG
## Purpose
Track system emails

## Rules
- Admin only access

## Validation
- Must be system-generated
- Cannot be manually modified by users

---

# FINAL ARCHITECTURE RULE

## Core System Flow

### Authentication
- User login → token/session

### Authorization
- Django Groups → role detection

### Ownership Control
- user
- course.instructor
- enrollment.student
- sponsorship.sponsor

### Data Access Control
- get_queryset() filtering
- object-level permission checks
- serializer validation rules

---

# GLOBAL VALIDATION PRINCIPLES

## Must ALWAYS enforce
- No duplicate ownership where OneToOne exists
- No cross-user data access
- Role-based access control (RBAC)
- Ownership-based filtering (request.user)

## Security Layers
- 1. Permission classes (role check)
- 2. Queryset filtering (data visibility)
- 3. Serializer validation (data correctness)
- 4. Model constraints (final safety)

---

# FINAL RESULT

This design ensures:
- Secure LMS backend
- Role-based access control
- Clean DRF architecture
- Scalable system for frontend integration