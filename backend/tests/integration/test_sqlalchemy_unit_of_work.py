import pytest

class TestSQLAlchemyUnitOfWork:

    def test_commit_persists_changes(session_factory):
        """
        DADO: Operaciones múltiples en UoW
        CUANDO: Se hace commit
        ENTONCES: Todos los cambios se persisten
        """
        pass

    def test_rollback_on_exception(session_factory):
        """
        DADO: Operación que lanza excepción
        CUANDO: Sale del context manager
        ENTONCES: Se hace rollback automático
        """
        pass

    def test_manual_rollback(session_factory):
        """
        DADO: Cambios en la session
        CUANDO: Llamo explícitamente a uow.rollback()
        ENTONCES: Los cambios no se persisten
        """
        pass

    def test_repositories_share_same_session(session_factory):
        """
        DADO: Dos repositories en el mismo UoW
        CUANDO: Uno hace flush
        ENTONCES: El otro ve los cambios (misma session)
        """
        pass
