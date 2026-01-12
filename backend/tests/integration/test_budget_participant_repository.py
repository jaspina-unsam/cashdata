import pytest

from app.domain.entities.budget_participant import BudgetParticipant
from app.infrastructure.persistence.repositories.sqlalchemy_budget_participant_repository import SQLAlchemyBudgetParticipantRepository


class TestBudgetParticipantRepository:
    def test_save_and_find_by_id(self, db_session):
        """Test saving and retrieving a budget participant"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant = BudgetParticipant(
            id=None,
            budget_id=1,
            user_id=1
        )

        # Save participant
        saved_participant = repo.save(participant)
        assert saved_participant.id is not None
        assert saved_participant.budget_id == 1
        assert saved_participant.user_id == 1

        # Find by ID
        found_participant = repo.find_by_id(saved_participant.id)
        assert found_participant is not None
        assert found_participant.id == saved_participant.id
        assert found_participant.budget_id == saved_participant.budget_id
        assert found_participant.user_id == saved_participant.user_id

    def test_find_by_budget_id(self, db_session):
        """Test finding participants by budget ID"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        # Create multiple participants for the same budget
        participant1 = BudgetParticipant(id=None, budget_id=1, user_id=1)
        participant2 = BudgetParticipant(id=None, budget_id=1, user_id=2)
        participant3 = BudgetParticipant(id=None, budget_id=2, user_id=1)  # Different budget

        participant1 = repo.save(participant1)
        participant2 = repo.save(participant2)
        participant3 = repo.save(participant3)

        # Find participants for budget 1
        budget_1_participants = repo.find_by_budget_id(1)
        assert len(budget_1_participants) == 2

        # Check that both participants belong to budget 1
        participant_ids = [p.id for p in budget_1_participants]
        assert participant1.id in participant_ids
        assert participant2.id in participant_ids

        # Find participants for budget 2
        budget_2_participants = repo.find_by_budget_id(2)
        assert len(budget_2_participants) == 1
        assert budget_2_participants[0].id == participant3.id

        # Find participants for non-existent budget
        empty_participants = repo.find_by_budget_id(999)
        assert len(empty_participants) == 0

    def test_find_by_user_id(self, db_session):
        """Test finding budgets where a user is a participant"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        # Create multiple participations for the same user
        participant1 = BudgetParticipant(id=None, budget_id=1, user_id=1)
        participant2 = BudgetParticipant(id=None, budget_id=2, user_id=1)
        participant3 = BudgetParticipant(id=None, budget_id=1, user_id=2)  # Different user

        participant1 = repo.save(participant1)
        participant2 = repo.save(participant2)
        participant3 = repo.save(participant3)

        # Find budgets for user 1
        user_1_participants = repo.find_by_user_id(1)
        assert len(user_1_participants) == 2

        # Check that both participations belong to user 1
        participant_ids = [p.id for p in user_1_participants]
        assert participant1.id in participant_ids
        assert participant2.id in participant_ids

        # Find budgets for user 2
        user_2_participants = repo.find_by_user_id(2)
        assert len(user_2_participants) == 1
        assert user_2_participants[0].id == participant3.id

        # Find budgets for non-existent user
        empty_participants = repo.find_by_user_id(999)
        assert len(empty_participants) == 0

    def test_find_by_budget_and_user(self, db_session):
        """Test finding a specific participant relationship"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant1 = BudgetParticipant(id=None, budget_id=1, user_id=1)
        participant2 = BudgetParticipant(id=None, budget_id=1, user_id=2)
        participant3 = BudgetParticipant(id=None, budget_id=2, user_id=1)

        participant1 = repo.save(participant1)
        participant2 = repo.save(participant2)
        participant3 = repo.save(participant3)

        # Find specific participant relationship
        found_participant = repo.find_by_budget_and_user(1, 1)
        assert found_participant is not None
        assert found_participant.id == participant1.id
        assert found_participant.budget_id == 1
        assert found_participant.user_id == 1

        # Find non-existent relationship
        not_found = repo.find_by_budget_and_user(1, 3)
        assert not_found is None

        not_found = repo.find_by_budget_and_user(3, 1)
        assert not_found is None

    def test_save_many(self, db_session):
        """Test saving multiple participants at once"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participants = [
            BudgetParticipant(id=None, budget_id=1, user_id=1),
            BudgetParticipant(id=None, budget_id=1, user_id=2),
            BudgetParticipant(id=None, budget_id=1, user_id=3)
        ]

        # Save many participants
        saved_participants = repo.save_many(participants)
        assert len(saved_participants) == 3

        for participant in saved_participants:
            assert participant.id is not None
            assert participant.budget_id == 1

        # Verify they were saved
        budget_participants = repo.find_by_budget_id(1)
        assert len(budget_participants) == 3

    def test_delete(self, db_session):
        """Test deleting a participant by ID"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant = BudgetParticipant(id=None, budget_id=1, user_id=1)
        saved_participant = repo.save(participant)

        # Verify it exists
        found = repo.find_by_id(saved_participant.id)
        assert found is not None

        # Delete it
        repo.delete(saved_participant.id)

        # Verify it's gone
        not_found = repo.find_by_id(saved_participant.id)
        assert not_found is None

    def test_delete_by_budget_id(self, db_session):
        """Test deleting all participants for a budget"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant1 = BudgetParticipant(id=None, budget_id=1, user_id=1)
        participant2 = BudgetParticipant(id=None, budget_id=1, user_id=2)
        participant3 = BudgetParticipant(id=None, budget_id=2, user_id=1)

        repo.save(participant1)
        repo.save(participant2)
        repo.save(participant3)

        # Verify participants exist
        budget_1_participants = repo.find_by_budget_id(1)
        assert len(budget_1_participants) == 2

        budget_2_participants = repo.find_by_budget_id(2)
        assert len(budget_2_participants) == 1

        # Delete all participants for budget 1
        repo.delete_by_budget_id(1)

        # Verify budget 1 participants are gone
        budget_1_participants_after = repo.find_by_budget_id(1)
        assert len(budget_1_participants_after) == 0

        # Verify budget 2 participants still exist
        budget_2_participants_after = repo.find_by_budget_id(2)
        assert len(budget_2_participants_after) == 1

    def test_delete_by_budget_and_user(self, db_session):
        """Test deleting a specific participant relationship"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant1 = BudgetParticipant(id=None, budget_id=1, user_id=1)
        participant2 = BudgetParticipant(id=None, budget_id=1, user_id=2)

        repo.save(participant1)
        repo.save(participant2)

        # Verify both exist
        assert repo.find_by_budget_and_user(1, 1) is not None
        assert repo.find_by_budget_and_user(1, 2) is not None

        # Delete specific relationship
        repo.delete_by_budget_and_user(1, 1)

        # Verify only the specific relationship is gone
        assert repo.find_by_budget_and_user(1, 1) is None
        assert repo.find_by_budget_and_user(1, 2) is not None

    def test_update_participant(self, db_session):
        """Test updating an existing participant"""
        repo = SQLAlchemyBudgetParticipantRepository(db_session)

        participant = BudgetParticipant(id=None, budget_id=1, user_id=1)
        saved_participant = repo.save(participant)

        # Update the participant (though budget_id and user_id are typically immutable)
        # For this test, we'll just verify the save method handles updates
        updated_participant = repo.save(saved_participant)

        # Verify it's the same record
        assert updated_participant.id == saved_participant.id
        assert updated_participant.budget_id == saved_participant.budget_id
        assert updated_participant.user_id == saved_participant.user_id