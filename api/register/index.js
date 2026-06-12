const https = require('https');
const { EmailClient } = require('@azure/communication-email');

// ── Graph API helpers ─────────────────────────────────────────────────────────

function httpsPost(hostname, path, headers, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = typeof body === 'string' ? body : JSON.stringify(body);
    const req = https.request(
      { hostname, path, method: 'POST', headers: { ...headers, 'Content-Length': Buffer.byteLength(bodyStr) } },
      res => {
        let data = '';
        res.on('data', c => (data += c));
        res.on('end', () => resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }));
      }
    );
    req.on('error', reject);
    req.write(bodyStr);
    req.end();
  });
}

function httpsGet(hostname, path, headers) {
  return new Promise((resolve, reject) => {
    const req = https.request({ hostname, path, method: 'GET', headers }, res => {
      let data = '';
      res.on('data', c => (data += c));
      res.on('end', () => resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }));
    });
    req.on('error', reject);
    req.end();
  });
}

async function getGraphToken(tenantId, clientId, clientSecret) {
  const body = new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: clientId,
    client_secret: clientSecret,
    scope: 'https://graph.microsoft.com/.default',
  }).toString();

  const result = await httpsPost(
    'login.microsoftonline.com',
    `/${tenantId}/oauth2/v2.0/token`,
    { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  );

  if (!result.body?.access_token) {
    throw new Error(result.body?.error_description || 'Failed to get Graph token');
  }
  return result.body.access_token;
}

function graphPost(token, path, body) {
  return httpsPost('graph.microsoft.com', `/v1.0${path}`, {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }, body);
}

