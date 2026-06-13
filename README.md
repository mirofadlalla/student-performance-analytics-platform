# KAYFA Analytics Intelligence Dashboard

**Real-time student performance analytics, risk detection, and cohort intelligence for data-driven academic interventions**

A production-grade Data Analytics & Engineering project that transforms raw educational data into actionable insights through advanced data cleaning, feature engineering, and interactive visualizations.

---

## 📊 Overview

The KAYFA Analytics Intelligence Dashboard is a comprehensive **data-driven analytics platform** designed to monitor student performance, identify at-risk learners, and provide institutional leadership with real-time cohort health metrics.

### Why This Project?

Modern educational institutions need to move beyond spreadsheets and reactive reporting. The KAYFA platform:
- **Detects at-risk students** before they fail using multi-dimensional risk scoring
- **Tracks concept mastery** across the curriculum to identify teaching gaps
- **Analyzes group/class dynamics** to reveal cohort-level performance patterns
- **Audits data quality** continuously, resolving 41 distinct integrity issues across heterogeneous data sources
- **Provides actionable insights** backed by evidence-based visualizations and recommendations

### Expected Users

- **Academic Leaders** – Track cohort health KPIs, identify struggling groups
- **Instructors** – Discover difficult concepts, monitor student engagement trends
- **Data Analysts** – Explore cleaned datasets, validate multi-source data integration
- **Students** (future) – Personal performance tracking and personalized recommendations

### Key Outcomes

✅ **95%+ Data Quality** – ETL pipeline resolves 41 verified data integrity issues  
✅ **Real-time KPIs** – 5 core metrics computed from 500+ student records  
✅ **Risk Segmentation** – Students classified into 4 risk tiers (High Achievers → At-Risk Disengaged)  
✅ **Curriculum Insights** – Concept failure heatmap identifying hardest concepts per course  
✅ **Deployment-Ready** – Production pipeline on Streamlit Cloud + MongoDB Atlas  

---

## 🎯 Features

### 📈 Executive Overview
- **KPI Dashboard** – Total students, platform avg grade, attendance rate, at-risk count, pass percentage
- **Attendance Trends** – Monthly platform-wide attendance tracking with threshold alerts
- **Grade Trends** – Monthly average grade by group with pass threshold visualization
- **Cohort Segmentation** – Donut chart showing distribution across 4 student segments
- **At-Risk Signals** – Top underperforming students ranked by composite risk score

### 🎓 Student Intelligence
- **Student Roster** – Ranked table with filters (name, group, risk level, performance tier)
- **Risk Segmentation** – Scatter plot: attendance vs. grade with segment classification
- **Risk Distribution** – Histogram showing count of students by risk level
- **Performance Charts** – Grade and engagement distributions across cohort
- **Drill-Down Capability** – Individual student profiles with key metrics

### 👥 Group Performance
- **Attendance Leaderboard** – Ranked bar chart highlighting above/below-platform-average groups
- **Grade Trend Lines** – Multi-series monthly trends per group with pass threshold overlay
- **Group Comparison** – Summary table with KPIs per group (instructor, attendance, enrollment discrepancies)
- **Underperformance Alerts** – Actionable recommendations for lowest-performing groups

### 🧠 Concept Intelligence
- **Failure Rate Ranking** – Top 15 hardest concepts with severity color-coding
- **Heatmap Analysis** – Failure rates by concept × course, identifying weak spots in curriculum
- **Course Comparison** – Average failure rate per course, revealing relative difficulty
- **Concept Mastery KPIs** – Total concepts, average mastery rate, critical concepts (≥50% failure)

### 🛡️ Data Quality Audit
- **Comprehensive Audit Log** – All 41 data integrity issues documented with resolution status
   - Duplicates (rows, IDs, emails)
   - Missing values (null names, scores, instructors)
   - Invalid data (negative ages, impossible scores >100, malformed emails)
   - Referential integrity (orphan records, wrong group assignments)
   - Temporal violations (records before enrollment)
   - ETL artifacts (injected test data, sentinel values)
   - Logical inconsistencies (mastery status at cutoff score, late submission flags)
- **Status Tracking** – All 41 issues marked "Resolved" or "Flagged" with action taken
- **Category Breakdown** – Issues grouped by type (Duplicate, Missing, Invalid, Referential, Temporal, Logical, ETL Artifact, Encoding)

---

## 🏗️ Architecture

### End-to-End Data Pipeline

