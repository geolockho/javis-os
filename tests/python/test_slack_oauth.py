"""Regression test for the Slack MCP user OAuth request (Slack requires `scope`)."""
import json
import urllib.parse
from pathlib import Path

from _paths import ROOT  # noqa: E402
import oauth_mcp  # noqa: E402
import mcp_store  # noqa: E402


def main():
    failures = []
    def check(name, ok):
        print(("ok  " if ok else "FAIL ") + name)
        if not ok:
            failures.append(name)

    connector = json.loads((ROOT / "server/packs/javis.slack/connectors/slack.json").read_text(encoding="utf-8"))
    auth = connector["auth"]
    configured_scopes = list(auth["scopes"])
    configured_scope_param = auth["scope_param"]
    # Simulate the stale installed-pack metadata that produced the reported URL.
    auth["scope_param"] = "user_scope"
    auth["scopes"] = ["openid", "email", "profile", *configured_scopes]
    old_conn, old_secrets = oauth_mcp._conn, mcp_store.connection_secrets
    old_load, old_save = oauth_mcp._load, oauth_mcp._save
    oauth_mcp._load = lambda: {}
    oauth_mcp._save = lambda data: None
    oauth_mcp._conn = lambda conn_id: {"id": conn_id, "connector": connector}
    mcp_store.connection_secrets = lambda conn_id: {"client_id": "test-client-id", "client_secret": "test-client-secret"}
    try:
        flow = oauth_mcp.start_auth("test-slack", "http://localhost:7777/connect/oauth/callback")
        try:
            flow.send(None)
        except StopIteration as completed:
            result = completed.value
        else:
            flow.close()
            raise AssertionError("explicit Slack OAuth setup unexpectedly suspended")
        check("OAuth URL is generated", result.get("ok") is True)
        parsed = urllib.parse.urlparse(result.get("url", ""))
        query = urllib.parse.parse_qs(parsed.query)
        check("Slack MCP user OAuth endpoint", parsed.scheme + "://" + parsed.netloc + parsed.path == "https://slack.com/oauth/v2_user/authorize")
        check("connector config uses Slack's `scope` parameter", configured_scope_param == "scope")
        check("all requested scopes use Slack's `scope` parameter", query.get("scope") == [",".join(configured_scopes)])
        check("legacy `user_scope` is absent", "user_scope" not in query)
        check("Sign in with Slack scopes are not mixed with API scopes", not ({"openid", "email", "profile"} & set(query.get("scope", [""])[0].split(","))))
        check("OAuth state and PKCE challenge are present", bool(query.get("state")) and bool(query.get("code_challenge")) and query.get("code_challenge_method") == ["S256"])
        check("user token exchange endpoint is configured", auth["token_url"] == "https://slack.com/api/oauth.v2.user.access")
        oauth_mcp._load = lambda: {"test-slack": {"scopes": ",".join(configured_scopes)}}
        check("comma-separated Slack token scopes are parsed", oauth_mcp.granted_scopes("test-slack") == configured_scopes)
        check("a token with the granted Slack scopes is not reported as missing permissions",
              oauth_mcp.scope_report("test-slack")["missing"] == [])
    finally:
        oauth_mcp._conn, mcp_store.connection_secrets = old_conn, old_secrets
        oauth_mcp._load, oauth_mcp._save = old_load, old_save
        oauth_mcp._pending.clear()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