function graphGet(token, path) {
  return httpsGet('graph.microsoft.com', `/v1.0${path}`, {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function generateTempPassword() {
  const upper   = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
  const lower   = 'abcdefghjkmnpqrstuvwxyz';
  const digits  = '23456789';
  const special = '@#$!';
  const pick    = s => s[Math.floor(Math.random() * s.length)];

  const chars = [
    pick(upper), pick(upper),
    pick(lower), pick(lower), pick(lower),
    pick(digits), pick(digits),
    pick(special),
  ];
  // Fisher-Yates shuffle
  for (let i = chars.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [chars[i], chars[j]] = [chars[j], chars[i]];
  }
  return chars.join('');
}

function toNickname(first, last) {
  const clean = s => s.toLowerCase().replace(/[^a-z0-9]/g, '').substring(0, 20);
  return `${clean(first)}.${clean(last)}`;
}

// ── Main handler ──────────────────────────────────────────────────────────────

module.exports = async function (context, req) {
  context.res = { headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } };

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    context.res.status = 204;
    context.res.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS';
    context.res.headers['Access-Control-Allow-Headers'] = 'Content-Type';
    return;
  }

  if (req.method !== 'POST') {
    context.res.status = 405;
    context.res.body = { error: 'Method not allowed' };
    return;
  }

  const { firstName, lastName, email, jobTitle } = req.body || {};

  if (!firstName?.trim() || !lastName?.trim() || !email?.trim()) {
    context.res.status = 400;
    context.res.body = { error: 'First name, last name, and email are required.' };
    return;
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    context.res.status = 400;
    context.res.body = { error: 'Please enter a valid email address.' };
    return;
  }

  const tenantId     = process.env.GRAPH_TENANT_ID;
  const clientId     = process.env.GRAPH_CLIENT_ID;
  const clientSecret = process.env.GRAPH_CLIENT_SECRET;
  const groupId      = process.env.LEARNERS_GROUP_ID;
  const acsConnStr   = process.env.ACS_CONNECTION_STRING;
  const acsSender    = process.env.ACS_SENDER_ADDRESS;
  const domain       = process.env.TENANT_DOMAIN || 'bdcloudacademy.com';
  const siteUrl      = (process.env.SITE_URL || 'https://training-hub.azurestaticapps.net').replace(/\/$/, '');

  if (!tenantId || !clientId || !clientSecret || !groupId || !acsConnStr || !acsSender) {
    context.log.error('Missing required environment variables for /api/register');
    context.res.status = 500;
    context.res.body = { error: 'Server configuration error. Contact the administrator.' };
    return;
  }

  try {
    const token = await getGraphToken(tenantId, clientId, clientSecret);

    // Find a unique UPN
    const baseNickname = toNickname(firstName.trim(), lastName.trim());
    let nickname = baseNickname;
    let upn = `${nickname}@${domain}`;

    for (let attempt = 1; attempt <= 5; attempt++) {
      const check = await graphGet(token, `/users/${encodeURIComponent(upn)}?$select=id`);
      if (check.status === 404) break; // available
      nickname = `${baseNickname}${attempt + 1}`;
      upn = `${nickname}@${domain}`;
    }

    const tempPassword = generateTempPassword();

    // Create the member user
    const createResult = await graphPost(token, '/users', {
      accountEnabled: true,
      displayName: `${firstName.trim()} ${lastName.trim()}`,
      givenName: firstName.trim(),
      surname: lastName.trim(),
      mailNickname: nickname,
      userPrincipalName: upn,
      ...(jobTitle?.trim() ? { jobTitle: jobTitle.trim() } : {}),
      passwordProfile: {
        forceChangePasswordNextSignIn: true,
        password: tempPassword,
      },
    });

    if (createResult.status !== 201) {
      const msg = createResult.body?.error?.message || 'Failed to create account.';
      // Surface duplicate display name or UPN conflicts clearly
      if (msg.includes('already exists') || msg.includes('already in use')) {
        context.res.status = 409;
        context.res.body = { error: 'An account with those details already exists. Try signing in instead.' };
      } else {
        context.res.status = 422;
        context.res.body = { error: msg };
      }
      return;
    }

    const userId = createResult.body.id;

    // Add to sg-training-hub-learners security group
    const groupResult = await graphPost(token, `/groups/${groupId}/members/$ref`, {
      '@odata.id': `https://graph.microsoft.com/v1.0/directoryObjects/${userId}`,
    });

    // 204 = added, 400 "already exists" = already a member — both are fine
    if (groupResult.status !== 204 && groupResult.status !== 400) {
      context.log.warn(`Group add returned ${groupResult.status} for user ${userId}`);
    }

    // Send welcome email via ACS
    const emailClient = new EmailClient(acsConnStr);
    const poller = await emailClient.beginSend({
      senderAddress: acsSender,
      recipients: {
        to: [{ address: email.trim(), displayName: `${firstName.trim()} ${lastName.trim()}` }],
      },
      content: {
        subject: 'Welcome to BD Cloud Academy — Your Login Credentials',
        plainText: [
          `Hi ${firstName.trim()},`,
          '',
          'Your BD Cloud Academy account has been created.',
          '',
          `Login URL : ${siteUrl}/login.html`,
          `Username  : ${upn}`,
          `Password  : ${tempPassword}`,
          '',
          'You will be prompted to set a new password on first sign-in.',
          '',
          '— BD Cloud Academy Team',
        ].join('\n'),
        html: buildEmailHtml(firstName.trim(), upn, tempPassword, siteUrl, email.trim()),
      },
    });
    await poller.pollUntilDone();

    context.res.status = 200;
    context.res.body = {
      success: true,
      message: `Account created! Check ${email.trim()} for your login credentials.`,
    };

  } catch (err) {
    context.log.error('register error:', err.message || err);
    context.res.status = 500;
    context.res.body = { error: 'An unexpected error occurred. Please try again shortly.' };
  }
};

// ── Email template ────────────────────────────────────────────────────────────

function buildEmailHtml(firstName, upn, password, siteUrl, recipientEmail) {
  return `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif">
  <div style="max-width:520px;margin:40px auto;padding:0 16px">

    <div style="background:#fff;border-radius:16px;padding:40px;border:1px solid #e2e8f0">

      <!-- Header -->
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:32px">
        <div style="width:38px;height:38px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:15px;text-align:center;line-height:38px">TH</div>
        <span style="font-size:18px;font-weight:700;color:#0f172a">BD Cloud Academy</span>
      </div>

      <!-- Greeting -->
      <h1 style="font-size:22px;font-weight:700;color:#0f172a;margin:0 0 6px">Welcome, ${firstName}!</h1>
      <p style="font-size:15px;color:#64748b;margin:0 0 28px;line-height:1.6">
        Your BD Cloud Academy account is ready. Use the credentials below to sign in and start learning.
      </p>

      <!-- Credentials box -->
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:24px;margin-bottom:24px">
        <p style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#94a3b8;margin:0 0 14px">Your Login Credentials</p>
        <table style="width:100%;border-collapse:collapse;font-size:14px">
          <tr>
            <td style="padding:8px 0;color:#64748b;width:90px;vertical-align:top">Login URL</td>
            <td style="padding:8px 0"><a href="${siteUrl}/login.html" style="color:#2563eb;text-decoration:none;font-weight:500">${siteUrl}/login.html</a></td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#64748b;vertical-align:top">Username</td>
            <td style="padding:8px 0;font-family:'Courier New',monospace;font-weight:600;color:#0f172a;background:#fff;border-radius:6px;word-break:break-all">${upn}</td>
          </tr>
          <tr>
            <td style="padding:8px 0;color:#64748b;vertical-align:top">Password</td>
            <td style="padding:8px 0;font-family:'Courier New',monospace;font-weight:700;color:#1d4ed8;font-size:16px;letter-spacing:0.05em">${password}</td>
          </tr>
        </table>
      </div>

      <!-- Warning -->
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin-bottom:28px;font-size:13px;color:#92400e;line-height:1.5">
        <strong>Important:</strong> You will be prompted to set a new password on your first sign-in. Keep this email until then.
      </div>

      <!-- CTA -->
      <a href="${siteUrl}/login.html"
         style="display:inline-block;background:#1d4ed8;color:#fff;text-decoration:none;font-weight:600;font-size:15px;padding:14px 32px;border-radius:10px;letter-spacing:0.01em">
        Sign in to BD Cloud Academy →
      </a>

    </div>

    <!-- Footer -->
    <p style="text-align:center;font-size:12px;color:#94a3b8;margin-top:24px;line-height:1.6">
      This email was sent to ${recipientEmail} because you created an account at BD Cloud Academy.<br>
      Questions? Reply to this email.
    </p>

  </div>
</body>
</html>`;
}
