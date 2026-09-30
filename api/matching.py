"""Resume <-> job requirement matching (no external AI needed, pure keyword logic)."""
import re
import zipfile
from io import BytesIO


def split_list(value):
    return [x.strip().lower() for x in re.split(r'[,\n;|]+', value or '') if x.strip()]


def _contains(skill, text):
    # word-boundary match that also works for c++, c#, node.js
    return re.search(r'(?<![a-z0-9+#])' + re.escape(skill) + r'(?![a-z0-9+#])', text) is not None


def extract_resume_text(data, ext):
    """Best-effort text extraction. Never raises - matching just falls back to profile skills."""
    try:
        if ext == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(data))
            return '\n'.join((page.extract_text() or '') for page in reader.pages)[:50000]
        if ext == '.docx':
            with zipfile.ZipFile(BytesIO(data)) as z:
                xml = z.read('word/document.xml').decode('utf-8', 'ignore')
            xml = re.sub(r'</w:p>', '\n', xml)
            return re.sub(r'<[^>]+>', '', xml)[:50000]
    except Exception:
        pass
    return ''


def match_student(opp, profile):
    """Return how well a student's profile + resume fits an opportunity's requirements."""
    required = split_list(opp.required_skills)
    text = ((profile.skills or '') + '\n' + (profile.resume_text or '')).lower()

    matched = [s for s in required if _contains(s, text)]
    missing = [s for s in required if s not in matched]
    score = round(len(matched) * 100 / len(required)) if required else 100

    branches = split_list(opp.required_branch)
    branch_ok = (not branches) or any(b in (profile.branch or '').lower() for b in branches)

    cgpa_ok = True
    if opp.min_cgpa is not None:
        cgpa_ok = profile.cgpa is not None and profile.cgpa >= opp.min_cgpa

    return {
        'match_percent': score, 'matched_skills': matched, 'missing_skills': missing,
        'branch_ok': branch_ok, 'cgpa_ok': cgpa_ok, 'eligible': branch_ok and cgpa_ok,
    }
