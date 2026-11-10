/** Service facade. UI talks only to this file. Today it wraps mock logic + localStorage;
 *  tomorrow each function becomes a fetch() to the real backend. */
import { generateReply } from './mockAI.js';
import { SEED_REPORTS, CONSISTENCY_HISTORY } from '../data/mockData.js';

export const chatService = { sendMessage: generateReply };
export const reportService = {
  async list() { return SEED_REPORTS; },
  async history() { return CONSISTENCY_HISTORY; },
};
