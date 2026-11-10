/* =============================================================================
   MOCK DATA — frontend-only demo seed.
   Everything here is replaced by real API responses once a backend exists.
   Shapes are intentionally close to what a REST/GraphQL API would return.
   ============================================================================= */

export const DEMO_USER = {
  id: 'u_demo',
  name: 'Arjun Mehta',
  initials: 'AM',
  plan: 'Pro Trial',
  memberSince: 'Sep 2026',
};

export const SEED_GOALS = [
  {
    id: 'g1',
    title: 'Become placement-ready',
    description: 'Crack technical interviews at product companies before campus placements open.',
    targetDate: '2026-12-20',
    priority: 'high',
    commitments: ['Solve 2 DSA problems', 'Study core CS subjects for 1 hour', 'Spend 30 minutes on interview preparation'],
    createdAt: '2026-09-14',
  },
  {
    id: 'g2',
    title: 'Ship my capstone project',
    description: 'Finish the MVP, deploy it, and write the project report.',
    targetDate: '2027-01-15',
    priority: 'medium',
    commitments: ['Write code for 90 minutes', 'Log one finished feature'],
    createdAt: '2026-10-01',
  },
  {
    id: 'g3',
    title: 'Get consistent at the gym',
    description: 'Train four days a week without negotiating with myself.',
    targetDate: '2027-02-01',
    priority: 'low',
    commitments: ['Complete the scheduled workout'],
    createdAt: '2026-10-08',
  },
];

export const SEED_TASKS = [
  { id: 't1', goalId: 'g1', title: 'Solve 2 DSA problems', description: 'One medium array problem and one medium graph problem. No peeking at the editorial for 30 minutes.', time: '07:00', priority: 'high', status: 'done', completedAt: '07:52' },
  { id: 't2', goalId: 'g1', title: 'Study OS: process scheduling', description: 'Read the chapter and write 5 short notes on scheduling algorithms. 60 minutes, phone out of the room.', time: '10:00', priority: 'high', status: 'done', completedAt: '11:05' },
  { id: 't3', goalId: 'g2', title: 'Build the auth flow for the capstone', description: 'Login, signup, and a protected route. Commit before lunch.', time: '12:30', priority: 'medium', status: 'pending' },
  { id: 't4', goalId: 'g1', title: 'Mock interview prep: 30 minutes', description: 'Answer two behavioural questions out loud and record yourself.', time: '16:00', priority: 'medium', status: 'pending' },
  { id: 't5', goalId: 'g3', title: 'Leg day workout', description: '45 minutes. The only acceptable reason to skip is illness.', time: '18:30', priority: 'low', status: 'pending' },
  { id: 't6', goalId: 'g1', title: 'Revise one CS fundamental', description: 'DBMS: normalisation. Explain it aloud without notes.', time: '21:00', priority: 'medium', status: 'pending' },
];

export const SEED_ACTIVITY = [
  { id: 'a1', type: 'done', text: 'Completed "Study OS: process scheduling"', time: '11:05 AM' },
  { id: 'a2', type: 'done', text: 'Completed "Solve 2 DSA problems"', time: '07:52 AM' },
  { id: 'a3', type: 'missed', text: 'Missed "Leg day workout" yesterday', time: 'Yesterday' },
  { id: 'a4', type: 'confront', text: 'Brutality AI flagged a repeated excuse: "no time"', time: 'Yesterday' },
  { id: 'a5', type: 'plan', text: 'Planner Agent moved 1 task to the morning slot', time: '2 days ago' },
];

/** Last seven days. `committed`/`completed` for today is derived from live tasks. */
export const WEEKLY_PERFORMANCE = [
  { day: 'Mon', committed: 4, completed: 4 },
  { day: 'Tue', committed: 4, completed: 4 },
  { day: 'Wed', committed: 3, completed: 3 },
  { day: 'Thu', committed: 4, completed: 2 },
  { day: 'Fri', committed: 3, completed: 1 },
  { day: 'Sat', committed: 3, completed: 0 },
];

export const BASE_STATS = { streak: 4, completedBefore: 14, missedBefore: 7 };

