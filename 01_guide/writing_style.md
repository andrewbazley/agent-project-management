# Writing style

For everything an agent writes in a project: documents, briefs, reports, indexes, commit messages,
code comments, and drafts a person will send as their own. The aim is prose that reads as if a
careful, curious scientist wrote it to a respected colleague. Many readers are scientists reading
in a second language, and later sessions take every sentence literally.

## The voice

- **Lead with the actor and the mechanism.** Say who did what and why it happened, in ordinary
  scientific English: "The filter removed 40 of 300 rows because their scores were tied."
- **Explain causes in place**, with "because", "since", "so" or a "which" clause, not by setting up
  a reveal.
- **Claim only what the data support, and say so once.** Hedge in the first person and by degree
  ("I think this is as much as the data show"), not with stacked qualifiers.
- **Disagree by conceding first**, then give the reason and the alternative. End on a proposal or a
  question rather than a verdict.
- **Use parentheses** for qualifiers and technical asides (the fit fails above 500 points).
- **Be candid** about what was a first try, unexpected or uncertain, without dramatizing it.
- **Vary sentence length naturally.** Long sentences chain connected clauses; short ones state a
  result or a decision. Neither is used for effect.
- **Make requests with a reason**, and acknowledge the cost to the other person.
- **For non-specialists**, define a term and then shorten it ("the polypeptide exit tunnel, or just
  the exit tunnel"), gloss a method with a "which" clause, and use an everyday analogy where it
  helps.

## By register

**Manuscripts, abstracts, proposals and reports.** Start with the biggest picture and narrow down,
each sentence connected to the one before. Use "we" and the active voice; present tense for
established facts, past tense for results. Leave out nuance too fine for the section. No
contractions. Avoid possessives on technical names ("hydrolysis by the enzyme", not "the enzyme's
hydrolysis"). End a section on its last real point, not a summary.

**Comments to co-authors.** First person, direct and collegial. State the constraint or evidence,
propose a way forward, offer to do more.

**Peer review and critique.** A short summary of the claim, then specific comments with page, line
or figure references. Direct requests ("Please clarify...") and pointed questions, each tied to
what it would establish.

**Email.** Open with "Hi [name]," and get to the point at once. Shift topics with "Also," or "As
for...". Close on an action or a question. Contractions are fine; one exclamation point at most,
never in a technical paragraph.

**Project records** (briefs, decisions, indexes, reports). Each sentence is a fact, a reason, a
request or a decision. Dates as YYYY-MM-DD, never "yesterday" or "last session". Paths in
backticks, relative to the repository root or the citing document, so the citation check can
follow them.

## Patterns to avoid

These make prose read as machine-written. The test is what a construction is doing: a contrast
between two real hypotheses, a colon before a list, or a short sentence that states a result is
fine. The same form used for emphasis, rhythm or drama is not.

- **Reveals:** "The answer: X.", "Here's the thing:", a sentence ending on a dash and a punchline.
  State the point.
- **Negation for effect:** "It's not X, it's Y", "conservative, not optimistic". Keep a contrast
  only when someone actually holds X.
- **Inverted emphasis:** "What this shows is...", "Central to this is...", "Worth noting is...".
  Put the subject first.
- **Staccato fragments:** "No signal. No contrast. Just noise." Write the sentence.
- **Rhythm devices:** pairs and triplets chosen for cadence, stacked "rather than" contrasts,
  parallel clauses repeated for effect.
- **Framing the text itself:** "This section explains...", "Here is an update on...". Start with the
  content.
- **Telling the reader how to read or feel:** "This raises an important question", "the right
  reading", "the form in which the result should be read".
- **Virtue and certainty words:** honest, genuinely, truly, defensible, clearly, importantly,
  notably, crucially, "it is worth noting".
- **Summary closers:** "In short", "Overall", "Together, these results...", a last sentence that
  restates the paragraph, except where the genre requires one (an abstract).
- **Stock words:** robust, leverage, seamless, delve, landscape, underscore, highlight (for
  findings), pivotal, nuanced, intricate, realm, harness, unlock, navigate (figuratively),
  elucidate, facilitate, "plays a role in".
- **Coined labels and agency for things:** describe a thing instead of naming it; a rule does not
  "decide", data do not "tell a story".
- **Punctuation for effect:** a dash pair for an aside and a semicolon between closely related
  clauses are fine in moderation. A dash that sets up a punchline, or semicolons chaining clauses
  for rhythm, are not.

## Clarity

- Define a project term or uncommon abbreviation before using it, and keep one meaning per term. A
  later session reads two words as two things.
- Make every "it", "this" and "they" point to one thing; repeat the noun if in doubt.
- Name the actor. Use the passive only when the actor does not matter, as is common in methods.
- Give numbers with units and their denominator ("12 of 48 designs at cutoff 0.8"), and both values
  for a change ("from 10 to 5 µM", not "2-fold").
- Avoid idioms and cultural references in technical documents.
- Split a sentence only when a reader would lose the thread; do not impose length limits.

## Mechanics

American spelling. No emoji in documents. In prose, write short lists inline with commas; use
bullets where the format calls for them (protocols, specifications, records, briefs). No slash
compounds ("only/mostly") in documents.

## Examples

| before | after |
|---|---|
| The published estimates were therefore conservative, not optimistic. | So the published estimates overstated the error rate, which makes them conservative. |
| This is stated first because it is the most defensible result, and the rest depends on it. | The rest of the paper depends on this result, so we describe it first. |
| What matters here is the scan rate. Not the buffer. Not the temperature. The scan rate. | Changing the scan rate shifted the peak, while changing the buffer or the temperature did not. |
| I wanted to provide a comprehensive update. Overall, progress has been robust. | Hi [name], things are going well. The plasmids are made and I'm transforming them now. |

## Code, comments and commits

Code can be as good as you can make it. Each script opens with a docstring: what it computes,
which decision governs it, what it reads and what it writes. Comments go where a good engineer
would put them; no banners, emoji, narration or "generated by" labels. Commit messages are one
sentence stating what is now true (`conventions.md`, Version control).

## Text a person wrote

Where a document mixes a person's own writing with an agent's, the agent revises only its own text.
It flags a passage of theirs that breaks these rules and suggests wording, but leaves the passage
unchanged unless they agree.
