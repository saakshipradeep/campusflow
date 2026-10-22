"""CampusFlow: simulated recruitment coordination portfolio app.
Run: streamlit run app.py
All data is synthetic. Edits persist only for the active Streamlit session.
"""
import io
from datetime import date, datetime, timedelta, time
import random
import pandas as pd
import streamlit as st

st.set_page_config(page_title='CampusFlow | Recruitment Operations', page_icon='📋', layout='wide')

STAGES = ['Applied', 'Screening', 'Assessment', 'Interview Scheduling', 'Interview', 'Hiring Review', 'Offer', 'Hired', 'Rejected', 'Withdrawn']
ACTIVE = STAGES[:7]
ROLES = ['Campus Recruitment Coordinator', 'Client Service Associate', 'Summer Analyst Intern']
RECRUITERS = ['Alex Morgan', 'Jordan Lee', 'Taylor Chen', 'Sam Rivera']
UNIVERSITIES = ['Northeastern University', 'Rutgers University', 'NYU', 'Boston University', 'Cornell University', 'Fordham University', 'Columbia University', 'University of Michigan']
INTERVIEWERS = ['Morgan Ellis', 'Jamie Patel', 'Casey Brooks', 'Drew Wilson']
TODAY = date(2027, 5, 31)  # fixed fictional snapshot so the portfolio is reproducible

st.markdown('''<style>
.block-container{padding-top:1.5rem;max-width:1450px}
[data-testid="stMetric"]{background:#f7fafb;border:1px solid #e2e9ed;padding:16px;border-radius:12px}
h1,h2,h3{letter-spacing:-.025em}
</style>''', unsafe_allow_html=True)


def seed():
    rng = random.Random(20270531)
    first = ['Avery','Riley','Parker','Quinn','Taylor','Jordan','Alex','Morgan','Casey','Sam','Harper','Emerson','Skyler','Rowan','Jamie','Drew','Reese','Cameron','Dakota','Finley']
    last = ['Patel','Chen','Garcia','Johnson','Williams','Kim','Brown','Shah','Nguyen','Lopez','Miller','Singh','Wilson','Lee','Davis','Martin']
    rows = []
    for i in range(1, 101):
        applied = TODAY - timedelta(days=rng.randint(7, 110))
        stage = rng.choices(STAGES, weights=[14,12,10,11,12,9,7,10,11,4])[0]
        stage_date = min(TODAY, applied + timedelta(days=rng.randint(0, min(30, (TODAY-applied).days))))
        rows.append({'id':f'CF-{i:04d}', 'name':f'{rng.choice(first)} {rng.choice(last)}',
                     'university':rng.choice(UNIVERSITIES), 'role':rng.choice(ROLES),
                     'recruiter':rng.choice(RECRUITERS), 'stage':stage,
                     'applied':applied.isoformat(), 'stage_date':stage_date.isoformat(),
                     'email':f'candidate{i:03d}@example.com', 'notes':''})
    return pd.DataFrame(rows)


def initialize():
    if 'candidates' not in st.session_state:
        st.session_state.candidates = seed()
        st.session_state.interviews = pd.DataFrame(columns=['id','candidate_id','interviewer','kind','start','duration','status'])
        st.session_state.tasks = pd.DataFrame(columns=['id','candidate_id','owner','description','due','done'])
        st.session_state.communications = pd.DataFrame(columns=['candidate_id','template','message','logged_at'])
        st.session_state.evaluations = pd.DataFrame(columns=['candidate_id','interviewer','communication','organization','problem_solving','role_fit','recommendation','comments','logged_at'])
        st.session_state.offers = pd.DataFrame(columns=['candidate_id','approval','documents','notified','accepted'])
        st.session_state.history = pd.DataFrame(columns=['candidate_id','old_stage','new_stage','changed_at'])
initialize()


def add_row(key, row):
    st.session_state[key] = pd.concat([st.session_state[key], pd.DataFrame([row])], ignore_index=True)


def candidate_label(cid):
    df = st.session_state.candidates
    match = df.loc[df.id == cid]
    return f'{cid} · {match.iloc[0]["name"]}' if not match.empty else cid


def candidate_picker(label='Candidate', key=None):
    ids = st.session_state.candidates.id.tolist()
    return st.selectbox(label, ids, format_func=candidate_label, key=key)


