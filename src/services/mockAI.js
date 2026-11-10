/* =============================================================================
   MOCK AI RESPONSE ENGINE  (frontend-only)
   -----------------------------------------------------------------------------
   !! THIS FILE IS A STAND-IN FOR A REAL LLM BACKEND !!
   `generateReply()` has the same contract a real endpoint would have:
        input : { message, history, context }
        output: Promise<{ agent, text, suggestions?, card? }>
   To go live, replace the body of `generateReply` with a fetch() to your API
   (e.g. POST /api/chat). The Chat UI never needs to change.
   ============================================================================= */

const pick = (arr, avoid = []) => {
  const pool = arr.filter((x) => !avoid.includes(x));
  const list = pool.length ? pool : arr;
  return list[Math.floor(Math.random() * list.length)];
};

const has = (t, words) => words.some((w) => t.includes(w));

/* ---------------- intent detection ---------------- */
export function detectIntent(raw) {
  const t = raw.toLowerCase().trim();
  if (!t) return 'empty';
  if (/^(hi|hello|hey|yo|sup|good (morning|evening|afternoon))\b/.test(t) && t.length < 25) return 'greeting';
  if (has(t, ['thank', 'thanks', 'thx'])) return 'thanks';
  if (has(t, ['reality report', 'weekly report', 'generate report', 'generate reality'])) return 'report';
  if (has(t, ["today's task", 'todays task', 'show today', 'my tasks', 'what do i have', 'what\'s on today', 'whats on today', 'to-do', 'todo'])) return 'tasks';
  if (has(t, ['analyse my excuse', 'analyze my excuse', 'my excuses', 'excuse pattern', 'what are my excuses'])) return 'excuse_analysis';
  if (has(t, ['review my progress', 'my progress', 'how am i doing', 'how am i', 'my streak', 'consistency', 'my score'])) return 'progress';
  if (has(t, ['i missed', 'missed', "didn't do", 'didnt do', 'did not do', 'skipped', 'failed to', "couldn't", 'couldnt', "haven't", 'havent started', 'i failed'])) return 'missed';
  if (has(t, ['no time', "don't have time", 'dont have time', 'too busy', 'busy', 'swamped', 'schedule was'])) return 'excuse_time';
  if (has(t, ['tired', 'exhausted', 'sleepy', 'drained', 'burnt out', 'burned out', 'no energy'])) return 'excuse_tired';
  if (has(t, ['not in the mood', 'no motivation', 'unmotivated', "didn't feel like", 'didnt feel like', "don't feel like", 'dont feel like', 'lazy', 'bored'])) return 'excuse_mood';
  if (has(t, ['tomorrow', 'later', 'next week', 'monday', 'will do it', "i'll do it", 'ill do it', 'tonight'])) return 'excuse_tomorrow';
  if (has(t, ['completed', 'finished', 'i did', 'done with', 'i solved', 'i studied', 'i worked out', 'i went to', 'i built', 'i wrote', 'all done'])) return 'completed';
  if (has(t, ['dsa', 'leetcode', 'algorithm', 'data structure', 'coding interview'])) return 'goal_dsa';
  if (has(t, ['gym', 'workout', 'fitness', 'exercise', 'weight', 'run '])) return 'goal_gym';
  if (has(t, ['career', 'job', 'placement', 'interview', 'resume', 'promotion'])) return 'goal_career';
  if (has(t, ['project', 'startup', 'app', 'website', 'capstone', 'thesis', 'portfolio', 'ship'])) return 'goal_project';
  if (has(t, ['habit', 'routine', 'wake up', 'sleep', 'read', 'meditat', 'journal'])) return 'goal_habit';
  if (has(t, ['goal', 'want to', 'plan to', 'need to', 'trying to', 'wish', 'dream'])) return 'goal_generic';
  if (has(t, ['stuck', 'overwhelm', 'anxious', 'stress', 'depress', 'hopeless'])) return 'struggling';
  if (has(t, ['help', 'what can you do', 'how does this work', 'how do you work'])) return 'help';
  if (t.length < 12) return 'vague';
  return 'fallback';
}