export const SEED_REPORTS = [
  {
    id: 'r4', week: 'Nov 3 – Nov 9', label: 'Week 6', score: 67, committed: 21, completed: 14, missed: 7,
    best: { day: 'Tuesday', pct: 100 }, worst: { day: 'Saturday', pct: 0 },
    daily: [
      { day: 'Mon', pct: 100 }, { day: 'Tue', pct: 100 }, { day: 'Wed', pct: 100 }, { day: 'Thu', pct: 50 }, { day: 'Fri', pct: 33 }, { day: 'Sat', pct: 0 }, { day: 'Sun', pct: 0 },
    ],
    excuses: [{ label: 'No time', count: 5 }, { label: 'Too tired', count: 3 }, { label: 'Will do tomorrow', count: 2 }, { label: 'Not in the mood', count: 1 }],
    missedList: ['Leg day workout (Sat)', 'Mock interview prep (Fri)', 'DBMS revision (Fri)', 'Capstone: auth flow (Thu)', 'Solve 2 DSA problems (Sat)', 'CS fundamentals (Sat)', 'Leg day workout (Thu)'],
    analysis: 'You committed to 21 tasks this week and completed 14. Your performance dropped during the last three days. Your recurring excuse was lack of time. Next week, your priority is consistency, not increasing workload.',
    actions: ['Move DSA practice to 7:00 AM, before the day can interfere.', 'Cut the daily plan to 3 tasks until you hit 5 consecutive perfect days.', 'Block Saturday morning for the workout. No renegotiation.', 'Check in before 9 PM every night, including bad days.'],
  },
  {
    id: 'r3', week: 'Oct 27 – Nov 2', label: 'Week 5', score: 78, committed: 20, completed: 16, missed: 4,
    best: { day: 'Monday', pct: 100 }, worst: { day: 'Sunday', pct: 25 },
    daily: [
      { day: 'Mon', pct: 100 }, { day: 'Tue', pct: 75 }, { day: 'Wed', pct: 100 }, { day: 'Thu', pct: 75 }, { day: 'Fri', pct: 75 }, { day: 'Sat', pct: 50 }, { day: 'Sun', pct: 25 },
    ],
    excuses: [{ label: 'Too tired', count: 2 }, { label: 'No time', count: 2 }],
    missedList: ['Gym (Sat)', 'Gym (Sun)', 'Mock interview prep (Fri)', 'DBMS revision (Tue)'],
    analysis: 'You completed 16 of 20 commitments, your best week so far. The weekend remains your weak point. Weekday execution was solid; protect it and fix Sunday.',
    actions: ['Set a fixed Sunday check-in.', 'Pre-pack gym clothes on Saturday night.', 'Keep the weekday plan unchanged.'],
  },
  {
    id: 'r2', week: 'Oct 20 – Oct 26', label: 'Week 4', score: 52, committed: 21, completed: 11, missed: 10,
    best: { day: 'Tuesday', pct: 75 }, worst: { day: 'Friday', pct: 0 },
    daily: [
      { day: 'Mon', pct: 67 }, { day: 'Tue', pct: 75 }, { day: 'Wed', pct: 50 }, { day: 'Thu', pct: 50 }, { day: 'Fri', pct: 0 }, { day: 'Sat', pct: 33 }, { day: 'Sun', pct: 50 },
    ],
    excuses: [{ label: 'No time', count: 6 }, { label: 'Not in the mood', count: 3 }, { label: 'Will do tomorrow', count: 1 }],
    missedList: ['DSA practice (Fri)', 'Gym (Fri)', 'Capstone work (Fri)', 'Mock interview prep (Wed)', 'DBMS revision (Thu)'],
    analysis: 'Half your commitments were missed. "No time" appeared six times, yet your Friday log shows zero activity. This is a priority problem, not a time problem.',
    actions: ['Reduce the daily plan to the 3 most important tasks.', 'Start the day with the hardest task.'],
  },
  {
    id: 'r1', week: 'Oct 13 – Oct 19', label: 'Week 3', score: 44, committed: 18, completed: 8, missed: 10,
    best: { day: 'Monday', pct: 75 }, worst: { day: 'Thursday', pct: 0 },
    daily: [
      { day: 'Mon', pct: 75 }, { day: 'Tue', pct: 50 }, { day: 'Wed', pct: 50 }, { day: 'Thu', pct: 0 }, { day: 'Fri', pct: 25 }, { day: 'Sat', pct: 50 }, { day: 'Sun', pct: 25 },
    ],
    excuses: [{ label: 'Not in the mood', count: 5 }, { label: 'No time', count: 4 }, { label: 'Too tired', count: 1 }],
    missedList: ['Most evening tasks', 'Gym (Thu)', 'DSA practice (Thu)'],
    analysis: 'First full week of tracking. Motivation-driven days (Monday) outperformed everything else. Evenings are where commitments go to die.',
    actions: ['Move critical tasks before 12 PM.', 'Remove "mood" from the decision.'],
  },
];

export const CONSISTENCY_HISTORY = [
  { week: 'Wk 1', score: 38 }, { week: 'Wk 2', score: 41 }, { week: 'Wk 3', score: 44 },
  { week: 'Wk 4', score: 52 }, { week: 'Wk 5', score: 78 }, { week: 'Wk 6', score: 67 },
];

export const GOAL_CHIPS = [
  'Improve my DSA skills.',
  'Build my career.',
  'Get consistent at the gym.',
  'Complete my project.',
  'Build a new habit.',
];

export const QUICK_ACTIONS = [
  { id: 'progress', label: 'Review My Progress' },
  { id: 'tasks', label: "Show Today's Tasks" },
  { id: 'excuses', label: 'Analyse My Excuses' },
  { id: 'report', label: 'Generate Reality Report' },
];

export const WELCOME_MESSAGE = `Welcome to Brutality AI.

Before we start, understand one thing.

I am not here to make you feel better about the goals you haven't achieved.

I am here to help you become someone who actually follows through.

What is the one goal you have been postponing?`;

export const AGENTS = [
  { n: '01', key: 'onboarding', name: 'Onboarding Agent', blurb: 'Turns ambitions into measurable daily commitments.', detail: 'Asks the hard questions: by when, how often, how will we measure it. Then writes the commitments for you.' },
  { n: '02', key: 'checkin', name: 'Check-In Agent', blurb: 'Checks your daily progress and asks direct questions.', detail: 'Shows up every evening. Did you do it? How long? What proof do you have?' },
  { n: '03', key: 'confront', name: 'Confront Agent', blurb: 'Identifies excuses, vague responses and inconsistent claims.', detail: '"Busy" is not an answer. It compares what you said against what you logged.' },
  { n: '04', key: 'planner', name: 'Planner Agent', blurb: 'Adjusts your plan based on actual performance.', detail: 'Missing a lot? It shrinks the plan. Hitting everything? It raises the bar.' },
  { n: '05', key: 'reality', name: 'Reality Agent', blurb: 'Generates weekly Reality Reports and identifies behavioural patterns.', detail: 'Finds the day, time and excuse that keep repeating, and puts it in writing.' },
  { n: '06', key: 'memory', name: 'Memory Agent', blurb: 'Remembers previous commitments, check-ins and recurring excuses.', detail: 'Never forgets what you promised last Tuesday. Neither will you.' },
];