```mermaid
graph LR
    A["Raw Data Sources<br/>(CSV, JSON, Excel)"] -->|Load| B["Data Ingestion<br/>(Pandas)"]
    B -->|Clean| C["Data Cleaning<br/>(Duplicates, Missing Values)"]
    C -->|Validate| D["Data Validation<br/>(Referential Integrity, Ranges)"]
    D -->|Engineer| E["Feature Engineering<br/>(Risk Scores, Aggregations)"]
    E -->|Normalize| F["Data Normalization<br/>(Encoding, Types)"]
    F -->|Store| G["MongoDB Atlas<br/>(Collections)"]
    G -->|Query| H["Streamlit App<br/>(Multi-page Dashboard)"]
    H -->|Visualize| I["Interactive Dashboards<br/>(Plotly Charts)"]
    I -->|Display| J["User Interface<br/>(Web Browser)"]
```

### Data Flow Layers

1. **Raw Data Layer** – 8 source datasets in heterogeneous formats (CSV, JSON, Excel) containing 500+ students across 10 groups
2. **Ingestion Layer** – Pandas DataFrames load and normalize all sources into unified schema
3. **Cleaning Layer** – 41-point audit framework removes duplicates, corrects invalid data, imputes missing values
4. **Validation Layer** – Cross-dataset referential integrity checks, temporal consistency, logical constraints
5. **Feature Engineering Layer** – Derive KPIs (risk scores, mastery rates, engagement metrics, attendance rates)
6. **Storage Layer** – MongoDB Atlas collections persist cleaned, feature-enriched data
7. **Application Layer** – Streamlit multi-page app with 5 dashboard pages
8. **Presentation Layer** – Plotly interactive visualizations with drill-down, filtering, and insights

---

## 📚 Dataset Description

### 1. **students** (500 records)
The main student entity table containing demographic and enrollment data.

**Key Columns:**
- `student_id` (string) – Unique identifier (e.g., S0001)
- `full_name` (string) – Student name (cleaned, null values imputed from email)
- `group_id` (string) – Group/class identifier (G01–G10)
- `course_id` (string) – Course code (C001–C007)
- `course_name` (string) – Course title (e.g., Python Fundamentals)
- `instructor` (string) – Assigned instructor name
- `att_rate_pct` (float) – Overall attendance rate as percentage (0–100)
- `avg_grade` (float) – Average grade across all assessments (0–100)
- `failed_concepts` (int) – Count of concepts not mastered
- `late_submissions` (int) – Count of late assignment submissions
- `login_count` (int) – Total platform logins over term
- `total_events` (int) – Total engagement events (logins, video views, etc.)
- `gender` (string) – Gender (normalized to Male/Female)
- `age` (int) – Student age in years (cleaned, outliers corrected)

**Data Quality Issues Resolved:** 6 – Duplicates at EOF, 4 NULL names (imputed), impossible ages (corrected), 10 gender encoding variants (normalized), 3 malformed emails (rebuilt), 97 duplicate email addresses (reconciled)

**Referential Integrity:** 3 non-existent group_ids (GZZ, G77) – corrected to valid groups

---

### 2. **grades** (500+ records)
Normalized from grades.json; contains all assessment scores per student.

**Key Columns:**
- `student_id` (string) – Student reference
- `course_id` (string) – Course reference
- `group_id` (string) – Group reference
- `assessment_type` (string) – Type of assessment (Quiz, Assignment, Final Exam, etc.)
- `score` (float) – Numeric score (0–100, cleaned to remove negatives and out-of-range values)
- `max_score` (float) – Maximum possible score (typically 100; corrected inconsistencies)
- `date_submitted` (datetime) – Submission timestamp

**Data Quality Issues Resolved:** 2 negative scores (GR00001, GR00045), 1 over-range score 187 > 100 (GR00013), 1 max_score=10 vs 100 inconsistency (corrected), 2 NULL scores (imputed with course average), 1 sentinel bonus exam (GR99999 - removed), 1 course mismatch (S0010 final exam from wrong course - corrected)

---

### 3. **attendance** (3500+ records)
Session attendance logs across all groups, spanning 6+ months.

**Key Columns:**
- `record_id` (string) – Unique identifier
- `student_id` (string) – Student reference
- `group_id` (string) – Group reference
- `date_session` (datetime) – Session date
- `session_day` (string) – Day of week (Monday–Sunday)
- `status` (string) – Attendance status (Attended, Absent, Late)
- `session_time` (string) – Session start time in HH:MM format

**Data Quality Issues Resolved:** 2 duplicate record_ids (4 total rows), 1 typo "Atttended" (normalized), 1 orphan student S9999 (removed), 606 records before enrollment (flagged), 13 records for wrong assigned group (corrected), 4 bad-data test records (AT900001–AT900004 - removed), 2 temporal mismatches (session on wrong day of week - corrected)

**Aggregation:** Attendance rate = (Attended count / Total sessions) × 100%

---

### 4. **concepts_performance** (100+ records)
Learning outcomes per concept; derived from quizzes and concept mastery assessments.

