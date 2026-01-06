from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.create_user_use_case import CreateUserUseCase
from app.application.use_cases.get_user_by_id_use_case import GetUserByIdUseCase
from app.application.use_cases.list_all_users_use_case import ListAllUsersUseCase
from app.application.use_cases.update_user_use_case import UpdateUserUseCase
from app.application.use_cases.delete_user_use_case import DeleteUserUseCase
from app.application.dtos.user_dto import (
    CreateUserInputDTO,
    UpdateUserInputDTO,
    UserResponseDTO,
)
from app.domain.repositories import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "User with this email already exists"},
    },
)
def create_user(
    user_data: CreateUserInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Create a new user with wage information.
    
    - **name**: User's full name (1-100 characters)
    - **email**: Valid email address (must be unique)
    - **wage_amount**: Monthly wage amount (must be positive)
    - **wage_currency**: Currency code (ARS, USD)
    """
    try:
        # Execute use case with DTO directly
        use_case = CreateUserUseCase(uow)
        result = use_case.execute(user_data)
        return result
    
    except ValueError as e:
        # Email already exists or validation error
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "",
    response_model=List[UserResponseDTO],
    summary="List all users",
    responses={
        200: {"description": "List of all users"},
    },
)
def list_users(
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Retrieve all users in the system.
    
    Returns a list of all non-deleted users.
    """
    use_case = ListAllUsersUseCase(uow)
    return use_case.execute()


@router.get(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="Get user by ID",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    },
)
def get_user(
    user_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Retrieve a specific user by ID.
    
    - **user_id**: The ID of the user to retrieve
    """
    use_case = GetUserByIdUseCase(uow)
    result = use_case.execute(user_id)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    
    return result


@router.put(
    "/{user_id}",
    response_model=UserResponseDTO,
    summary="Update user",
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Email already in use by another user"},
    },
)
def update_user(
    user_id: int,
    user_data: UpdateUserInputDTO,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Update an existing user's information.
    
    - **user_id**: The ID of the user to update
    - **name**: New name (optional)
    - **email**: New email (optional, must be unique)
    - **wage_amount**: New wage amount (optional)
    - **wage_currency**: New wage currency (optional)
    """
    try:
        # Set the user_id in the DTO
        user_data.id = user_id
        
        # Execute use case with DTO directly
        use_case = UpdateUserUseCase(uow)
        result = use_case.execute(user_data)
        return result
    
    except ValueError as e:
        # User not found, email conflict, or validation error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
            )
        elif "already exists" in str(e).lower() or "already in use" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (soft delete)",
    responses={
        204: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
    },
)
def delete_user(
    user_id: int,
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    Soft delete a user by marking them as deleted.
    
    - **user_id**: The ID of the user to delete
    
    The user will not be physically removed from the database,
    but will be marked as deleted and excluded from queries.
    """
    try:
        use_case = DeleteUserUseCase(uow)
        use_case.execute(user_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
