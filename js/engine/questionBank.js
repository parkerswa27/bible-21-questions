// The rule-based question bank. Each entry is:
//   id        - unique key
//   category  - used to group suggested-question chips in the UI
//   label     - default phrasing shown as a clickable suggested question
//   match(t)  - t is the normalized (lowercase, punctuation-stripped) question text;
//               return true if this handler should answer the question
//   evaluate(character) - returns an answer object (see answerTypes.js)
//
// Order matters: more specific patterns are listed before more general ones,
// and questionEngine.js stops at the first match.
//
// GAME-INTEGRITY RULE: evaluate() must never leak the character's identity. Any
// clarifying text for a 'sometimes' answer must be a fixed, generic sentence tied
// to the QUESTION (defined right here, once), never to the specific character —
// see js/engine/answerTypes.js for why. Never pass character.notes into an answer.
//
// This module is also the swap point for the AI fallback: questionEngine.js tries
// every handler here first, and only calls the AI when nothing matches.

import {
  answerFromTriState,
  answerFromBoolean,
  answerFromYesNoUnknown,
  answerFromTimeline,
  makeAnswer,
} from './answerTypes.js';

export const QUESTION_BANK = [
  // --- Identity -----------------------------------------------------------
  {
    id: 'testament_old', category: 'Identity', label: 'Are you from the Old Testament?',
    match: (t) => /\bold testament\b/.test(t),
    evaluate: (c) => answerFromBoolean(c.testament === 'OT'),
  },
  {
    id: 'testament_new', category: 'Identity', label: 'Are you from the New Testament?',
    match: (t) => /\bnew testament\b/.test(t),
    evaluate: (c) => answerFromBoolean(c.testament === 'NT'),
  },
  {
    id: 'gender_woman', category: 'Identity', label: 'Are you a woman?',
    match: (t) => /\b(woman|female|girl|lady)\b/.test(t),
    evaluate: (c) => answerFromBoolean(c.gender === 'F'),
  },
  {
    id: 'gender_man', category: 'Identity', label: 'Are you a man?',
    match: (t) => /\b(man|male|guy|boy)\b/.test(t) && !/\bwoman|\bhuman/.test(t),
    evaluate: (c) => answerFromBoolean(c.gender === 'M'),
  },

  // --- Roles / offices ------------------------------------------------------
  {
    id: 'role_queen', category: 'Role', label: 'Were you a queen?',
    match: (t) => /\bqueen(s)?\b/.test(t),
    evaluate: (c) => answerFromBoolean(c.roles.some((r) => /queen/i.test(r))),
  },
  {
    id: 'role_king', category: 'Role', label: 'Were you a king?',
    match: (t) => /\bking(s)?\b/.test(t) && !/kingdom/.test(t),
    evaluate: (c) => answerFromTriState(c.king, { sometimesHint: "This depends on how the term 'king' is defined." }),
  },
  {
    id: 'role_judge', category: 'Role', label: 'Were you a judge of Israel?',
    match: (t) => /\bjudge(s)?\b/.test(t),
    evaluate: (c) => answerFromTriState(c.judge, { sometimesHint: "This depends on how the term 'judge' is defined." }),
  },
  {
    id: 'role_prophet', category: 'Role', label: 'Were you a prophet?',
    match: (t) => /\bprophet(s|ess|esses)?\b/.test(t),
    evaluate: (c) => answerFromTriState(c.prophet, { sometimesHint: "This depends on how the term 'prophet' is defined." }),
  },
  {
    id: 'role_priest', category: 'Role', label: 'Were you a priest?',
    match: (t) => /\bpriest(s|hood)?\b/.test(t),
    evaluate: (c) => answerFromTriState(c.priest, { sometimesHint: "This depends on how the term 'priest' is defined." }),
  },
  {
    id: 'role_apostle', category: 'Role', label: 'Were you an apostle?',
    match: (t) => /\bapostle(s)?\b/.test(t) || /\btwelve\b/.test(t),
    evaluate: (c) => answerFromTriState(c.apostle, { sometimesHint: "This depends on how the term 'apostle' is defined." }),
  },
  {
    id: 'role_disciple', category: 'Role', label: "Were you one of Jesus's disciples?",
    match: (t) => /\bdisciple(s)?\b/.test(t),
    evaluate: (c) => answerFromTriState(c.disciple, { sometimesHint: 'Scripture does not explicitly label this either way.' }),
  },
  {
    id: 'wrote_book', category: 'Role', label: 'Did you write a book of the Bible?',
    match: (t) => /\b(write|wrote|writer|author(ed)?)\b/.test(t) && /\bbook(s)?\b|\bbible\b|\bscripture(s)?\b/.test(t),
    evaluate: (c) => answerFromTriState(c.wrote_biblical_book, { sometimesHint: 'Authorship is traditionally held but debated by some scholars.' }),
  },

  // --- Morality --------------------------------------------------------------
  {
    id: 'morality_bad', category: 'Character', label: 'Are you considered a bad or villainous character?',
    match: (t) => /\b(bad|evil|wicked|villain(ous)?|sinful)\b/.test(t),
    evaluate: (c) => {
      const hint = 'Their portrayal in Scripture includes both admirable and troubling actions.';
      if (c.good_bad_neutral === 'bad') return makeAnswer('yes');
      if (c.good_bad_neutral === 'good') return makeAnswer('no');
      if (c.good_bad_neutral === 'mixed') return makeAnswer('sometimes', { hint });
      return makeAnswer('unknown');
    },
  },
  {
    id: 'morality_good', category: 'Character', label: 'Are you generally considered a good character?',
    match: (t) => /\b(good|righteous|godly|virtuous)\b/.test(t) && /\b(character|person|guy|man|woman|figure)?\b/.test(t),
    evaluate: (c) => {
      const hint = 'Their portrayal in Scripture includes both admirable and troubling actions.';
      if (c.good_bad_neutral === 'good') return makeAnswer('yes');
      if (c.good_bad_neutral === 'bad') return makeAnswer('no');
      if (c.good_bad_neutral === 'mixed') return makeAnswer('sometimes', { hint });
      return makeAnswer('unknown');
    },
  },

  // --- Family ------------------------------------------------------------
  {
    id: 'was_married', category: 'Family', label: 'Were you married?',
    match: (t) => /\bmarried\b|\bwife\b|\bhusband\b|\bspouse\b/.test(t),
    evaluate: (c) => answerFromYesNoUnknown(c.married),
  },
  {
    id: 'had_children', category: 'Family', label: 'Did you have children?',
    match: (t) => /\bchildren\b|\bkids\b|\bson(s)?\b|\bdaughter(s)?\b/.test(t) && /\bhave\b|\bany\b|\bdid\b/.test(t),
    evaluate: (c) => answerFromYesNoUnknown(c.had_children),
  },
  {
    id: 'genealogy', category: 'Family', label: 'Is your genealogy recorded in the Bible?',
    match: (t) => /\bgenealog(y|ies)\b|\bfamily tree\b/.test(t),
    evaluate: (c) => answerFromBoolean(c.genealogy_recorded),
  },

  // --- Death ---------------------------------------------------------------
  {
    id: 'violent_death', category: 'Life & Death', label: 'Did you die a violent death?',
    match: (t) => /\bviolent(ly)?\b|\bkilled\b|\bmurder(ed)?\b|\bcrucif(y|ied|ixion)\b|\bexecut(ed|ion)\b|\bassassinat(ed|ion)\b|\bbehead(ed|ing)?\b|\bstab(bed)?\b|\bslain\b/.test(t),
    evaluate: (c) => answerFromYesNoUnknown(c.violent_death),
  },

  // --- Time period (landmark-relative) -------------------------------------
  {
    id: 'flood_before', category: 'Time period', label: 'Did you live before the Great Flood?',
    match: (t) => /\bflood\b/.test(t) && /\bbefore\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_flood, 'before', { sometimesHint: 'Their life overlaps with this event.' }),
  },
  {
    id: 'flood_after', category: 'Time period', label: 'Did you live after the Great Flood?',
    match: (t) => /\bflood\b/.test(t) && /\bafter\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_flood, 'after', { sometimesHint: 'Their life overlaps with this event.' }),
  },
  {
    id: 'temple_before', category: 'Time period', label: 'Did you live before the First Temple was built?',
    match: (t) => /\btemple\b/.test(t) && /\bbefore\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_first_temple, 'before', { sometimesHint: 'Their life overlaps with this period.' }),
  },
  {
    id: 'temple_after', category: 'Time period', label: 'Did you live after the First Temple was built?',
    match: (t) => /\btemple\b/.test(t) && /\bafter\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_first_temple, 'after', { sometimesHint: 'Their life overlaps with this period.' }),
  },
  {
    id: 'exile_before', category: 'Time period', label: 'Did you live before the Babylonian exile?',
    match: (t) => /\bexile\b|\bcaptivity\b/.test(t) && /\bbefore\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_babylonian_exile, 'before', { sometimesHint: 'Their life overlaps with this period.' }),
  },
  {
    id: 'exile_after', category: 'Time period', label: 'Did you live after the Babylonian exile?',
    match: (t) => /\bexile\b|\bcaptivity\b/.test(t) && /\bafter\b/.test(t),
    evaluate: (c) => answerFromTimeline(c.before_or_after_babylonian_exile, 'after', { sometimesHint: 'Their life overlaps with this period.' }),
  },
];
