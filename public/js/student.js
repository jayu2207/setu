/* =========================================================
   STUDENT DASHBOARD LOGIC
   ========================================================= */
const user = requireAuth('student');

if (user) {
  document.getElementById('sideAvatar').textContent = initials(user.name);
  document.getElementById('sideName').textContent = user.name;
  document.getElementById('welcomeName').textContent = user.name.split(' ')[0];
  loadOverview();
}

/* ---------- OVERVIEW ---------- */
async function loadOverview() {
  try {
    const [opps, apps, mentorships, events] = await Promise.all([
      api.get('/opportunities'),
      api.get('/opportunities/my/applications'),
      api.get('/mentorship/sent'),
      api.get('/events'),
    ]);
    const grid = document.getElementById('overviewStats');
    grid.innerHTML = `
      <div class="stat-card"><div class="num">${opps.length}</div><div class="label">Open opportunities</div></div>
      <div class="stat-card"><div class="num">${apps.length}</div><div class="label">Applications sent</div></div>
      <div class="stat-card"><div class="num">${mentorships.filter(m => m.status === 'accepted').length}</div><div class="label">Active mentors</div></div>
      <div class="stat-card"><div class="num">${events.length}</div><div class="label">Upcoming events</div></div>
    `;
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- OPPORTUNITIES ---------- */
async function loadOpportunities() {
  const wrap = document.getElementById('opportunitiesList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const opps = await api.get('/opportunities');
    if (!opps.length) {
      wrap.innerHTML = emptyState('No opportunities posted yet', 'Check back soon — alumni regularly post new roles.');
      return;
    }
    wrap.innerHTML = opps.map((o) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(o.title)} <span class="badge ${o.type === 'job' ? 'badge-navy' : 'badge-gold'}">${o.type}</span></h4>
          <div class="row-meta">
            <span>${escapeHtml(o.company)}</span>${o.location ? `<span>· ${escapeHtml(o.location)}</span>` : ''}
            <span>· Posted by ${escapeHtml(o.posted_by_name)}</span>
          </div>
          ${o.description ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(o.description)}</p>` : ''}
        </div>
        <div class="row-actions">
          ${o.already_applied
            ? '<span class="badge badge-green">Applied ✓</span>'
            : `<button class="btn btn-brass btn-sm" onclick="applyTo(${o.id}, this)">Apply</button>`}
          ${o.apply_link ? `<a class="btn btn-outline btn-sm" href="${escapeHtml(o.apply_link)}" target="_blank" rel="noopener">Details</a>` : ''}
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

async function applyTo(id, btn) {
  btn.disabled = true; btn.textContent = 'Applying...';
  try {
    await api.post(`/opportunities/${id}/apply`, {});
    toast('Applied successfully!');
    loadOpportunities();
  } catch (err) {
    toast(err.message, 'error');
    btn.disabled = false; btn.textContent = 'Apply';
    if (/resume/i.test(err.message)) {   // no resume yet -> take the student to the upload box
      showSection('profile', document.querySelector(".side-nav a[onclick*=\"'profile'\"]"));
      loadProfile();
    }
  }
}

/* ---------- MY APPLICATIONS ---------- */
async function loadApplications() {
  const wrap = document.getElementById('applicationsList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const apps = await api.get('/opportunities/my/applications');
    if (!apps.length) {
      wrap.innerHTML = emptyState('No applications yet', 'Apply to an opportunity and track its status here.');
      return;
    }
    const statusBadge = { applied: 'badge-navy', shortlisted: 'badge-gold', selected: 'badge-green', rejected: 'badge-red' };
    wrap.innerHTML = apps.map((a) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(a.title)}</h4>
          <div class="row-meta"><span>${escapeHtml(a.company)}</span><span>· Applied ${formatDate(a.applied_at)}</span></div>
        </div>
        <div class="row-actions"><span class="badge ${statusBadge[a.status] || 'badge-navy'}">${a.status}</span></div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- FIND ALUMNI ---------- */
async function loadAlumni() {
  const wrap = document.getElementById('alumniList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const alumni = await api.get('/profile/alumni');
    if (!alumni.length) {
      wrap.innerHTML = emptyState('No alumni have joined yet', 'Invite your seniors to join Setu as alumni.');
      return;
    }
    wrap.innerHTML = alumni.map((a) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(a.name)}</h4>
          <div class="row-meta">
            ${a.position ? `<span>${escapeHtml(a.position)}</span>` : ''}${a.company ? `<span>· ${escapeHtml(a.company)}</span>` : ''}
            ${a.graduation_year ? `<span>· Batch of ${escapeHtml(a.graduation_year)}</span>` : ''}
          </div>
          ${a.skills ? `<div style="margin-top:0.5rem; display:flex; gap:0.35rem; flex-wrap:wrap;">${a.skills.split(',').filter(s=>s.trim()).map(s => `<span class="badge badge-grey">${escapeHtml(s.trim())}</span>`).join('')}</div>` : ''}
          ${a.bio ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(a.bio)}</p>` : ''}
        </div>
        <div class="row-actions">
          <button class="btn btn-brass btn-sm" onclick="openMentorModal(${a.id}, '${escapeHtml(a.name).replace(/'/g, "\\'")}')">Request mentorship</button>
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

function openMentorModal(alumniId, name) {
  document.getElementById('mentorAlumniId').value = alumniId;
  document.getElementById('mentorTargetName').textContent = `To: ${name}`;
  document.getElementById('mentorField').value = '';
  document.getElementById('mentorMessage').value = '';
  document.getElementById('mentorModal').classList.add('open');
}
function closeMentorModal() { document.getElementById('mentorModal').classList.remove('open'); }

document.getElementById('mentorForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await api.post('/mentorship', {
      alumni_id: Number(document.getElementById('mentorAlumniId').value),
      field: document.getElementById('mentorField').value,
      message: document.getElementById('mentorMessage').value,
    });
    toast('Mentorship request sent!');
    closeMentorModal();
  } catch (err) { toast(err.message, 'error'); }
});

