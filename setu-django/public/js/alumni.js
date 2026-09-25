/* =========================================================
   ALUMNI DASHBOARD LOGIC
   ========================================================= */
const user = requireAuth('alumni');

if (user) {
  document.getElementById('sideAvatar').textContent = initials(user.name);
  document.getElementById('sideName').textContent = user.name;
  document.getElementById('welcomeName').textContent = user.name.split(' ')[0];
  loadOverview();
}

/* ---------- OVERVIEW ---------- */
async function loadOverview() {
  try {
    const [mine, mentorship, events] = await Promise.all([
      api.get('/opportunities/mine'),
      api.get('/mentorship/received'),
      api.get('/events'),
    ]);
    const totalApplicants = mine.reduce((sum, o) => sum + o.applicants.length, 0);
    const pendingMentorship = mentorship.filter((m) => m.status === 'pending').length;
    const grid = document.getElementById('overviewStats');
    grid.innerHTML = `
      <div class="stat-card"><div class="num">${mine.length}</div><div class="label">Opportunities posted</div></div>
      <div class="stat-card"><div class="num">${totalApplicants}</div><div class="label">Total applicants</div></div>
      <div class="stat-card"><div class="num">${pendingMentorship}</div><div class="label">Pending mentorship requests</div></div>
      <div class="stat-card"><div class="num">${events.length}</div><div class="label">Upcoming events</div></div>
    `;
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- POST OPPORTUNITY ---------- */
document.getElementById('oppForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await api.post('/opportunities', {
      title: document.getElementById('o_title').value,
      type: document.getElementById('o_type').value,
      company: document.getElementById('o_company').value,
      location: document.getElementById('o_location').value,
      description: document.getElementById('o_description').value,
      apply_link: document.getElementById('o_link').value,
    });
    toast('Opportunity posted!');
    document.getElementById('oppForm').reset();
    showSection('myOpps', document.querySelectorAll('.side-nav a')[2]);
    loadMyOpportunities();
  } catch (err) { toast(err.message, 'error'); }
});