def filtered_candidates():
    df = st.session_state.candidates.copy()
    with st.sidebar:
        st.subheader('Filters')
        roles = st.multiselect('Position', ROLES)
        recruiters = st.multiselect('Recruiter', RECRUITERS)
        stages = st.multiselect('Stage', STAGES)
        universities = st.multiselect('University', UNIVERSITIES)
        st.caption('Fixed fictional snapshot: May 31, 2027')
        st.caption('All records are simulated. Changes last only for this browser session.')
    if roles: df = df[df.role.isin(roles)]
    if recruiters: df = df[df.recruiter.isin(recruiters)]
    if stages: df = df[df.stage.isin(stages)]
    if universities: df = df[df.university.isin(universities)]
    return df

st.title('CampusFlow')
st.caption('Recruitment Coordination & Candidate Experience · Interactive fictional portfolio case study')
st.info('**Simulation only:** All candidate names, contact details, recruitment activities and outcomes are fictional. No emails or calendar invites are actually sent. Data edits are session-only and reset when the app restarts.')
page = st.sidebar.radio('Workspace', ['Overview','Candidates & Pipeline','Interview Scheduling','Recruiter Tasks','Candidate Communications','Interview Evaluations','Offer Checklist','Activity & Export','Methodology'])
view = filtered_candidates()
all_df = st.session_state.candidates

if page == 'Overview':
    active = view[view.stage.isin(ACTIVE)]
    tasks = st.session_state.tasks
    pending = tasks[(tasks.done != True) & (tasks.candidate_id.isin(view.id))] if not tasks.empty else tasks
    overdue = pending[pd.to_datetime(pending.due).dt.date < TODAY] if not pending.empty else pending
    interviews = st.session_state.interviews
    scheduled = interviews[(interviews.status == 'Scheduled') & (interviews.candidate_id.isin(view.id))] if not interviews.empty else interviews
    a,b,c,d = st.columns(4)
    a.metric('Candidates',len(view)); b.metric('Active pipeline',len(active)); c.metric('Scheduled interviews',len(scheduled)); d.metric('Overdue tasks',len(overdue))
    left,right = st.columns([1.3,1])
    with left:
        st.subheader('Current recruitment pipeline')
        counts = view.stage.value_counts().reindex(STAGES,fill_value=0)
        st.bar_chart(counts)
    with right:
        st.subheader('Recruiter workload')
        st.dataframe(view.groupby('recruiter').size().reindex(RECRUITERS,fill_value=0).rename('Assigned candidates'),use_container_width=True)
        st.subheader('Candidates requiring attention')
        attention = active.copy()
        attention['days_in_stage'] = (pd.Timestamp(TODAY) - pd.to_datetime(attention.stage_date)).dt.days
        st.dataframe(attention[attention.days_in_stage > 10][['id','name','recruiter','stage','days_in_stage']].sort_values('days_in_stage',ascending=False).head(12),hide_index=True,use_container_width=True)
    st.caption('Stage chart is a snapshot of current status, not a historical conversion funnel.')

elif page == 'Candidates & Pipeline':
    st.subheader('Candidate records')
    search = st.text_input('Search by name or candidate ID')
    shown = view[view.name.str.contains(search,case=False,na=False) | view.id.str.contains(search,case=False,na=False)] if search else view
    st.dataframe(shown[['id','name','role','university','recruiter','stage','applied','stage_date']],hide_index=True,use_container_width=True)
    with st.expander('Add fictional candidate'):
        with st.form('new_candidate'):
            name = st.text_input('Candidate name')
            email = st.text_input('Email (use example.com only)')
            university = st.selectbox('University',UNIVERSITIES)
            role = st.selectbox('Position',ROLES)
            recruiter = st.selectbox('Assigned recruiter',RECRUITERS)
            if st.form_submit_button('Add candidate'):
                if not name.strip() or not email.lower().endswith('@example.com'):
                    st.error('Enter a name and a fictional @example.com email address.')
                else:
                    cid = f'CF-{max([int(x.split("-")[1]) for x in all_df.id])+1:04d}'
                    add_row('candidates',{'id':cid,'name':name.strip(),'email':email,'university':university,'role':role,'recruiter':recruiter,'stage':'Applied','applied':TODAY.isoformat(),'stage_date':TODAY.isoformat(),'notes':''})
                    st.success(f'Created {cid}'); st.rerun()
    st.subheader('Update a candidate')
    cid = candidate_picker(key='edit_candidate')
    idx = st.session_state.candidates.index[st.session_state.candidates.id == cid][0]
    record = st.session_state.candidates.loc[idx]
    with st.form('edit_candidate_form'):
        stage = st.selectbox('Recruitment stage',STAGES,index=STAGES.index(record.stage))
        owner = st.selectbox('Recruiter',RECRUITERS,index=RECRUITERS.index(record.recruiter))
        notes = st.text_area('Internal notes',value=str(record.notes))
        if st.form_submit_button('Save changes'):
            if stage != record.stage:
                add_row('history',{'candidate_id':cid,'old_stage':record.stage,'new_stage':stage,'changed_at':datetime.now().isoformat(timespec='seconds')})
                st.session_state.candidates.loc[idx,'stage_date'] = TODAY.isoformat()
            st.session_state.candidates.loc[idx,['stage','recruiter','notes']] = [stage,owner,notes]
            st.success('Candidate updated'); st.rerun()

