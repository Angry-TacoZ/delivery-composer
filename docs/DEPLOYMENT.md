# Deterministic demo deployment

## Declared scope

Public low-risk demonstration using synthetic data only. The hosted demo does not initialize PostgreSQL or Gemini and must not receive real client, consultant, employee, or candidate data.

## Target architecture

- Firebase project: `composermvp-4d5c0`
- Firebase Hosting URL: `https://composermvp-4d5c0.web.app`
- Custom domain after verification: `https://composer.jamesai.space`
- Cloud Run service: `delivery-composer-api`
- Region: `us-east1`
- Runtime mode: `DEMO_MODE=true`
- Runtime identity: dedicated `delivery-composer-runtime` service account with no project roles
- Capacity: zero minimum instances, one maximum instance, 1 CPU, 512 MiB memory, 20 concurrent requests

Firebase Hosting serves `web/dist`, routes `/api/**` to Cloud Run, and routes remaining paths to the React application. Cloud Run retains reviews only in one process's memory; a restart or scale-to-zero event clears them.

## Preconditions

1. PR containing the deployment state is reviewed, merged, and passing on `main`.
2. Blaze billing is active for `composermvp-4d5c0`.
3. A low Cloud Billing budget alert is configured and verified. An alert is not a hard spending cap.
4. Google Cloud CLI and Firebase CLI access are authenticated to James's account.
5. Local `main` is clean and exactly matches `origin/main`.

## Authentication checks

```powershell
gcloud auth list
gcloud projects describe composermvp-4d5c0
npx firebase-tools@latest login:list
npx firebase-tools@latest projects:list
```

Both tools must show access to project `composermvp-4d5c0`. Do not continue if either tool selects another project.

## Deploy in dependency order

The deployment script verifies source state, runs the canonical verifier and secret scan, creates a no-role runtime service account if required, deploys Cloud Run, verifies its deterministic health contract, deploys Firebase Hosting, and verifies the Hosting-to-Cloud-Run rewrite.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\deploy-demo.ps1 -BudgetAlertConfirmed
```

The script must report all of the following before the deployment is accepted:

- Cloud Run health status is `ok`.
- Execution mode is `deterministic_demo`.
- `demo_mode` is `true`.
- Database and Gemini configuration are both `false`.
- Firebase Hosting returns the application shell.
- `https://composermvp-4d5c0.web.app/api/health` reaches Cloud Run.

## Custom domain

After the default Hosting URL passes:

1. Open Firebase Console > Hosting > Add custom domain.
2. Enter `composer.jamesai.space`.
3. Add only the DNS records Firebase provides to the current DNS provider.
4. Wait for Firebase to verify ownership and provision HTTPS.
5. Verify the application and `/api/health` through the custom domain.

Do not guess DNS values or remove unrelated `jamesai.space` records.

## Rollback

1. In Firebase Hosting release history, roll back to the previous verified release.
2. In Cloud Run revision history, route 100% traffic to the previous verified revision.
3. Re-run the application-shell and `/api/health` smoke tests.
4. If costs or abuse are suspected, set Cloud Run maximum instances to zero or remove public invocation while investigating.

## Known limitations

- Session state can disappear when Cloud Run restarts or scales to zero.
- Rate limiting is process-local and not a substitute for authenticated multi-user abuse controls.
- The PDF endpoint is bounded but is not a production document-security pipeline.
- PostgreSQL migrations, pgvector retrieval, and Gemini calls remain unverified and disabled.