/* ---------- MY MENTORSHIP REQUESTS ---------- */
async function loadMentorship() {
  const wrap = document.getElementById('mentorshipList');
  wrap.innerHTML = '<p style="color:var(--ink-400);">Loading...</p>';
  try {
    const reqs = await api.get('/mentorship/sent');
    if (!reqs.length) {
      wrap.innerHTML = emptyState('No mentorship requests yet', 'Find a mentor and send your first request.');
      return;
    }
    const statusBadge = { pending: 'badge-gold', accepted: 'badge-green', rejected: 'badge-red', completed: 'badge-navy' };
    wrap.innerHTML = reqs.map((r) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(r.field)}</h4>
          <div class="row-meta"><span>To ${escapeHtml(r.alumni_name)}</span><span>· Sent ${formatDate(r.created_at)}</span></div>
          ${r.message ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(r.message)}</p>` : ''}
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
    const events = await api.get('/events');
    if (!events.length) {
      wrap.innerHTML = emptyState('No events scheduled', 'Check back later for campus events and activities.');
      return;
    }
    wrap.innerHTML = events.map((ev) => `
      <div class="row-card">
        <div>
          <h4>${escapeHtml(ev.title)}</h4>
          <div class="row-meta"><span>${formatDate(ev.event_date)}</span>${ev.location ? `<span>· ${escapeHtml(ev.location)}</span>` : ''}<span>· By ${escapeHtml(ev.created_by_name)}</span></div>
          ${ev.description ? `<p style="margin-top:0.5rem; color: var(--ink-700); font-size: var(--fs-sm);">${escapeHtml(ev.description)}</p>` : ''}
        </div>
      </div>
    `).join('');
  } catch (err) { toast(err.message, 'error'); }
}

/* ---------- PROFILE ---------- */
async function loadProfile() {
  try {
    const { profile } = await api.get('/profile/me');
    if (profile) {
      document.getElementById('p_branch').value = profile.branch || '';
      document.getElementById('p_year').value = profile.year || '';
      document.getElementById('p_skills').value = profile.skills || '';
      document.getElementById('p_cgpa').value = profile.cgpa || '';
      renderResumeStatus(profile);
      document.getElementById('p_bio').value = profile.bio || '';
    }
  } catch (err) { toast(err.message, 'error'); }
}

document.getElementById('profileForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await api.put('/profile/me', {
      branch: document.getElementById('p_branch').value,
      year: document.getElementById('p_year').value,
      skills: document.getElementById('p_skills').value,
      cgpa: document.getElementById('p_cgpa').value,
      bio: document.getElementById('p_bio').value,
    });
    toast('Profile saved!');
  } catch (err) { toast(err.message, 'error'); }
});

/* ---------- RESUME ---------- */
function renderResumeStatus(profile) {
  const has = !!(profile && profile.resume_name);
  document.getElementById('resumeStatus').innerHTML = has
    ? `Current resume: <strong>${escapeHtml(profile.resume_name)}</strong> <span class="badge badge-green">Uploaded ✓</span>`
    : 'No resume uploaded yet. You must upload one before you can apply.';
  document.getElementById('viewResumeBtn').style.display = has ? '' : 'none';
  document.getElementById('delResumeBtn').style.display = has ? '' : 'none';
}

async function uploadResume() {
  const input = document.getElementById('resumeFile');
  if (!input.files.length) { toast('Please choose a PDF or DOCX file first.', 'error'); return; }
  const fd = new FormData();
  fd.append('resume', input.files[0]);
  try {
    await api.upload('/profile/resume', fd);
    toast('Resume uploaded!');
    input.value = '';
    loadProfile();
  } catch (err) { toast(err.message, 'error'); }
}

async function deleteResume() {
  if (!confirm('Remove your resume? You will not be able to apply until you upload a new one.')) return;
  try { await api.del('/profile/resume'); toast('Resume removed.'); loadProfile(); }
  catch (err) { toast(err.message, 'error'); }
}

/* ---------- HELPERS ---------- */
function emptyState(title, sub) {
  return `<div class="empty-state">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M9 10h.01M15 10h.01M8 15a4 4 0 0 0 8 0"/></svg>
    <h3 style="color:var(--ink-700); font-size: var(--fs-md);">${title}</h3>
    <p style="color:var(--ink-400); font-size: var(--fs-sm); margin:0;">${sub}</p>
  </div>`;
}