**Key Columns:**
- `concept_id` (string) – Unique concept identifier (e.g., C002-K05)
- `concept_name` (string) – Human-readable concept name (e.g., Recursion)
- `course_id` (string) – Parent course
- `failure_rate_pct` (float) – Percentage of students failing this concept
- `mastery_status` (string) – Re-derived from score ≥60 threshold (cleaned inconsistencies at boundary)

**Data Quality Issues Resolved:** 5 duplicate record_ids (10 rows), 2 out-of-range scores (CPBAD02: -33, CPBAD03: 142 - removed), 13 inconsistent mastery_status at score=60 (re-derived using consistent rule)

**Key Finding:** Recursion has an 85.3% failure rate—the hardest concept across all courses.

---

### 5. **engagement_events** (25000+ records)
Granular engagement activity: logins, video watches, resource downloads, forum posts.

**Key Columns:**
- `event_id` (string) – Unique identifier
- `student_id` (string) – Student reference
- `event_type` (string) – Type (login, video_watch, forum_post, resource_download, etc.)
- `timestamp` (datetime) – When event occurred
- `duration_seconds` (float) – Duration for applicable events; NULL for instantaneous events like login

**Data Quality Issues Resolved:** 8 duplicate event_ids (16 rows), 2 negative durations (-120 seconds - corrected), 1 sentinel value 99999 seconds (27.8 hours - corrected to reasonable estimate), 1 orphan student S8888 (removed), 2 sentinel IDs (EVBAD01, EVBAD02 - removed), 1 event 11 months before enrollment (flagged)

**Structural Note:** 22,049 NULL duration_seconds (71%) is expected—video_watch and login events don't have discrete durations.

**Aggregations:**
- `total_events` = count of all events per student
- `login_count` = count of login events
- Engagement Score = weighted combination of event diversity and frequency

---

### 6. **assignment_submissions** (1500+ records)
Student submissions on homework, projects, and quizzes.

**Key Columns:**
- `submission_id` (string) – Unique identifier
- `student_id` (string) – Student reference
- `assignment_id` (string) – Assignment reference
- `submitted_at` (datetime) – Submission timestamp
- `due_at` (datetime) – Due date
- `is_late` (bool) – Whether submission was tardy
- `time_spent_minutes` (float) – Estimated time spent on assignment

**Data Quality Issues Resolved:** 3 duplicate submission_ids (6 rows), 1 negative time (-40 minutes - corrected), 1 NULL submitted_at with is_late=False (is_late set to NaN), 2 is_late=True despite on-time timestamps (recalculated), 1 NULL submitted_at (flagged for manual review)

**Aggregation:**
- `late_submissions` = count of submissions with is_late=True

---

### 7. **groups** (10 records)
Class/cohort metadata and instructor assignments.

**Key Columns:**
- `group_id` (string) – Unique identifier (G01–G10)
- `course_id` (string) – Course taught in this group
- `course_name` (string) – Course title
- `instructor` (string) – Primary instructor name
- `session_day` (string) – Primary session day (Monday–Sunday)
- `session_time` (string) – Normal session start time (HH:MM)
- `stated_num_students` (int) – Enrollment count from registration
- `actual_count` (int) – Actual student count from students table

**Data Quality Issues Resolved:** 1 exact duplicate row for G01 (deduplicated), 1 test record G99 / TEST_GROUP_DELETE (removed), 1 NULL instructor on G99 (removed with G99), 3 session_time formats (HH:MM, H PM, HHMM - normalized to HH:MM)

**Known Issues (Flagged):** 5 groups with stated_num_students ≠ actual_count (G03, G05, G07, G08, G10) – discrepancy documented in audit

---

### 8. **courses** (7 records)
Course catalog and metadata.

**Key Columns:**
- `course_id` (string) – Unique identifier (C001–C007)
- `course_name` (string) – Human-readable title
- `department` (string) – Academic department
- `duration_weeks` (int) – Course length in weeks

**Courses Include:**
- C001: Python Fundamentals
- C002: Data Structures & Algorithms
- C003: Machine Learning
- C004: Web Development
- C005: Digital Marketing
- C006: Database Design
- C007: Cybersecurity Essentials

**Data Quality:** No issues detected in courses table.

---

## 🔍 Data Quality & Cleaning

### Comprehensive Issue Resolution Log

The project documents and resolves **41 distinct data integrity issues** across 8 heterogeneous datasets:

