# Фаззинг-тестирование

В проекте фаззинг-тестирование реализовано на Python с помощью `pytest` и `Hypothesis`.

Проверяются три типа некорректных данных:

- случайные недопустимые роли пользователя вместо `admin`, `manager`, `clerk`;
- отрицательные значения остатка товара;
- случайные SKU, не соответствующие формату `A-Z`, `0-9` и `-`.

Команда запуска в Docker:

```bash
docker compose exec api python tools/fuzz_report.py
```

Ожидаемый результат:

```text
Test Suites: 4 passed, 4 total
Tests:       8 passed, 8 total
Snapshots:   0 total
Time:        7.78 s, estimated 8 s
Ran all test suites.
```

Фаззинг-тесты находятся в `backend/tests/test_fuzz_validation.py`.