/* ---------------- response banks ---------------- */
const BANK = {
  greeting: [
    "Good. You showed up. That's already more than most people do.\n\nSo: what's the one goal you've been postponing?",
    "Hello. Skip the small talk. What are you committing to today?",
  ],
  thanks: [
    'No thanks needed. Results are the only thank-you I accept. What are you doing next?',
    'Understood. Now go and do the work. Check back in tonight.',
  ],
  empty: ['You sent nothing. That is also an answer, and it is the one most people give themselves. Try again.'],
  vague: [
    '"{m}" is not enough for me to work with. Be specific: what exactly will you do, and by when?',
    'That is too vague to hold you accountable to. Give me a number, a duration, or a deadline.',
  ],
  help: [
    "I do four things:\n\n1. Turn your goals into measurable daily commitments.\n2. Check whether you actually did them.\n3. Call out excuses and vague answers.\n4. Adjust your plan using real performance, then summarise it in a weekly Reality Report.\n\nStart by telling me the goal you keep postponing.",
  ],
  goal_dsa: [
    "DSA. Good. It is measurable, which means you cannot hide.\n\nHere is a starting commitment:\n• Solve 2 problems every day (1 easy/medium, 1 from your weak topic)\n• 30 minutes reviewing yesterday's mistakes\n• 1 timed mock set every Sunday\n\nBy what date do you need to be ready, and at what time of day will you actually do it?",
    "Improving at DSA is not a mood, it is a count. Two problems a day, every day.\n\nTell me your deadline and which time slot you are locking in. \"Whenever I get time\" is not a slot.",
  ],
  goal_gym: [
    "Gym consistency. Most people fail this one at the decision point, not the workout.\n\nProposed commitment:\n• 4 sessions a week, fixed days\n• Bag packed the night before\n• 45 minutes, no negotiation\n\nWhich four days, and what time? Answer exactly.",
    "Getting fit is simple. Showing up is the whole game.\n\nPick your 4 training days and a start time. I will hold you to them.",
  ],
  goal_career: [
    "Career growth is too broad to track, so let's make it concrete.\n\nWhich of these is the real target?\n• A specific role or company\n• A skill you must be able to demonstrate\n• A deadline such as placements or an interview date\n\nGive me one, plus the date.",
    "\"Build my career\" cannot be completed in a day, so it cannot be tracked. Name the next milestone: the job you want, and when you need it by.",
  ],
  goal_project: [
    "A project. These die at 80% because nobody defines \"done\".\n\nTell me:\n1. What does the finished version include?\n2. The launch date.\n3. How many focused hours per day you will give it.\n\nThen I will break it into daily deliverables.",
    "Good. Now define done. What does the shipped version look like, and when do you ship it? A project without a date is a hobby.",
  ],
  goal_habit: [
    "A new habit. Which one, and what is the smallest version you will not skip, even on your worst day?\n\nAlso tell me when it happens: after which existing routine?",
    "Habits fail when they are vague. State the habit, the trigger and the minimum. Example: \"After breakfast, I read 10 pages.\"",
  ],
  goal_generic: [
    "I hear the intention. Intentions are free. Now give me the commitment: what will you do daily, for how long, and starting when?",
    "That is a wish until it has a number and a deadline. What is the measurable version of this goal?",
  ],
  commit_followup: [
    "Locked in. Here is what I have recorded:\n\n• Goal captured\n• Daily commitment: as you stated\n• Check-in: tonight at 9:00 PM\n\nOpen your Daily Commitments to see it on the board. Tonight I will ask whether you did it, and \"I was busy\" will not be accepted.",
  ],
  missed: [
    "Noted. Missing a task is information. Hiding it is the problem.\n\nAnswer plainly:\n1. What exactly did you skip?\n2. What did you do in that time instead?\n3. What is the specific plan to recover it today?\n\nNo adjectives, just facts.",
    "Okay. No lecture. Just the facts: what did you miss, what actually happened, and when will you make it up? Give me a time, not a feeling.",
  ],
  excuse_time: [
    "\"No time.\" Let's test it.\n\nYou have 24 hours. Sleep is 7–8. Work or study takes maybe 8. That leaves roughly 8 hours, so where did the commitment's 45 minutes go?\n\nIt is rarely time. It is priority. Which activity did you choose over it?",
    "You have said \"no time\" before. It appears in your Reality Reports 5 times this week. Time is not missing; it is being spent somewhere.\n\nTell me honestly: what did you do with the hour you were supposed to use?",
  ],
  excuse_tired: [
    "Tired is real. It is also convenient.\n\nHere is the test: could you have done a 10-minute version? If yes, tiredness removed the ambition, not the ability.\n\nFix it: what time did you sleep, and what will you change tonight so that tomorrow's commitment is not negotiable?",
    "Fair, sleep matters. But look at your pattern: the tired excuse shows up mainly after 6 PM. Move the hard task to the morning and see if the excuse disappears.",
  ],
  excuse_mood: [
    "\"Not in the mood\" is the most expensive sentence in self-improvement. Mood did not make the commitment. You did.\n\nYou don't need to feel like it. You need to start for 5 minutes. Will you?",
    "Motivation is unreliable, and that is exactly why we use commitments. Do the minimum version now. Then tell me what happened.",
  ],
  excuse_tomorrow: [
    "\"Tomorrow\" is how a week disappears. Be exact: what time tomorrow, and what happens to today's task?\n\nIf you cannot give me a time, I will log today as missed.",
    "You said tomorrow last time too. That is the pattern in your history. What changes tomorrow that you cannot change right now?",
  ],
  completed: [
    "Good. Now prove it. What exactly did you complete, how long did it take, and what was the hardest part?\n\nIf the answer is specific, I will mark it done.",
    "Acknowledged. Specifics, please: numbers, duration, outcome. \"Did it\" is a claim. Details are evidence.",
  ],
  struggling: [
    "That sounds heavy, and I am not going to wave it away. If it feels like more than a rough patch, please talk to someone you trust or a professional.\n\nFor today, shrink the plan to one task. One. What is the smallest thing you can complete in the next 20 minutes?",
  ],
  fallback: [
    "I want to turn that into something trackable. In one sentence: what will you do, how often, and by when?",
    "Understood. Where does it connect to your goals? Tell me what you will do about it today, in measurable terms.",
    "Let's make that concrete. Name the action, the duration and the deadline.",
  ],
};

