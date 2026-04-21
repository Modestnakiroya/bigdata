-- ============================================
-- Global Patent Intelligence Database Schema
-- ============================================

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS patent_relationships;
DROP TABLE IF EXISTS inventors;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS patents;

-- ============================================
-- PATENTS TABLE
-- ============================================
CREATE TABLE patents (
    patent_id     TEXT PRIMARY KEY,
    title         TEXT,
    abstract      TEXT,
    filing_date   TEXT,
    year          INTEGER,
    patent_type   TEXT,
    num_claims    INTEGER
);

-- ============================================
-- INVENTORS TABLE
-- ============================================
CREATE TABLE inventors (
    inventor_id   TEXT PRIMARY KEY,
    name          TEXT,
    country       TEXT
);

-- ============================================
-- COMPANIES TABLE
-- ============================================
CREATE TABLE companies (
    company_id    TEXT PRIMARY KEY,
    name          TEXT
);

-- ============================================
-- RELATIONSHIPS TABLE
-- ============================================
CREATE TABLE patent_relationships (
    patent_id     TEXT,
    inventor_id   TEXT,
    company_id    TEXT,
    FOREIGN KEY (patent_id)   REFERENCES patents(patent_id),
    FOREIGN KEY (inventor_id) REFERENCES inventors(inventor_id),
    FOREIGN KEY (company_id)  REFERENCES companies(company_id)
);