elif page == 'Interview Scheduling':
    st.subheader('Interview scheduling')
    st.caption('Scheduling is simulated. Conflicts are checked for the same interviewer and overlapping time windows.')
    with st.form('schedule'):
        cid = candidate_picker(key='schedule_candidate')
        interviewer = st.selectbox('Interviewer',INTERVIEWERS)
        kind = st.selectbox('Interview type',['Phone','Video','In-person'])
        col1,col2,col3 = st.columns(3)
        day = col1.date_input('Interview date',value=TODAY+timedelta(days=2))
        clock = col2.time_input('Time (ET)',value=time(10,0))
        duration = col3.selectbox('Duration (minutes)',[30,45,60],index=1)
        if st.form_submit_button('Schedule interview'):
            start = datetime.combine(day,clock)
            existing = st.session_state.interviews
            conflict = False
            for _,r in existing[existing.interviewer == interviewer].iterrows():
                if r.status != 'Scheduled': continue
                other = datetime.fromisoformat(r.start)
                if start < other+timedelta(minutes=int(r.duration)) and other < start+timedelta(minutes=duration): conflict = True
            if conflict: st.error('Scheduling conflict: this interviewer is already booked during that time.')
            else:
                iid = f'INT-{len(existing)+1:04d}'
                add_row('interviews',{'id':iid,'candidate_id':cid,'interviewer':interviewer,'kind':kind,'start':start.isoformat(timespec='minutes'),'duration':duration,'status':'Scheduled'})
                st.success(f'{iid} scheduled (simulation only)')
    df = st.session_state.interviews
    if not df.empty:
        st.dataframe(df,hide_index=True,use_container_width=True)
        with st.form('change_interview'):
            iid = st.selectbox('Manage interview',df.id.tolist())
            status = st.selectbox('Status',['Scheduled','Completed','Cancelled'])
            new_day = st.date_input('New date',value=TODAY+timedelta(days=2),key='new_interview_date')
            new_time = st.time_input('New time (ET)',value=time(10,0),key='new_interview_time')
            if st.form_submit_button('Update interview'):
                row = df[df.id == iid].iloc[0]
                proposed = datetime.combine(new_day,new_time)
                conflict = any(r.id != iid and r.interviewer == row.interviewer and r.status == 'Scheduled' and proposed < datetime.fromisoformat(r.start)+timedelta(minutes=int(r.duration)) and datetime.fromisoformat(r.start) < proposed+timedelta(minutes=int(row.duration)) for _,r in df.iterrows()) if status == 'Scheduled' else False
                if conflict: st.error('Conflict with an existing interview.')
                else:
                    mask = st.session_state.interviews.id == iid
                    st.session_state.interviews.loc[mask,'status'] = status
                    st.session_state.interviews.loc[mask,'start'] = proposed.isoformat(timespec='minutes')
                    st.success('Interview updated'); st.rerun()
    else: st.info('No interviews scheduled yet. Add one above.')

