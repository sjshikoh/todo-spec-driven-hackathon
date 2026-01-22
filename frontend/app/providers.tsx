'use client';

import { useEffect } from 'react';
import { auth } from '@/lib/auth';

export function Providers({ children }: { children: React.ReactNode }) {
  const session = auth.useSession();

  useEffect(() => {
    console.log('Auth session:', session);
  }, [session]);

  return <>{children}</>;
}
