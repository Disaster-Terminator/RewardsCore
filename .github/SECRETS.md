# GitHub Actions Secrets for E2E Tests

The E2E workflows require the following repository secrets (Settings > Secrets and variables > Actions).

## Required Secrets

| Secret Name | Description | Format |
|-------------|-------------|--------|
| `MS_REWARDS_E2E_EMAIL` | Test Microsoft account email | `user@outlook.com` |
| `MS_REWARDS_E2E_PASSWORD` | Test account password | Plain text (no special escaping) |
| `MS_REWARDS_E2E_TOTP_SECRET` | Optional: 2FA TOTP base32 secret | `JBSWY3DPEHPK3PXP` (from Microsoft Authenticator) |

## Setting Up Secrets

1. Go to repository Settings
2. Navigate to **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with Name and Value
5. Save

## Security Notes

- **Never** commit `.env.test` or `storage_state.json` to repository
- Use dedicated test accounts, not personal main accounts
- Rotate credentials if accidentally exposed
- Consider using GitHub Environments for staging/prod separation

## CI Variables (Optional)

Also define repository variables (Settings → Actions → Variables):

| Variable | Description | Default |
|----------|-------------|---------|
| `E2E_HEADLESS` | Run browser headless? | `true` |
| `E2E_STORAGE_STATE_GENERATE` | Generate storage_state on first run? | `true` |
| `E2E_SLACK_WEBHOOK` | Optional: Notification webhook URL | (empty) |

## Testing CI Configuration

After setting secrets, manually trigger workflow:

1. Go to repository **Actions** tab
2. Select "E2E Smoke Tests" or "E2E Full Tests"
3. Click **Run workflow** → **Run workflow**
4. Monitor logs for failures

## Troubleshooting

- **Secret not found**: Verify secret name matches exactly (case-sensitive)
- **Permission denied**: Secrets are encrypted; ensure repository has write access
- **Browser install fails**: Check `playwright install-deps` step has sudo privileges
