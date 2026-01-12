from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.use_cases.create_category_use_case import (
    CreateCategoryUseCase,
    CreateCategoryCommand,
)
from app.application.use_cases.list_categories_use_case import (
    ListCategoriesUseCase,
)
from app.application.use_cases.get_category_by_id_use_case import (
    GetCategoryByIdUseCase,
    GetCategoryByIdQuery,
)
from app.application.use_cases.list_purchases_by_category_use_case import (
    ListPurchasesByCategoryUseCase,
    ListPurchasesByCategoryQuery,
)
from app.application.dtos.category_dto import CreateCategoryInputDTO
from app.application.dtos.purchase_dto import (
    CategoryResponseDTO,
    PurchaseResponseDTO,
)
from app.application.mappers.purchase_dto_mapper import (
    CategoryDTOMapper,
    PurchaseDTOMapper,
)
from app.domain.repositories.iunit_of_work import IUnitOfWork
from app.infrastructure.api.dependencies import get_unit_of_work


router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.post(
    "",
    response_model=CategoryResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    responses={
        201: {"description": "Category created successfully"},
        400: {"description": "Invalid input data"},
    },
)
def create_category(
    category_data: CreateCategoryInputDTO, uow: IUnitOfWork = Depends(get_unit_of_work)
):
    """
    Create a new category for classifying purchases.

    - **name**: Category name (required)
    - **color**: Hex color code for UI display (optional, e.g., #FF5733)
    - **icon**: Icon identifier for UI display (optional)
    """
    try:
        command = CreateCategoryCommand(
            name=category_data.name, color=category_data.color, icon=category_data.icon
        )

        use_case = CreateCategoryUseCase(uow)
        category = use_case.execute(command)

        return CategoryDTOMapper.to_response_dto(category)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=List[CategoryResponseDTO],
    summary="List all categories",
    responses={
        200: {"description": "List of categories (may be empty)"},
    },
)
def list_categories(uow: IUnitOfWork = Depends(get_unit_of_work)):
    """
    List all available categories.

    Categories are shared across all users for consistency.
    """
    use_case = ListCategoriesUseCase(uow)
    categories = use_case.execute()

    return [CategoryDTOMapper.to_response_dto(cat) for cat in categories]


@router.get(
    "/{category_id}",
    response_model=CategoryResponseDTO,
    summary="Get category by ID",
    responses={
        200: {"description": "Category found"},
        404: {"description": "Category not found"},
    },
)
def get_category(category_id: int, uow: IUnitOfWork = Depends(get_unit_of_work)):
    """
    Retrieve a specific category by ID.
    """
    query = GetCategoryByIdQuery(category_id=category_id)
    use_case = GetCategoryByIdUseCase(uow)
    category = use_case.execute(query)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return CategoryDTOMapper.to_response_dto(category)


@router.get(
    "/{category_id}/purchases",
    response_model=List[PurchaseResponseDTO],
    summary="List purchases by category",
    responses={
        200: {"description": "List of purchases (may be empty)"},
        404: {"description": "Category not found"},
    },
)
def list_purchases_by_category(
    category_id: int,
    user_id: int = Query(..., description="User ID (from auth context)"),
    uow: IUnitOfWork = Depends(get_unit_of_work),
):
    """
    List all purchases for a specific category.

    Returns only purchases belonging to the authenticated user,
    sorted by date (most recent first).
    """
    # Verify category exists
    category_query = GetCategoryByIdQuery(category_id=category_id)
    get_category_use_case = GetCategoryByIdUseCase(uow)
    category = get_category_use_case.execute(category_query)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Get purchases
    query = ListPurchasesByCategoryQuery(category_id=category_id, user_id=user_id)
    use_case = ListPurchasesByCategoryUseCase(uow)
    purchases = use_case.execute(query)

    return [PurchaseDTOMapper.to_response_dto(p) for p in purchases]
