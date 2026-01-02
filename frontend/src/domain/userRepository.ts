/**
 * User Repository Interface
 * 
 * Defines the contract for user data operations.
 */

import type { User } from './entities';

export interface IUserRepository {
  findAll(): Promise<User[]>;
  findById(id: number): Promise<User | null>;
  create(data: Omit<User, 'id'>): Promise<User>;
  update(id: number, data: Partial<Omit<User, 'id'>>): Promise<User>;
  delete(id: number): Promise<void>;
}