const AGENT_FOR = {
  greeting: 'Onboarding Agent', goal_dsa: 'Onboarding Agent', goal_gym: 'Onboarding Agent', goal_career: 'Onboarding Agent',
  goal_project: 'Onboarding Agent', goal_habit: 'Onboarding Agent', goal_generic: 'Onboarding Agent', help: 'Onboarding Agent',
  missed: 'Check-In Agent', completed: 'Check-In Agent', tasks: 'Check-In Agent', progress: 'Memory Agent',
  excuse_time: 'Confront Agent', excuse_tired: 'Confront Agent', excuse_mood: 'Confront Agent', excuse_tomorrow: 'Confront Agent',
  excuse_analysis: 'Reality Agent', report: 'Reality Agent', struggling: 'Check-In Agent',
};

const SUGGEST = {
  goal_dsa: ['Every morning at 7 AM', 'By 20 December', 'Evenings after college'],
  goal_gym: ['Mon, Tue, Thu, Sat at 6 PM', 'Mornings before college'],
  goal_career: ['Placements in December', 'Land a backend internship'],
  goal_project: ['Ship by 15 January', '2 hours every day'],
  goal_habit: ['Read 10 pages daily', 'Wake up at 6 AM'],
  missed: ['I had no time', 'I was too tired', "I'll do it tomorrow"],
  excuse_time: ['I scrolled my phone', 'I was studying something else'],
  excuse_tired: ['I slept at 2 AM', 'I will do the short version now'],
  excuse_mood: ['Okay, starting 5 minutes now'],
  excuse_tomorrow: ['Tomorrow at 7 AM sharp', 'Starting now instead'],
  greeting: ['Improve my DSA skills.', 'Get consistent at the gym.'],
};