elif page == 'Recruiter Tasks':
    st.subheader('Recruiter task management')
    with st.form('add_task'):
        cid = candidate_picker(key='task_candidate')
        owner = st.selectbox('Task owner',RECRUITERS)
        description = st.text_input('Task description',placeholder='Confirm interview availability')
        due = st.date_input('Due date',value=TODAY+timedelta(days=1))
        if st.form_submit_button('Create task'):
            if description.strip():
                add_row('tasks',{'id':f'TASK-{len(st.session_state.tasks)+1:04d}','candidate_id':cid,'owner':owner,'description':description.strip(),'due':due.isoformat(),'done':False})
                st.success('Task created')
            else: st.error('Add a task description.')
    df = st.session_state.tasks
    if not df.empty:
        edited = st.data_editor(df,disabled=['id','candidate_id','owner','description','due'],column_config={'done':st.column_config.CheckboxColumn('Completed')},hide_index=True,use_container_width=True,key='task_editor')
        if st.button('Save completion changes'):
            st.session_state.tasks['done'] = edited['done'].astype(bool).values
            st.success('Task statuses saved'); st.rerun()
        st.caption('Overdue = incomplete task with due date before the fictional snapshot date.')
    else: st.info('No tasks yet.')

elif page == 'Candidate Communications':
    st.subheader('Candidate communication templates')
    cid = candidate_picker(key='comms_candidate')
    r = all_df[all_df.id == cid].iloc[0]
    templates = {
        'Application acknowledgment':f'Hello {r["name"]},\n\nThank you for applying for the {r["role"]} position. We appreciate your interest and will be in touch about next steps.\n\nBest,\nCampus Recruitment Team',
        'Interview invitation':f'Hello {r["name"]},\n\nWe would like to invite you to an interview for the {r["role"]} position. Please reply with your availability and time zone.\n\nBest,\nCampus Recruitment Team',
        'Interview confirmation':f'Hello {r["name"]},\n\nYour interview for {r["role"]} has been confirmed. Please refer to the agreed date, time zone, and joining instructions.\n\nBest,\nCampus Recruitment Team',
        'Rescheduling notice':f'Hello {r["name"]},\n\nWe need to reschedule your interview for {r["role"]}. We apologize for the inconvenience and will coordinate a suitable alternative.\n\nBest,\nCampus Recruitment Team',
        'Post-interview follow-up':f'Hello {r["name"]},\n\nThank you for taking the time to interview for {r["role"]}. We appreciate your interest and will share an update when available.\n\nBest,\nCampus Recruitment Team',
        'Offer notification (mock)':f'Hello {r["name"]},\n\nWe are pleased to share that you have been selected to proceed to the offer stage for {r["role"]}. This is a simulated template, not a real offer.\n\nBest,\nCampus Recruitment Team',
        'Rejection notification':f'Hello {r["name"]},\n\nThank you for your interest in {r["role"]} and the time you invested. We will not be moving forward with your application at this time.\n\nBest,\nCampus Recruitment Team'
    }
    template = st.selectbox('Message template',list(templates))
    message = st.text_area('Editable draft (copy and paste as needed)',value=templates[template],height=220,key=f'comms_{cid}_{template}')
    if st.button('Log drafted communication'):
        add_row('communications',{'candidate_id':cid,'template':template,'message':message,'logged_at':datetime.now().isoformat(timespec='seconds')})
        st.success('Draft logged. No email was sent.')
    st.caption('Use the text area to copy your message. The app does not send email.')
    log = st.session_state.communications
    if not log.empty: st.dataframe(log[['candidate_id','template','logged_at']],hide_index=True,use_container_width=True)

elif page == 'Interview Evaluations':
    st.subheader('Structured interview evaluation')
    with st.form('evaluation'):
        cid = candidate_picker(key='evaluation_candidate')
        interviewer = st.selectbox('Evaluator',INTERVIEWERS)
        c1,c2 = st.columns(2)
        communication = c1.slider('Communication',1,5,3)
        organization = c2.slider('Organization',1,5,3)
        problem = c1.slider('Problem solving',1,5,3)
        role_fit = c2.slider('Role-specific competencies',1,5,3)
        recommendation = st.selectbox('Recommendation',['Further review','Proceed','Do not proceed'])
        comments = st.text_area('Evidence-based notes (avoid sensitive personal characteristics)')
        if st.form_submit_button('Save evaluation'):
            add_row('evaluations',{'candidate_id':cid,'interviewer':interviewer,'communication':communication,'organization':organization,'problem_solving':problem,'role_fit':role_fit,'recommendation':recommendation,'comments':comments,'logged_at':datetime.now().isoformat(timespec='seconds')})
            st.success('Evaluation recorded')
    if not st.session_state.evaluations.empty: st.dataframe(st.session_state.evaluations,hide_index=True,use_container_width=True)
    st.caption('Scores support consistent review; they do not automatically determine hiring decisions.')

