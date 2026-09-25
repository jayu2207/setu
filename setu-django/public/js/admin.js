/* =========================================================
   ADMIN DASHBOARD LOGIC
   ========================================================= */
const user = requireAuth('admin');

if (user) {
  document.getElementById('sideAvatar').textContent = initials(user.name);
  document.getElementById('sideName').textContent = user.name;
  loadStats();
}

/* ---------- OVERVIEW ---------- */
async function loadStats() {
  try {
    const s = await api.get('/admin/stats');
    document.getElementById('statsGrid').innerHTML = `
      <div class="stat-card"><div class="num">${s.totalStudents}</div><div class="label">Students</div></div>
      <div class="stat-card"><div class="num">${s.totalAlumni}</div><div class="label">Alumni</div></div>
      <div class="stat-card"><div class="num">${s.totalOpportunities}</div><div class="label">Opportunities posted</div></div>
      <div class="stat-card"><div class="num">${s.totalApplications}</div><div class="label">Applications sent</div></div>
      <div class="stat-card"><div class="num">${s.totalMentorships}</div><div class="label">Mentorship requests</div></div>
      <div class="stat-card"><div class="num">${s.totalEvents}</div><div class="label">Events</div></div>
    `;
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- USERS ---------- */
async function loadUsers() {
  const body = document.getElementById('usersBody');
  body.innerHTML = `<tr><td colspan="6" style="color:var(--ink-400);">Loading...</td></tr>`;
  try {
    const users = await api.get('/admin/users');
    if (!users.length) { body.innerHTML = `<tr><td colspan="6">No users found.</td></tr>`; return; }
    body.innerHTML = users.map((u) => `
      <tr>
        <td><strong>${escapeHtml(u.name)}</strong></td>
        <td>${escapeHtml(u.email)}</td>
        <td><span class="badge ${u.role === 'admin' ? 'badge-navy' : u.role === 'alumni' ? 'badge-gold' : 'badge-green'}">${u.role}</span></td>
        <td>${formatDate(u.created_at)}</td>
        <td><span class="badge ${u.status === 'active' ? 'badge-green' : 'badge-red'}">${u.status}</span></td>
        <td>
          ${u.role === 'admin' ? '' : `
            <div style="display:flex; gap:0.4rem;">
              <button class="btn btn-outline btn-sm" onclick="toggleUserStatus(${u.id}, '${u.status}')">${u.status === 'active' ? 'Block' : 'Unblock'}</button>
              <button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})">Delete</button>
            </div>
          `}
        </td>
      </tr>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function toggleUserStatus(id, currentStatus) {
  const next = currentStatus === 'active' ? 'blocked' : 'active';
  try {
    await api.put(`/admin/users/${id}/status`, { status: next });
    toast(`User ${next === 'blocked' ? 'blocked' : 'unblocked'}.`);
    loadUsers();
  } catch (err) { toast(err.message, 'error'); }
}

async function deleteUser(id) {
  if (!confirm('Delete this user permanently? This cannot be undone.')) return;
  try {
    await api.del(`/admin/users/${id}`);
    toast('User deleted.');
    loadUsers();
    loadStats();
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- OPPORTUNITIES ---------- */
async function loadOpps() {
  const wrap = document.getElementById('oppsList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const opps = await api.get('/admin/opportunities');
    if (!opps.length) { wrap.innerHTML = emptyState('No opportunities posted', 'Alumni postings will appear here.'); return; }
    wrap.innerHTML = opps.map((o) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(o.title)} <span class="badge ${o.type === 'job' ? 'badge-navy' : 'badge-gold'}">${o.type}</span></h4>
          <div class="row-meta"><span>${escapeHtml(o.company)}</span><span>· By ${escapeHtml(o.posted_by_name)}</span><span>· ${formatDate(o.created_at)}</span></div>
        </div>
        <div class="row-actions"><button class="btn btn-danger btn-sm" onclick="deleteOpp(${o.id})">Delete</button></div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function deleteOpp(id) {
  if (!confirm('Delete this opportunity?')) return;
  try {
    await api.del(`/opportunities/${id}`);
    toast('Opportunity deleted.');
    loadOpps(); loadStats();
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- MENTORSHIP ---------- */
async function loadMentorship() {
  const wrap = document.getElementById('mentorshipList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const reqs = await api.get('/admin/mentorship');
    if (!reqs.length) { wrap.innerHTML = emptyState('No mentorship activity yet', 'Requests between students and alumni will appear here.'); return; }
    const statusBadge = { pending: 'badge-gold', accepted: 'badge-green', rejected: 'badge-red', completed: 'badge-navy' };
    wrap.innerHTML = reqs.map((r) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(r.field)}</h4>
          <div class="row-meta"><span>${escapeHtml(r.student_name)} → ${escapeHtml(r.alumni_name)}</span><span>· ${formatDate(r.created_at)}</span></div>
        </div>
        <div class="row-actions"><span class="badge ${statusBadge[r.status]}">${r.status}</span></div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- EVENTS ---------- */
async function loadEvents() {
  const wrap = document.getElementById('eventsList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const events = await api.get('/admin/events');
    if (!events.length) { wrap.innerHTML = emptyState('No events yet', 'Events created by alumni or admin will appear here.'); return; }
    wrap.innerHTML = events.map((ev) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(ev.title)}</h4>
          <div class="row-meta"><span>${formatDate(ev.event_date)}</span>${ev.location ? `<span>· ${escapeHtml(ev.location)}</span>` : ''}<span>· By ${escapeHtml(ev.created_by_name)}</span></div>
        </div>
        <div class="row-actions"><button class="btn btn-danger btn-sm" onclick="deleteEvent(${ev.id})">Delete</button></div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function deleteEvent(id) {
  if (!confirm('Delete this event?')) return;
  try {
    await api.del(`/events/${id}`);
    toast('Event deleted.');
    loadEvents(); loadStats();
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- HELPERS ---------- */
function emptyState(title, sub) {
  return `<div class="empty-state">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M8 15a4 4 0 0 0 8 0"/></svg>
    <h3 style="color:var(--ink-700); font-size: var(--fs-md);">${title}</h3>
    <p style="color:var(--ink-400); font-size: var(--fs-sm); margin:0;">${sub}</p>
  </div>`;
}