/* ---------- MY POSTINGS ---------- */
async function loadMyOpportunities() {
  const wrap = document.getElementById('myOppsList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const opps = await api.get('/opportunities/mine');
    if (!opps.length) {
      wrap.innerHTML = emptyState('No postings yet', 'Post your first job or internship opportunity for students.');
      return;
    }
    const statusBadge = { applied: 'badge-navy', shortlisted: 'badge-gold', selected: 'badge-green', rejected: 'badge-red' };
    wrap.innerHTML = opps.map((o) => `
      <div class="row-card" style="flex-direction:column; align-items:stretch;">
        <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.6rem;">
          <div>
            <h4>${escapeHtml(o.title)} <span class="badge ${o.type === 'job' ? 'badge-navy' : 'badge-gold'}">${o.type}</span></h4>
            <div class="row-meta"><span>${escapeHtml(o.company)}</span>${o.location ? `<span>· ${escapeHtml(o.location)}</span>` : ''}<span>· Posted ${formatDate(o.created_at)}</span></div>
          </div>
          <div class="row-actions">
            <button class="btn btn-danger btn-sm" onclick="deleteOpp(${o.id})">Delete</button>
          </div>
        </div>
        <div style="margin-top:0.8rem; border-top:1px solid var(--paper-line); padding-top:0.8rem;">
          <strong style="font-size:var(--fs-xs); color:var(--ink-600);">APPLICANTS (${o.applicants.length})</strong>
          ${o.applicants.length === 0 ? '<p style="color:var(--ink-400); font-size:var(--fs-sm); margin-top:0.3rem;">No applicants yet.</p>' : `
          <div style="margin-top:0.5rem; display:flex; flex-direction:column; gap:0.5rem;">
            ${o.applicants.map((a) => `
              <div style="display:flex; justify-content:space-between; align-items:center; background:var(--paper-50); border-radius:var(--radius-sm); padding:0.5rem 0.8rem; flex-wrap:wrap; gap:0.5rem;">
                <div style="font-size:var(--fs-sm);"><strong>${escapeHtml(a.name)}</strong> · ${escapeHtml(a.email)}</div>
                <select class="input" style="width:auto; padding:0.3rem 0.6rem; font-size:var(--fs-xs);" onchange="updateAppStatus(${a.application_id}, this.value)">
                  <option value="applied" ${a.status==='applied'?'selected':''}>Applied</option>
                  <option value="shortlisted" ${a.status==='shortlisted'?'selected':''}>Shortlisted</option>
                  <option value="selected" ${a.status==='selected'?'selected':''}>Selected</option>
                  <option value="rejected" ${a.status==='rejected'?'selected':''}>Rejected</option>
                </select>
              </div>
            `).join('')}
          </div>`}
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function deleteOpp(id) {
  if (!confirm('Delete this opportunity? This cannot be undone.')) return;
  try {
    await api.del(`/opportunities/${id}`);
    toast('Opportunity deleted.');
    loadMyOpportunities();
  } catch (err) { toast(err.message, 'error'); }
}

async function updateAppStatus(appId, status) {
  try {
    await api.put(`/opportunities/applications/${appId}/status`, { status });
    toast('Applicant status updated.');
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- MENTORSHIP RECEIVED ---------- */
async function loadMentorshipReceived() {
  const wrap = document.getElementById('mentorshipList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const reqs = await api.get('/mentorship/received');
    if (!reqs.length) {
      wrap.innerHTML = emptyState('No mentorship requests yet', 'Students will be able to request your guidance once you complete your profile.');
      return;
    }
    wrap.innerHTML = reqs.map((r) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(r.field)}</h4>
          <div class="row-meta"><span>From ${escapeHtml(r.student_name)}</span><span>· ${escapeHtml(r.student_email)}</span><span>· ${formatDate(r.created_at)}</span></div>
          ${r.message ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(r.message)}</p>` : ''}
        </div>
        <div class="row-actions">
          ${r.status === 'pending' ? `
            <button class="btn btn-brass btn-sm" onclick="respondMentor(${r.id}, 'accepted')">Accept</button>
            <button class="btn btn-outline btn-sm" onclick="respondMentor(${r.id}, 'rejected')">Decline</button>
          ` : `<span class="badge ${r.status === 'accepted' ? 'badge-green' : r.status === 'rejected' ? 'badge-red' : 'badge-navy'}">${r.status}</span>`}
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function respondMentor(id, status) {
  try {
    await api.put(`/mentorship/${id}/status`, { status });
    toast(status === 'accepted' ? 'Request accepted!' : 'Request declined.');
    loadMentorshipReceived();
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- EVENTS ---------- */
async function loadEvents() {
  const wrap = document.getElementById('eventsList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const events = await api.get('/events');
    if (!events.length) {
      wrap.innerHTML = emptyState('No events yet', 'Add a campus event so students can see it.');
      return;
    }
    wrap.innerHTML = events.map((ev) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(ev.title)}</h4>
          <div class="row-meta"><span>${formatDate(ev.event_date)}</span>${ev.location ? `<span>· ${escapeHtml(ev.location)}</span>` : ''}<span>· By ${escapeHtml(ev.created_by_name)}</span></div>
          ${ev.description ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(ev.description)}</p>` : ''}
        </div>
        <div class="row-actions">
          ${ev.created_by === user.id ? `<button class="btn btn-danger btn-sm" onclick="deleteEvent(${ev.id})">Delete</button>` : ''}
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}
function openEventModal() { document.getElementById('eventModal').classList.add('open'); }
function closeEventModal() { document.getElementById('eventModal').classList.remove('open'); document.getElementById('eventForm').reset(); }

document.getElementById('eventForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await api.post('/events', {
      title: document.getElementById('e_title').value,
      event_date: document.getElementById('e_date').value,
      location: document.getElementById('e_location').value,
      description: document.getElementById('e_description').value,
    });
    toast('Event added!');
    closeEventModal();
    loadEvents();
  } catch (err) { toast(err.message, 'error'); }
});

async function deleteEvent(id) {
  if (!confirm('Delete this event?')) return;
  try {
    await api.del(`/events/${id}`);
    toast('Event deleted.');
    loadEvents();
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- PROFILE ---------- */
async function loadProfile() {
  try {
    const { profile } = await api.get('/profile/me');
    if (profile) {
      document.getElementById('p_company').value = profile.company || '';
      document.getElementById('p_position').value = profile.position || '';
      document.getElementById('p_branch').value = profile.branch || '';
      document.getElementById('p_gradyear').value = profile.graduation_year || '';
      document.getElementById('p_experience').value = profile.experience || '';
      document.getElementById('p_skills').value = profile.skills || '';
      document.getElementById('p_bio').value = profile.bio || '';
    }
  } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await api.put('/profile/me', {
      company: document.getElementById('p_company').value,
      position: document.getElementById('p_position').value,
      branch: document.getElementById('p_branch').value,
      graduation_year: document.getElementById('p_gradyear').value,
      experience: document.getElementById('p_experience').value,
      skills: document.getElementById('p_skills').value,
      bio: document.getElementById('p_bio').value,
    });
    toast('Profile saved!');
  } catch (err) { toast(err.message, 'error'); }
});

/* ---------- HELPERS ---------- */
function emptyState(title, sub) {
  return `<div class="empty-state">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M8 15a4 4 0 0 0 8 0"/></svg>
    <h3 style="color:var(--ink-700); font-size: var(--fs-md);">${title}</h3>
    <p style="color:var(--ink-400); font-size: var(--fs-sm); margin:0;">${sub}</p>
  </div>`;
}
