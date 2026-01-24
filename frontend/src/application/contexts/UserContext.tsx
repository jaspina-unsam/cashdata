/**
 * User Context
 *
 * Provides the active user selection across the application. This is an ephemeral
 * selector for the MVP (resets on page reload). Default active user id = 1.
 */
import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import type { User } from '../../domain/entities';
import { userRepository } from '../../infrastructure/api/userRepository';

interface UserContextValue {
  activeUserId: number;
  setActiveUserId: (id: number) => void;
  users: User[];
  activeUser?: User | undefined;
  isLoading: boolean;
}

const UserContext = createContext<UserContextValue | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [activeUserId, setActiveUserId] = useState<number>(1); // default = 1
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;

    const loadUsers = async () => {
      try {
        setIsLoading(true);
        const fetched = await userRepository.findAll();
        if (mounted) setUsers(fetched);
      } catch (error) {
        console.error('Failed to load users:', error);
        if (mounted) setUsers([]);
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    void loadUsers();

    return () => {
      mounted = false;
    };
  }, []);

  const activeUser = users.find((u) => u.id === activeUserId);

  return (
    <UserContext.Provider value={{ activeUserId, setActiveUserId, users, activeUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
}

export function useActiveUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useActiveUser must be used within a UserProvider');
  }
  return context;
}