elif page == 'Offer Checklist':
    st.subheader('Simulated offer preparation')
    cid = candidate_picker(key='offer_candidate')
    offers = st.session_state.offers
    existing = offers[offers.candidate_id == cid]
    defaults = existing.iloc[-1] if not existing.empty else None
    with st.form('offer'):
        approval = st.checkbox('Hiring approval recorded',value=bool(defaults.approval) if defaults is not None else False)
        documents = st.checkbox('Mock offer documents reviewed',value=bool(defaults.documents) if defaults is not None else False)
        notified = st.checkbox('Candidate notification prepared',value=bool(defaults.notified) if defaults is not None else False)
        accepted = st.checkbox('Simulated acceptance recorded',value=bool(defaults.accepted) if defaults is not None else False)
        if st.form_submit_button('Save checklist'):
            st.session_state.offers = offers[offers.candidate_id != cid].copy()
            add_row('offers',{'candidate_id':cid,'approval':approval,'documents':documents,'notified':notified,'accepted':accepted})
            st.success('Mock offer checklist saved')
    if not st.session_state.offers.empty: st.dataframe(st.session_state.offers,hide_index=True,use_container_width=True)
    st.caption('This is not a real offer-letter generation or approval system.')

elif page == 'Activity & Export':
    st.subheader('Activity and exports')
    for name,key in [('Candidates','candidates'),('Interview schedules','interviews'),('Recruiter tasks','tasks'),('Communication drafts','communications'),('Evaluations','evaluations'),('Offer checklists','offers'),('Stage changes','history')]:
        df = st.session_state[key]
        with st.expander(f'{name} ({len(df)})'):
            st.dataframe(df,hide_index=True,use_container_width=True)
            st.download_button(f'Download {name} CSV',df.to_csv(index=False).encode('utf-8'),file_name=f'campusflow_{key}.csv',mime='text/csv',key=f'export_{key}')
    if st.button('Reset all data to fictional starting state'):
        for key in ['candidates','interviews','tasks','communications','evaluations','offers','history']:
            del st.session_state[key]
        initialize(); st.rerun()

else:
    st.subheader('Methodology and limitations')
    st.markdown('''**Scenario.** A fictional professional-services company coordinates applications for early-career positions. This demo shows how a recruitment coordinator might manage candidate records, interview schedules, communication drafts, structured evaluations, tasks and offer checklists.

**Candidate lifecycle.** Applied → Screening → Assessment → Interview Scheduling → Interview → Hiring Review → Offer → Hired. Rejected and Withdrawn are terminal stages. Status changes are recorded in a session-level history table.

**Scheduling rules.** Interviews use a simplified Eastern Time (ET) assumption and detect overlapping appointments for the same interviewer. This is not integrated with Google Calendar, Outlook or time-zone conversion APIs.

**Attention flags.** The overview highlights active candidates who have spent more than 10 days in their current stage. Overdue tasks are incomplete tasks with a due date earlier than May 31, 2027. The date is fixed intentionally to make the fictional example reproducible.

**Candidate experience.** Communication templates cover acknowledgments, invitations, confirmations, rescheduling, follow-up and decisions. Logging a draft does not send it. Evaluations are structured to encourage job-relevant, evidence-based notes.

**Privacy and fairness.** Records are entirely fictional, use example.com email addresses, and avoid protected-characteristic data. This demo is not an operational applicant tracking system and must not be used to store real applicant data.

**Data persistence.** Edits are held in Streamlit session state. They do not survive a session reset or app restart, and changes are not shared across visitors. CSV export lets users retain demo output locally.

**Limitations.** No authentication, durable database, external ATS, calendar/email integrations, audit-grade logging, or real hiring decisions. Seed data and all outcomes are simulated. A production implementation would require secure access controls, durable storage, compliance review, and tested integrations.

**Tech stack.** Python, Streamlit, Pandas. No paid APIs or secrets required.''')
