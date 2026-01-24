This PR implements the User Selector MVP (no auth).

Summary:
- Add `UserProvider` context and `useActiveUser()` hook (default user_id = 1)
- Add `UserSelector` dropdown in header (loading/empty states)
- Integrate `activeUserId` across main pages and hooks (Projections, Purchases, Budgets, Statements, Exchange Rates, Payment Methods, Credit Cards, Edit Purchase, etc.)
- Add unit tests for `UserContext`
- Add "Actualizar" button to Purchases page to manually refetch purchases for the active user
- Update documentation (`feature-5-user-selector.md`, frontend README)

Notes:
- Queries are keyed by `activeUserId` so changing the dropdown triggers refetches.
- Kept state ephemeral (no localStorage) as per spec.
- Typecheck/build passes locally.

Please review: tests, integration points, and the UI placement of the selector/button.
