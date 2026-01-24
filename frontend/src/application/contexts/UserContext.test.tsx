import { renderHook, act, waitFor } from '@testing-library/react';
import { UserProvider, useActiveUser } from './UserContext';
import { userRepository } from '../../infrastructure/api/userRepository';

jest.mock('../../infrastructure/api/userRepository');

describe('UserContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('initializes with activeUserId = 1', () => {
    const wrapper = ({ children }: any) => <UserProvider>{children}</UserProvider>;
    const { result } = renderHook(() => useActiveUser(), { wrapper });

    expect(result.current.activeUserId).toBe(1);
  });

  it('loads users on mount and exposes them', async () => {
    const mockUsers = [
      { id: 1, name: 'User 1', email: 'u1@test.com', deleted_at: null, created_at: '', updated_at: '' },
      { id: 2, name: 'User 2', email: 'u2@test.com', deleted_at: null, created_at: '', updated_at: '' },
    ];
    (userRepository.findAll as jest.Mock).mockResolvedValue(mockUsers);

    const wrapper = ({ children }: any) => <UserProvider>{children}</UserProvider>;
    const { result } = renderHook(() => useActiveUser(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.users).toEqual(mockUsers);
    });
  });

  it('setActiveUserId updates the active user id', async () => {
    const wrapper = ({ children }: any) => <UserProvider>{children}</UserProvider>;
    const { result } = renderHook(() => useActiveUser(), { wrapper });

    act(() => {
      result.current.setActiveUserId(2);
    });

    expect(result.current.activeUserId).toBe(2);
  });
});