| **Category** | **Count** | **Examples** |
|---|---|---|
| **Duplicates** | 12 | 2 student rows, 97 duplicate emails, 5 concept IDs, 8 event IDs, 3 submission IDs, 2 attendance records, 1 group row |
| **Missing Values** | 6 | 4 NULL student names, 2 NULL grades, 22,049 NULL engagement durations (structural) |
| **Invalid Data** | 7 | 3 impossible ages, 1 negative score, 1 over-range score >100, 1 max_score inconsistency, 2 negative durations, 1 malformed email |
| **Referential Integrity** | 8 | 3 non-existent group_ids, 97 duplicate emails, 2 student-group mismatches in grades, 1 orphan student in attendance, 1 orphan student in engagement |
| **Temporal Violations** | 4 | 606 attendance records before enrollment, 1 event 11 months before enrollment, 2 sessions on wrong day of week |
| **Encoding/Format** | 4 | 10 gender encoding variants, 3 session_time formats, 1 "Atttended" typo |
| **ETL Artifacts** | 10 | 1 bonus exam (GR99999), 1 course-wrong final exam (GR99998), 1 test group (G99), 4 bad-data records (AT900001–AT900004, EV00001–EV00002), 2 out-of-range concept scores (CPBAD02, CPBAD03), 1 sentinel value 99999 seconds |
| **Logical Inconsistencies** | 3 | 13 mastery_status at score=60 boundary, 2 is_late flags on on-time submissions, 1 NULL submitted_at with is_late=False |
| **Discrepancies** | 5 | stated_num_students ≠ actual_count in 5 groups (flagged, not automatically corrected) |

### Handling Strategies

**Duplicates:** Detected via `duplicated()` and `drop_duplicates()`. Root cause: ETL pipeline merges from multiple sources.

**Missing Values:**
- **Structural NULL** (e.g., engagement duration): Documented and preserved for analysis
- **Imputation:** Student names rebuilt from email; course avg imputed for 2 missing grades; age mean imputed for 1 outlier

**Invalid Data:**
- **Ranges:** Scores clipped to [0, 100]; ages corrected to positive values; negative durations set to 0
- **Referential:** Orphan records removed; wrong group_ids corrected via student table
- **Temporal:** Records before enrollment flagged in audit, excluded from analysis

**Encoding:** Gender normalized via name-based gender classifier; timestamps parsed to datetime; session times standardized to HH:MM

**ETL Artifacts:** Sentinel records (test data, bonus exams) identified by ID patterns and removed

**Logical Rules Re-applied:**
- Mastery status: `score ≥ 60 → "Passed"`, else `"Failed"` (13 boundary inconsistencies corrected)
- Late submission: `submitted_at > due_at → is_late=True` (recalculated, not trusted from source)

---

## 🗄️ MongoDB Design

### Collections & Schema

#### 1. **students_master**
Complete student profiles with all attributes ready for dashboard consumption.

```json
{
  "student_id": "S0001",
  "full_name": "Ahmed Ali Student1",
  "group_id": "G01",
  "course_id": "C001",
  "course_name": "Python Fundamentals",
  "instructor": "Dr. Amira",
  "att_rate_pct": 85.3,
  "avg_grade": 78.5,
  "failed_concepts": 3,
  "late_submissions": 1,
  "login_count": 45,
  "total_events": 92,
  "gender": "Male",
  "age": 21
}
```

**Indexes:** `student_id` (primary), `group_id` (group filters), `att_rate_pct`, `avg_grade` (sorting)

---

#### 2. **group_summaries**
Aggregated KPIs per cohort for group performance page.

```json
{
  "group_id": "G01",
  "course_name": "Python Fundamentals",
  "instructor": "Dr. Amira",
  "att_rate_pct": 78.5,
  "actual_count": 52,
  "stated_num_students": 50
}
```

**Aggregation Pipeline:** MongoDB aggregates `students_master` grouping by `group_id`, computing mean `att_rate_pct`, count, etc.

---

#### 3. **at_risk_students**
Top 10 highest-risk students for early intervention (computed daily/on-demand).

```json
{
  "student_id": "S0453",
  "full_name": "Marwan ElBaz",
  "group_id": "G07",
  "overall_att": 42.1,
  "avg_grade": 51.3,
  "failed_concepts": 22,
  "recent_att": 38.0,
  "total_events": 21,
  "risk_score": 84.7
}
```

**Risk Score Formula:**
$$\text{Risk Score} = 0.35 \times (100 - \text{att\_rate}) + 0.45 \times (100 - \text{grade}) + 0.2 \times (\text{failed\_concepts} / \text{max\_concepts})$$

Normalized to 0–100 scale, where 100 = highest risk.

---

#### 4. **concept_failures**
Concept mastery rates; one row per concept across all courses.

```json
{
  "concept_id": "C002-K05",
  "concept_name": "Recursion",
  "course_id": "C002",
  "failure_rate_pct": 85.3
}
```

**Calculation:** `failure_rate = (count_failed / total_attempts) × 100%`

---

#### 5. **grade_trends**
Time-series of monthly average grades per group (supports trend lines).

```json
{
  "true_group": "G01",
  "month": "2026-01",
  "avg_score": 73.2
}
```

**Granularity:** Monthly aggregates of `grades` collection, grouped by `group_id`

---

#### 6. **attendance_trends**
Platform-wide attendance over time (supports platform attendance chart).

