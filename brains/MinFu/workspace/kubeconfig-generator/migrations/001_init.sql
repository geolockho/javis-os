-- kubeconfig-generator: schema ban đầu (PostgreSQL >= 12)
-- App tự chạy file này lúc khởi động (dưới advisory lock), có ghi vào schema_migrations.

CREATE TABLE IF NOT EXISTS access_request (
    id                 BIGSERIAL PRIMARY KEY,
    requester_email    TEXT        NOT NULL,
    cluster            TEXT        NOT NULL,
    namespace          TEXT        NOT NULL,
    role               TEXT        NOT NULL DEFAULT 'view',
    requested_seconds  INTEGER     NOT NULL CHECK (requested_seconds >= 600),
    status             TEXT        NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled', 'issuing',
                          'issued', 'expired', 'revoked', 'revoke_failed')),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    decided_by         TEXT,
    decided_at         TIMESTAMPTZ,
    reject_reason      TEXT,
    claim_deadline     TIMESTAMPTZ,          -- hạn nhận sau khi duyệt
    issuing_started_at TIMESTAMPTZ,
    issued_at          TIMESTAMPTZ,          -- thời điểm dev tải
    sa_name            TEXT,
    token_expires_at   TIMESTAMPTZ,          -- lấy từ expirationTimestamp của TokenRequest
    revoked_by         TEXT,
    revoked_at         TIMESTAMPTZ,
    last_error         TEXT
);

CREATE INDEX IF NOT EXISTS access_request_requester_idx ON access_request (requester_email, status);
CREATE INDEX IF NOT EXISTS access_request_status_idx ON access_request (status);

-- Chống trùng: cùng dev, cluster, namespace chỉ có 1 request còn hiệu lực
CREATE UNIQUE INDEX IF NOT EXISTS access_request_one_active_idx
    ON access_request (requester_email, cluster, namespace)
    WHERE status IN ('pending', 'approved', 'issuing', 'issued');

CREATE TABLE IF NOT EXISTS download_link (
    id          BIGSERIAL PRIMARY KEY,
    request_id  BIGINT      NOT NULL REFERENCES access_request (id),
    token_hash  TEXT        NOT NULL UNIQUE,   -- sha256 hex, không lưu token gốc
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS download_link_request_idx ON download_link (request_id);

CREATE TABLE IF NOT EXISTS audit_log (
    id               BIGSERIAL PRIMARY KEY,
    at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor            TEXT        NOT NULL,   -- email từ SSO hoặc 'system'
    action           TEXT        NOT NULL,   -- request_created, approved, rejected, link_created, downloaded, ...
    result           TEXT        NOT NULL,   -- ok | denied | error
    request_id       BIGINT,
    requester_email  TEXT,
    cluster          TEXT,
    namespace        TEXT,
    role             TEXT,
    approver         TEXT,
    downloaded_at    TIMESTAMPTZ,
    token_expires_at TIMESTAMPTZ,
    detail           TEXT
);

CREATE INDEX IF NOT EXISTS audit_log_request_idx ON audit_log (request_id);
CREATE INDEX IF NOT EXISTS audit_log_at_idx ON audit_log (at DESC);

-- Audit chỉ thêm: chặn UPDATE, DELETE, TRUNCATE ở mức DB
CREATE OR REPLACE FUNCTION audit_log_append_only() RETURNS trigger
    LANGUAGE plpgsql AS
$$
BEGIN
    RAISE EXCEPTION 'audit_log chỉ cho phép INSERT';
END;
$$;

DROP TRIGGER IF EXISTS audit_log_no_update ON audit_log;
CREATE TRIGGER audit_log_no_update
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_append_only();

DROP TRIGGER IF EXISTS audit_log_no_truncate ON audit_log;
CREATE TRIGGER audit_log_no_truncate
    BEFORE TRUNCATE ON audit_log
    FOR EACH STATEMENT EXECUTE FUNCTION audit_log_append_only();