/* ---------------- data-driven replies ---------------- */
function tasksReply(ctx) {
  const { tasks = [] } = ctx;
  const pend = tasks.filter((t) => t.status === 'pending');
  const done = tasks.filter((t) => t.status === 'done');
  const missed = tasks.filter((t) => t.status === 'missed');
  const lines = tasks.map((t) => `${t.status === 'done' ? '✓' : t.status === 'missed' ? '✗' : '○'} ${t.time}  ${t.title}`).join('\n');
  const verdict = pend.length === 0
    ? 'Everything is resolved. Good. Check in tonight.'
    : `${pend.length} still open. The next one is "${pend[0].title}" at ${pend[0].time}. Not later. Then.`;
  return {
    text: `Here is today:\n\n${lines || 'No tasks scheduled. That is a problem on its own.'}\n\n${done.length} done · ${missed.length} missed · ${pend.length} pending.\n${verdict}`,
    card: { kind: 'tasks', done: done.length, missed: missed.length, pending: pend.length },
  };
}

function progressReply(ctx) {
  const { stats = {} } = ctx;
  const pct = stats.consistency ?? 0;
  let verdict;
  if (pct >= 80) verdict = 'That is strong. Do not celebrate yet; protect it.';
  else if (pct >= 60) verdict = 'Decent, not good. The gap between 60% and 80% is where your excuses live.';
  else verdict = 'This is not where you said you would be. The numbers do not lie, even if you do.';
  return {
    text: `Here is the reality:\n\n• Consistency: ${pct}%\n• Current streak: ${stats.streak ?? 0} days\n• Completed: ${stats.completed ?? 0}\n• Missed: ${stats.missed ?? 0}\n\n${verdict}\n\nWhat is the single thing you will fix this week?`,
    card: { kind: 'progress', pct },
  };
}

function excuseAnalysisReply() {
  return {
    text: `Your excuse log, last 30 days:\n\n1. "No time" × 11, mostly after 6 PM\n2. "Too tired" × 6, mostly on Fridays\n3. "I'll do it tomorrow" × 5\n4. "Not in the mood" × 3\n\nPattern: your commitments fail in the evening, not in the morning. The Planner Agent recommends moving your hardest task to 7 AM.\n\nWill you accept that change?`,
    card: { kind: 'excuses' },
    suggestions: ['Yes, move it to the morning', 'Show me the full report'],
  };
}

function reportReply() {
  return {
    text: "Your latest Reality Report is ready.\n\nYou committed to 21 tasks this week and completed 14. Your performance dropped during the last three days. Your recurring excuse was lack of time. Next week, your priority is consistency, not increasing workload.\n\nOpen the full report with the button below.",
    card: { kind: 'report' },
  };
}

/* ---------------- public API ---------------- */
export async function generateReply({ message, history = [], context = {} }) {
  const intent = detectIntent(message);
  const lastAI = [...history].reverse().find((m) => m.role === 'ai');
  const recent = history.filter((m) => m.role === 'ai').slice(-6).map((m) => m.text);

  let out;
  switch (intent) {
    case 'tasks': out = tasksReply(context); break;
    case 'progress': out = progressReply(context); break;
    case 'excuse_analysis': out = excuseAnalysisReply(); break;
    case 'report': out = reportReply(); break;
    default: {
      // After a goal prompt, a specific follow-up (time/date words) confirms the commitment.
      const followsGoal = lastAI && /(by what date|which four days|what time|slot|deadline|launch date)/i.test(lastAI.text);
      const specific = /\b(\d{1,2}\s?(am|pm)|morning|evening|night|every day|daily|monday|tuesday|wednesday|thursday|friday|saturday|sunday|dec|jan|feb|mar|\d{1,2}(st|nd|rd|th)?)\b/i.test(message);
      if (followsGoal && specific && intent !== 'missed') {
        out = { text: pick(BANK.commit_followup, recent), card: { kind: 'commit' }, suggestions: ["Show Today's Tasks", 'Review My Progress'] };
      } else {
        const text = pick(BANK[intent] || BANK.fallback, recent).replace('{m}', message.slice(0, 40));
        out = { text, suggestions: SUGGEST[intent] };
      }
    }
  }

  // Simulate network + model latency. REPLACE with a real request.
  const delay = 700 + Math.min(1400, (out.text?.length || 0) * 6);
  await new Promise((r) => setTimeout(r, delay));
  return { agent: AGENT_FOR[intent] || 'Brutality Agent', ...out };
}
