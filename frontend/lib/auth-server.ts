import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  database: {
    type: 'memory',
  },
  emailAndPassword: {
    enabled: true,
  },
});