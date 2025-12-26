import pytest
from decimal import Decimal
from cashdata.domain.entities.user import User
from cashdata.domain.entities.monthly_income import MonthlyIncome, IncomeSource
from cashdata.domain.value_objects.money import Money, Currency
from cashdata.domain.value_objects.period import Period
from cashdata.domain.value_objects.percentage import Percentage
from cashdata.domain.services.apportionment_calculator import ApportionmentCalculator
from cashdata.domain.exceptions.domain_exceptions import InvalidCalculation


# Fixtures
@pytest.fixture
def make_user():
    def _make(id, name, email, wage_amount, currency=Currency.USD):
        return User(
            id=id,
            name=name,
            email=email,
            wage=Money(Decimal(str(wage_amount)), currency),
        )

    return _make


@pytest.fixture
def period_dec_2025():
    """Fixture for December 2025 period"""
    return Period.from_string("202512")


@pytest.fixture
def calculator():
    """Fixture for ApportionmentCalculator instance"""
    return ApportionmentCalculator()


class TestApportionmentCalculatorProportionalSplit:
    """Tests for proportional split based on incomes"""

    def test_should_calculate_proportional_split_for_two_users(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Javier earns 2540 USD and Ailen earns 1800 USD in December 2025
        When: Calculating apportionment percentages
        Then: Javier should contribute 58.52% and Ailen 41.47%
        """
        user_javier = make_user(1, "Javier", "j@example.com", 2540)
        user_ailen = make_user(2, "Ailén", "a@example.com", 1800)

        incomes = [
            MonthlyIncome(1, 1, period_dec_2025, Money("2540", Currency.USD)),
            MonthlyIncome(2, 2, period_dec_2025, Money("1800", Currency.USD)),
        ]

        result = calculator.calculate_percentages(
            [user_javier, user_ailen], incomes, period_dec_2025
        )

        total = Decimal("2540") + Decimal("1800")
        expected_javier = Percentage((Decimal("2540") / total) * 100)
        expected_ailen = Percentage((Decimal("1800") / total) * 100)

        assert result[1].is_close_to(expected_javier)
        assert result[2].is_close_to(expected_ailen)
        assert (result[1] + result[2]).is_close_to(Percentage("100"))

    def test_should_calculate_proportional_split_for_three_users(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Three users with incomes 3000, 2000, and 1000
        When: Calculating apportionment percentages
        Then: Percentages should be 50%, 33.33%, and 16.67%
        """
        user_olga = make_user(1, "Olga", "olga@email.com", 3000)
        user_margarita = make_user(2, "Margarita", "margarita@email.com", 2000)
        user_ana = make_user(3, "Ana", "ana@email.com", 1000)

        incomes = [
            MonthlyIncome(1, 1, period_dec_2025, Money("3000", Currency.USD)),
            MonthlyIncome(2, 2, period_dec_2025, Money("2000", Currency.USD)),
            MonthlyIncome(3, 3, period_dec_2025, Money("1000", Currency.USD)),
        ]

        result = calculator.calculate_percentages(
            [user_olga, user_margarita, user_ana],
            incomes,
            period_dec_2025,
        )

        all_pct = Percentage(sum([pct.value for pct in result.values()]))

        assert result[1].is_close_to(Percentage(Decimal(3000 / 6000 * 100)))
        assert result[2].is_close_to(Percentage(Decimal(2000 / 6000 * 100)))
        assert result[3].is_close_to(Percentage(Decimal(1000 / 6000 * 100)))
        assert all_pct.is_close_to(Percentage(100))

    @pytest.mark.parametrize(
        "user_data_list",
        [
            [{"id": 1, "name": "Alice", "email": "a@test.com", "wage_amount": 1000}],
            [
                {
                    "id": 1,
                    "name": "Alice",
                    "email": "a@test.com",
                    "wage_amount": 2500.50,
                },
                {"id": 2, "name": "Bob", "email": "b@test.com", "wage_amount": 1200.75},
                {"id": 3, "name": "Charlie", "email": "c@test.com", "wage_amount": 800},
            ],
            [
                {
                    "id": 1,
                    "name": "Alice",
                    "email": "a@test.com",
                    "wage_amount": 1000,
                },
                {"id": 2, "name": "Bob", "email": "b@test.com", "wage_amount": 1000},
                {
                    "id": 3,
                    "name": "Charlie",
                    "email": "c@test.com",
                    "wage_amount": 1000,
                },
                {
                    "id": 4,
                    "name": "Charlie",
                    "email": "ch@test.com",
                    "wage_amount": 1000,
                },
            ],
            [
                {
                    "id": 1,
                    "name": "User A",
                    "email": "u1@test.com",
                    "wage_amount": 0.01,
                },
                {
                    "id": 2,
                    "name": "User B",
                    "email": "u2@test.com",
                    "wage_amount": 0.02,
                },
            ],
        ],
        ids=[
            "single_user",
            "multiple_users1",
            "multiple_users2",
            "low_wages",
        ],
    )
    def test_should_sum_to_100_percent(
        self, calculator, make_user, period_dec_2025, user_data_list
    ):
        users = [make_user(**data) for data in user_data_list]
        period_wages = [
            MonthlyIncome(
                id=0,
                user_id=user.id,
                period=period_dec_2025,
                amount=Money(str(user.wage.amount)),
            )
            for user in users
        ]

        result = calculator.calculate_percentages(users, period_wages, period_dec_2025)
        print(result[1])
        total_percentage = sum([pct for pct in result.values()], Percentage("0"))

        assert total_percentage.is_close_to(Percentage(100))

    def test_should_handle_different_income_amounts(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Users with incomes 1000 and 9000 (90/10 split)
        When: Calculating apportionment percentages
        Then: Should return 10% and 90%
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 9000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("10")
        assert result[2] == Percentage("90")
        assert all_pct == Percentage("100")


class TestApportionmentCalculatorEqualSplit:
    """Tests for equal split fallback"""

    def test_should_apply_equal_split_when_no_incomes_configured(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: No incomes configured for the period
        When: Calculating apportionment percentages
        Then: Should return 50% for each user
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 9000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, Period.from_string("202511"), Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("50")
        assert result[2] == Percentage("50")
        assert all_pct == Percentage("100")

    def test_should_apply_equal_split_for_three_users_without_incomes(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Three users with no incomes
        When: Calculating apportionment percentages
        Then: Should return 33.33% for each user
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 9000),
            make_user(3, "Test User 3", "t3@mail.com", 9000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, Period.from_string("202511"), Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1].is_close_to(Percentage("33.3333"))
        assert result[2].is_close_to(Percentage("33.3333"))
        assert result[3].is_close_to(Percentage("33.3333"))
        assert all_pct.is_close_to(Percentage("100"))

    def test_should_apply_equal_split_when_all_incomes_are_zero(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: All users have zero income for the period
        When: Calculating apportionment percentages
        Then: Should return 50% for each user (fallback)
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 9000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money("0"))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("50")
        assert result[2] == Percentage("50")
        assert all_pct == Percentage("100")


class TestApportionmentCalculatorPartialIncomes:
    """Tests for scenarios where only some users have incomes"""

    def test_should_give_100_percent_to_user_with_income_when_other_has_none(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Only Javier has income, Ailen has none
        When: Calculating apportionment percentages
        Then: Javier should have 100%, Ailen 0%
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 0),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("100")
        assert result[2] == Percentage("0")
        assert all_pct == Percentage("100")

    def test_should_distribute_proportionally_when_one_user_has_zero_income(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Javier has 2540 income, Ailen has 0 income explicitly set
        When: Calculating apportionment percentages
        Then: Javier 100%, Ailen 0%
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
            make_user(3, "Test User 3", "t3@mail.com", 0),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("50")
        assert result[2] == Percentage("50")
        assert result[3] == Percentage("0")
        assert all_pct == Percentage("100")


class TestApportionmentCalculatorPeriodFiltering:
    """Tests for correct period filtering"""

    def test_should_only_consider_incomes_from_specified_period(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Incomes exist for November and December
        When: Calculating for December only
        Then: Should only use December incomes
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 2000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(1000))
            for user in users
        ] + [
            MonthlyIncome(1, user.id, Period.from_string("202511"), Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("50")
        assert result[2] == Percentage("50")
        assert all_pct == Percentage("100")

    def test_should_ignore_incomes_from_other_periods(self, calculator, make_user):
        """
        Given: Users have incomes in multiple periods
        When: Calculating for a specific period
        Then: Other periods' incomes should not affect the result
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 2000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(1000))
            for user in users
        ] + [
            MonthlyIncome(1, user.id, Period.from_string("202511"), Money(user.wage.amount))
            for user in users
        ] + [
            MonthlyIncome(2, user.id, Period.from_string("202510"), Money(user.wage.amount))
            for user in users
        ] + [
            MonthlyIncome(3, user.id, Period.from_string("202509"), Money(user.wage.amount))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)
        all_pct = sum([pct for pct in result.values()], Percentage("0"))

        # Assert
        assert result[1] == Percentage("50")
        assert result[2] == Percentage("50")
        assert all_pct == Percentage("100")


class TestApportionmentCalculatorCurrencyValidation:
    """Tests for currency validation"""

    def test_should_raise_exception_when_incomes_have_different_currencies(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Javier has income in USD, Ailen in ARS
        When: Calculating apportionment percentages
        Then: Should raise InvalidCalculation exception
        """
        user_javier = make_user(1, "Javier", "j@example.com", 1000)
        user_ailen = make_user(2, "Ailén", "a@example.com", 1000000, Currency.ARS)

        with pytest.raises(InvalidCalculation) as exc_info:
            calculator.calculate_percentages(
                [user_javier, user_ailen],
                [
                    MonthlyIncome(1, 1, period_dec_2025, Money("1000", Currency.USD)),
                    MonthlyIncome(2, 2, period_dec_2025, Money("1000", Currency.ARS)),
                ],
                period_dec_2025,
            )

        assert "same currency" in str(exc_info.value).lower()


class TestApportionmentCalculatorEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_should_raise_exception_when_users_list_is_empty(
        self, calculator, period_dec_2025
    ):
        """
        Given: Empty list of users
        When: Calculating apportionment percentages
        Then: Should raise InvalidCalculation with message about users
        """
        users = []
        incomes = []

        with pytest.raises(InvalidCalculation) as edesc:
            _ = calculator.calculate_percentages(users, incomes, period_dec_2025)

        assert "at least one user" in str(edesc).lower()

    def test_should_handle_single_user(self, calculator, make_user, period_dec_2025):
        """
        Given: Only one user
        When: Calculating apportionment percentages
        Then: Should return 100% for that user
        """
        test_user = User(1, "Martha", "martha@waynecorp.com", Money("100000000000", Currency.USD))
        income = MonthlyIncome(1, 1, period_dec_2025, Money("100000000000100000000000"))

        result = calculator.calculate_percentages([test_user], [income], period_dec_2025)

        assert result[1] == Percentage(100)

    def test_should_raise_exception_when_users_is_none(
        self, calculator, period_dec_2025
    ):
        """
        Given: users parameter is None
        When: Calculating apportionment percentages
        Then: Should raise InvalidCalculation
        """
        with pytest.raises(InvalidCalculation) as edesc:
            _ = calculator.calculate_percentages(None, None, period_dec_2025)

        assert "at least one user" in str(edesc).lower()

    def test_should_raise_exception_when_incomes_is_none(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: incomes parameter is None
        When: Calculating apportionment percentages
        Then: Should raise InvalidCalculation
        """
        test_user = User(1, "Martha", "martha@waynecorp.com", Money("100000000000", Currency.USD))

        with pytest.raises(InvalidCalculation) as edesc:
            _ = calculator.calculate_percentages([test_user], None, period_dec_2025)

        assert "cannot be none" in str(edesc).lower()


class TestApportionmentCalculatorReturnType:
    """Tests for return type and structure"""

    def test_should_return_dict_with_user_ids_as_keys(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Valid users and incomes
        When: Calculating apportionment percentages
        Then: Should return dict with user IDs as keys
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 2000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(1000))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)

        # Assert
        assert isinstance(result, dict)
        assert result.keys() == {1, 2}

    def test_should_return_percentage_objects_as_values(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Valid users and incomes
        When: Calculating apportionment percentages
        Then: All values should be Percentage objects
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 2000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(1000))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)

        # Assert
        assert all([isinstance(pct, Percentage) for pct in result.values()])

    def test_should_include_all_users_in_result(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Two users
        When: Calculating apportionment percentages
        Then: Result should contain entries for both users
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 2000),
            make_user(2, "Test User 2", "t2@mail.com", 1000),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, Money(1000))
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)

        # Assert
        assert len(result) == 2


class TestApportionmentCalculatorPrecision:
    """Tests for decimal precision"""

    def test_should_use_decimal_for_all_calculations(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Incomes that result in repeating decimals
        When: Calculating apportionment percentages
        Then: Should maintain precision without float errors
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1600),
            make_user(2, "Test User 2", "t2@mail.com", 1800),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, user.wage)
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)

        # Assert
        assert result[1].is_close_to(Percentage.from_decimal(0.47058824))
        assert result[2].is_close_to(Percentage.from_decimal(0.52941176))

    def test_should_handle_very_small_income_differences(
        self, calculator, make_user, period_dec_2025
    ):
        """
        Given: Two users with incomes differing by 0.01
        When: Calculating apportionment percentages
        Then: Should calculate correctly with proper precision
        """
        # Arrange
        users = [
            make_user(1, "Test User 1", "t1@mail.com", 1501),
            make_user(2, "Test User 2", "t2@mail.com", 1499),
        ]

        incomes = [
            MonthlyIncome(0, user.id, period_dec_2025, user.wage)
            for user in users
        ]

        # Act
        result = calculator.calculate_percentages(users, incomes, period_dec_2025)

        # Assert
        assert result[1].is_close_to(Percentage.from_decimal(0.50033333))
        assert result[2].is_close_to(Percentage.from_decimal(0.49966667))