```json
{
  "month": "2026-01",
  "att_rate": 79.1
}
```

---

#### 7. **cluster_segments**
Student segmentation results from engagement + performance clustering.

```json
{
  "student_id": "S0001",
  "full_name": "Ahmed Ali Student1",
  "segment": "High Achievers",
  "att_rate": 84.2,
  "avg_grade": 76.5,
  "total_events": 92,
  "failed_concepts": 2
}
```

**Segments:**
- **High Achievers** (37%): Grade ≥ 75, Att ≥ 80% – strong across all dimensions
- **Average Engaged** (28%): Grade 60–74, Att 70–80% – steady performers
- **Struggling** (21%): Grade < 70, Att < 75% – need support
- **At-Risk Disengaged** (14%): Grade < 60, Att < 70%, many failed concepts – urgent intervention

---

### Key Aggregations & KPIs

| **KPI** | **Formula** | **Freshness** |
|---|---|---|
| **Avg Grade (Platform)** | Mean of all `avg_grade` in students_master | Real-time (cached 5 min) |
| **Avg Attendance (Platform)** | Mean of all `att_rate_pct` in students_master | Real-time (cached 5 min) |
| **Total Students** | Count of documents in students_master | Real-time |
| **At-Risk Count** | Count where `risk_score ≥ 70` | On-demand computation |
| **Pass Rate** | Count where `avg_grade ≥ 60` / total × 100% | Real-time |
| **Concept Mastery Rate** | Mean of (100 - `failure_rate_pct`) | Real-time |
| **Engagement Score (per student)** | `total_events` / 100 (normalized 0–1) | Real-time |

---

## 📊 Analytics & KPIs

### Core Metrics Computed by the Dashboard

#### 1. **Student Performance Metrics**
- **Average Grade:** Mean of all assessment scores (0–100)
- **High Performer Classification:** Grade ≥ 75
- **Failing Student Classification:** Grade < 60
- **Pass Rate:** Percentage of students with grade ≥ 60

#### 2. **Attendance Metrics**
- **Overall Attendance Rate:** (Sessions attended / Total sessions) × 100%
- **Platform Attendance:** Mean attendance rate across all students
- **Group Attendance Ranking:** Mean attendance per group (identifies struggling cohorts)
- **Attendance Trend:** Month-over-month attendance rates

#### 3. **Risk Scoring & Segmentation**
- **Composite Risk Score (0–100):**
  - Incorporates: attendance rate (35%), grade (45%), concept failures (20%)
  - Higher score = higher risk of non-completion
  - Stratified into 3 risk tiers:
    - 🟢 **Low Risk:** Risk < 60 AND Grade ≥ 70 AND Att ≥ 75%
    - 🟡 **Medium Risk:** 60 ≤ Risk < 70 OR Grade 60–69 OR Att 65–74%
    - 🔴 **High Risk:** Risk ≥ 70 OR Grade < 60 OR Att < 65%

- **Student Segments (K-means clustering):**
  - High Achievers (37% of cohort)
  - Average Engaged (28%)
  - Struggling (21%)
  - At-Risk Disengaged (14%)

#### 4. **Engagement Metrics**
- **Total Events:** Count of all platform interactions (logins, video views, forum posts, downloads)
- **Login Count:** Frequency of platform access
- **Late Submissions:** Count of assignments submitted after due date
- **Failed Concepts:** Count of concepts not mastered (score < 60)

#### 5. **Concept Mastery & Curriculum Metrics**
- **Concept Failure Rate:** Percentage of students failing each concept (0–100%)
- **Platform Avg Mastery:** 100% - Platform's average failure rate
- **Critical Concepts:** Concepts with failure rate ≥ 50% (prioritize intervention)
- **Course Difficulty Ranking:** Average failure rate per course

#### 6. **Cohort Health Indicators**
- **Group Avg Grade (Monthly):** Trend lines per cohort showing learning trajectory
- **Pass/Fail Volume:** Absolute student counts in pass/fail categories
- **Enrollment Discrepancy:** stated_num_students vs. actual_count (flags administrative issues)
- **Instructor Performance:** Proxy = group's average grade and attendance

---

## 📱 Dashboard Walkthrough

### Page 1: Executive Overview
**Purpose:** High-level platform health snapshot for leadership.

**Key Visualizations:**
- 5 KPI cards: Total students, avg grade, avg attendance, at-risk count, pass %
- Monthly attendance trend line with platform average benchmark
- Grade trend lines by group (multi-series) with pass threshold overlay
- Student segment donut (High Achievers → At-Risk Disengaged)
- Top 10 at-risk students ranked table with action recommendations

**Filters:** None (page shows platform-wide aggregates)

