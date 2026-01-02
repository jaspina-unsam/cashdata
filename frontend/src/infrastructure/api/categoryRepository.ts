/**
 * API Repository: Category
 * 
 * Implementation of ICategoryRepository using the HTTP API.
 */

import { httpClient } from '../http/httpClient';
import type { Category } from '../../domain/entities';
import type { ICategoryRepository } from '../../domain/repositories';

export class CategoryApiRepository implements ICategoryRepository {
  private readonly basePath = '/api/v1/categories';

  async findAll(): Promise<Category[]> {
    return httpClient.get<Category[]>(this.basePath);
  }

  async findById(id: number): Promise<Category | null> {
    try {
      return await httpClient.get<Category>(`${this.basePath}/${id}`);
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(data: Omit<Category, 'id'>): Promise<Category> {
    return httpClient.post<Category>(this.basePath, data);
  }
}

export const categoryRepository = new CategoryApiRepository();
