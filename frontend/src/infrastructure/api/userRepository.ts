/**
 * API Repository: User
 * 
 * Implementation of IUserRepository using the HTTP API.
 */

import { httpClient } from '../http/httpClient';
import type { User } from '../../domain/entities';
import type { IUserRepository } from '../../domain/userRepository';

export class UserApiRepository implements IUserRepository {
  private readonly basePath = '/api/v1/users';

  async findAll(): Promise<User[]> {
    return httpClient.get<User[]>(this.basePath);
  }

  async findById(id: number): Promise<User | null> {
    try {
      return await httpClient.get<User>(`${this.basePath}/${id}`);
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(data: Omit<User, 'id'>): Promise<User> {
    return httpClient.post<User>(this.basePath, data);
  }

  async update(id: number, data: Partial<Omit<User, 'id'>>): Promise<User> {
    return httpClient.put<User>(`${this.basePath}/${id}`, data);
  }

  async delete(id: number): Promise<void> {
    await httpClient.delete(`${this.basePath}/${id}`);
  }
}

export const userRepository = new UserApiRepository();