**Insight Boxes:**
- "Platform attendance dipped to 62.2% in March 2026" → Seasonal factor → Pre-schedule makeup sessions
- "G07 stayed below 60-point pass threshold" → Low attendance + high concept failure → Assign dedicated tutor

---

### Page 2: Student Intelligence
**Purpose:** Granular student-level performance drill-down with risk assessment.

**Key Visualizations:**
- 5 KPI cards: Total students, high performers, failing count, platform avg grade, platform avg attendance
- Live search box (by name)
- Filters: Group selector, Risk Level (High/Medium/Low), Performance Tier (High/On-Track/Failing)
- Ranked student roster (sorted by avg_grade descending) with columns: Name, Group, Course, Attendance %, Grade, Failed Concepts, Late Submissions, Risk Level
- Scatter plot: Attendance vs. Grade with segment color-coding
- Risk distribution histogram
- Top 10 students by engagement (total_events metric)

**Filters:** Name search, Group, Risk Level, Performance Tier

**Drill-Down:** Click any student row → (future) individual profile page with time-series engagement data

---

### Page 3: Group Performance
**Purpose:** Cohort-level analysis to reveal class-wide patterns.

**Key Visualizations:**
- 5 KPI cards: Total groups, best attendance group, worst attendance group, groups below average, platform avg attendance
- Attendance leaderboard (bars colored for above/below platform average)
- Monthly grade trends by group (multi-series line chart)
- Group comparison table: Group ID, Course, Instructor, Attendance %, Actual Enrollment, Stated Enrollment
- Group roster drilldown (students per group)

**Filters:** Group selector (multi-select future enhancement)

**Insight Box:**
- "G07 (60.2%) and G10 (65.4%) are most attendance-challenged" → Scheduling conflicts or engagement issues → Audit session times, survey students

---

### Page 4: Concept Intelligence
**Purpose:** Identify curriculum weak spots and design targeted remediation.

**Key Visualizations:**
- 5 KPI cards: Total concepts, avg failure rate, critical concepts (≥50% failure), hardest concept, avg mastery rate
- Top 15 concepts by failure rate (horizontal bar, color-coded red ≥70%, amber 50–69%, blue <50%)
- Concept failure heatmap (rows = concepts, columns = courses, color intensity = failure %)
- Average failure rate per course (bar chart)

**Filters:** Course selector (to filter heatmap by course)

**Insight Box:**
- "Recursion has an 85.3% failure rate—the hardest concept" → Abstract thinking challenge → Add 2 supplementary sessions, create step-through visualizations

---

### Page 5: Data Quality Audit
**Purpose:** Transparency into ETL pipeline robustness and data confidence.

**Key Visualizations:**
- Hero section: "41 data integrity issues detected and resolved"
- Status badges: ✅ Audit Complete
- Full audit table (41 rows):
  - Issue ID (#01–#41)
  - Category (Duplicate, Missing, Invalid, Referential, Temporal, Encoding, ETL Artifact, Logical)
  - Dataset affected
  - Severity (Low, Medium, High, Critical)
  - Description (specific issue)
  - Status (Resolved or Flagged)
- Category breakdown chart (count by type)
- Severity breakdown chart (count by severity level)
- Timeline: Issues resolved during data pipeline development

**No Filters** (page is informational/audit-focused)

---

## 🛠️ Tech Stack

| **Layer** | **Technology** | **Version** | **Purpose** |
|---|---|---|---|
| **Backend** | Python | ≥ 3.8 | Core ETL logic |
| **Data Processing** | Pandas | ≥ 2.0.0 | Data manipulation, aggregation |
| **Numerical Computing** | NumPy | ≥ 1.24.0 | Vectorized operations |
| **Database** | MongoDB Atlas | Cloud | Production data storage |
| **Database Driver** | PyMongo | ≥ 4.6.0 | MongoDB Python client |
| **Web Framework** | Streamlit | ≥ 1.32.0 | Multi-page interactive dashboard |
| **Visualization** | Plotly | ≥ 5.18.0 | Interactive charts & graphs |
| **Machine Learning (Optional)** | Scikit-learn | ≥ 1.4.0 | K-means clustering for segmentation |
| **Statistics** | SciPy | ≥ 1.12.0 | Statistical calculations |
| **SSL/TLS** | Certifi | ≥ 2024.2.2 | MongoDB SSL certificate validation |
| **Environment** | python-dotenv | ≥ 1.0.0 | Manage secrets locally (dev) |
| **DNS** | dnspython | ≥ 2.6.0 | MongoDB SRV record resolution |

---

## 📁 Project Structure

```
kayfa_dashboard/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── app.py                             # Main Streamlit entry point
├── db.py                              # MongoDB integration & shared UI components
├── pages/
│   ├── __init__.py                   # Package marker
│   ├── overview.py                   # Executive overview dashboard
│   ├── students.py                   # Student intelligence & filters
│   ├── groups.py                     # Group performance analysis
│   ├── concepts.py                   # Concept mastery & curriculum
│   └── audit.py                      # Data quality audit report
├── data/
│   ├── students.csv                  # Student master data (~500 rows)
│   ├── groups.csv                    # Group/cohort metadata (10 rows)
│   ├── courses.csv                   # Course catalog (7 rows)
│   ├── grades.json                   # Student assessment scores
│   ├── attendance.xlsx               # Session attendance logs
│   ├── concepts_performance.csv      # Concept mastery rates
│   ├── engagement_events.csv         # Platform activity logs (~25k rows)
│   └── assignment_submissions.csv    # Assignment submissions (~1.5k rows)
└── Student_Analytics_Updated.ipynb   # ETL pipeline & feature engineering notebook
```

---

## ⚙️ Installation

### Prerequisites
- **Python** 3.8 or later
- **MongoDB Atlas** account with a free cluster (M0)
- **Streamlit Cloud** account (for deployment)

### Local Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/kayfa-analytics-dashboard.git
cd kayfa-analytics-dashboard/kayfa_dashboard
```

#### 2. Create a Python Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up MongoDB Atlas
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster (M0)
3. In **Network Access**, add your IP (or 0.0.0.0 for anywhere)
4. Create a database user with username & password
5. Copy the **connection string** (SRV format):
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/StudentAnalytics?retryWrites=true&w=majority
   ```

#### 5. Create a `.env` File Locally (Development Only)
```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/StudentAnalytics?retryWrites=true&w=majority
DB_NAME=StudentAnalytics
```

#### 6. Load Data into MongoDB (First Run)
Run the Jupyter notebook `Student_Analytics_Updated.ipynb` to:
- Load raw CSV/JSON/Excel files
- Execute the 41-point data quality audit
- Clean and validate data
- Feature engineer KPIs
- Insert cleaned collections into MongoDB

**Alternative:** Pymongo script (to be provided) to directly insert demo or cleaned data.

#### 7. Run Streamlit Locally
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🚀 Streamlit Cloud Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial KAYFA dashboard commit"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click **New app** → Connect your GitHub repo
3. Select:
   - Repository: `yourusername/kayfa-analytics-dashboard`
   - Branch: `main`
   - Main file path: `kayfa_dashboard/app.py`

4. Click **Deploy**

### 3. Configure Secrets (Critical)

On your deployed Streamlit app:
1. Go to **App menu** (top-right) → **Settings** → **Secrets**
2. Add this TOML configuration:

```toml
# .streamlit/secrets.toml on Streamlit Cloud

MONGO_URI = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/StudentAnalytics?retryWrites=true&w=majority"
DB_NAME = "StudentAnalytics"
```

**Important:** Never commit `secrets.toml` to Git. Streamlit Cloud keeps secrets encrypted server-side.

### 4. Verify Deployment

- App live at: `https://yourapp-hash.streamlit.app`
- Check logs in Streamlit Cloud dashboard for errors
- If MongoDB connection fails, verify:
  - Connection string correct
  - IP whitelist includes Streamlit IP (or use 0.0.0.0)
  - Database `StudentAnalytics` exists
  - Collections are populated

### 5. Optional: Set Up Data Refresh
For production, consider:
- **Scheduled ETL job** (Cloud Run, Lambda) to refresh collections daily
- **Streamlit cache TTL** (already set to 300s for collections)
- **MongoDB aggregation pipelines** for real-time KPI computation

---

## 📈 Usage Examples

### Example 1: Identify At-Risk Students
1. Open **Student Intelligence** page
2. Filter: Risk Level = "High Risk"
3. Sort by Grade (ascending)
4. View: Top 20 students needing immediate intervention
5. Action: Email instructor with personalized recommendations

### Example 2: Audit a Struggling Group
1. Open **Group Performance** page
2. Click on "G07" row
3. View: 60.2% attendance, monthly grade below 60 threshold
4. Open **Concept Intelligence**, filter Course = "Data Structures & Algorithms" (G07's course)
5. Identify: Which concepts are hardest for this group
6. Action: Recommend curriculum adjustment, additional tutoring sessions

### Example 3: Explore Curriculum Weak Spots
1. Open **Concept Intelligence** page
2. View: Recursion (85.3%), Dynamic Programming (44.1%) are top failures
3. Heatmap: See which courses struggle most
4. Action: Allocate learning resources, create supplementary materials

### Example 4: Monitor Data Quality
1. Open **Data Quality Audit** page
2. Review: 41 issues, all "Resolved"
3. Sort by Severity: See Critical items first
4. Verify: All referential integrity and temporal issues addressed
5. Confidence: Proceed with data-driven decisions

---

## 🔄 Data Refresh & Maintenance

### Updating Data

**Local (Development):**
1. Place updated CSV/JSON/Excel files in `/data/`
2. Run `Student_Analytics_Updated.ipynb` to clean & validate
3. Collections auto-update in MongoDB (via `insert_many` with upsert)

**Production (Streamlit Cloud):**
1. Schedule a Cloud Function / Lambda to run ETL nightly
2. Function executes notebook or Python script
3. MongoDB collections updated with latest data
4. Streamlit cache invalidates after 5 minutes (auto-refreshes)

### Monitoring

- Log MongoDB connection health
- Track cache hit/miss rates
- Monitor Streamlit app performance
- Set up alerts for failed data loads

---

## 🧪 Testing Checklist

- [ ] Local Streamlit instance loads all 5 pages without errors
- [ ] MongoDB connection verified (demo data visible)
- [ ] Overview page shows non-zero KPI values
- [ ] Student filtering works (by name, group, risk, performance)
- [ ] Group attendance sorted correctly
- [ ] Concept heatmap displays top 15 concepts
- [ ] Audit page lists all 41 issues
- [ ] Plotly charts render interactively (hover, zoom, etc.)
- [ ] No console errors in Streamlit terminal
- [ ] Deployment to Streamlit Cloud successful
- [ ] Cloud secrets configured correctly
- [ ] Cloud app loads with same data as local

---

## 📝 Key Insights & Findings

### From the Current Dataset:

1. **G07 is the most at-risk group**
   - Attendance: 60.2% (lowest)
   - Grades: Below 60 for 6 months
   - Recommended action: Assignment of dedicated tutor, schedule audit

2. **Recursion is the hardest concept**
   - Failure rate: 85.3%
   - Affects primarily C002 (Data Structures & Algorithms)
   - Insight: Abstract thinking barrier; needs visualization & step-through materials

3. **Student segments aren't evenly distributed**
   - High Achievers: 37% (healthy)
   - At-Risk Disengaged: 14% (concerning minority)
   - Insight: Targeted interventions can move 14% to "Struggling" → "Average Engaged"

4. **Attendance dips in March**
   - Platform-wide drop to 62.2%
   - Likely external factor (exam period, holidays)
   - Recommendation: Pre-schedule makeup sessions before March

5. **Late submissions correlate with failing grades**
   - Students with ≥3 late submissions average 58.1 grade (vs. 71.4 for on-time)
   - Insight: Time management or engagement issue; intervention opportunity

---

## 🚨 Limitations & Future Enhancements

### Current Limitations
- **No user authentication** – Anyone with link can access all data (add Auth for production)
- **No real-time data** – 5-minute cache (can reduce to 1 minute for real-time)
- **No predictive models** – Currently descriptive analytics only (add churn prediction)
- **No drill-down exports** – Dashboard only; add CSV export capability
- **No mobile-optimized** – Best on desktop (Streamlit can handle mobile, but UX not optimized)

### Planned Enhancements
- ✅ **Predictive Churn Modeling** – Logistic regression to flag future dropouts
- ✅ **Individual Student Profiles** – Detailed time-series engagement plots
- ✅ **Automated Alerts** – Email/SMS when student crosses risk threshold
- ✅ **Instructor Dashboard** – Group-level only view (permission controls)
- ✅ **Parent Portal** – Student grades & attendance (anonymized)
- ✅ **Curriculum Optimization** – Recommendations based on concept failure patterns
- ✅ **API Endpoint** – REST API for third-party integration
- ✅ **Data Connectors** – Direct pulls from Canvas, Blackboard, other LMS

---

## 📄 License

This project is licensed under the **MIT License** – see LICENSE file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📧 Contact & Support

For questions, issues, or collaboration:
- **Email:** analytics@kayfa.io
- **GitHub Issues:** [Project Issues](https://github.com/yourusername/kayfa-analytics-dashboard/issues)
- **Documentation:** Full setup guide & API docs in `/docs/`

---

## 🙏 Acknowledgments

- Data sourced from Kayfa Institute's student information system
- Inspired by modern analytics platforms (Mixpanel, Amplitude, Graphy)
- Built with Python, Streamlit, MongoDB, and Plotly
- Special thanks to open-source community

---

## 📊 Quick Reference: Dashboard URLs (After Deployment)

| Page | Route | Purpose |
|---|---|---|
| Executive Overview | `https://app.streamlit.app/` | Platform health snapshot |
| Student Intelligence | `https://app.streamlit.app/?page=students` | Student drill-down |
| Group Performance | `https://app.streamlit.app/?page=groups` | Cohort analysis |
| Concept Intelligence | `https://app.streamlit.app/?page=concepts` | Curriculum insights |
| Data Quality Audit | `https://app.streamlit.app/?page=audit` | ETL transparency |

---

**Last Updated:** June 2026  
**Version:** 1.0.0 (Production Release)  
**Status:** ✅ Ready for Portfolio Submission
