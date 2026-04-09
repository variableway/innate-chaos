# Macro Index Bugs

## Bug 1: database error for risk_score calculation

```
2026-04-09 07:44:39 [error    ] risk_score_calculation_error   error="(sqlalchemy.dialects.postgresql.asyncpg.Error) <class 'asyncpg.exceptions.DataError'>: invalid input for query argument $2: datetime.datetime(2026, 4, 1, 23, 44, 39... (can't subtract offset-naive and offset-aware datetimes)\n[SQL: SELECT prices.price \nFROM prices \nWHERE prices.asset = $1::VARCHAR AND prices.time >= $2::TIMESTAMP WITHOUT TIME ZONE ORDER BY prices.time ASC]\n[parameters: ('OIL', datetime.datetime(2026, 4, 1, 23, 44, 39, 335732, tzinfo=datetime.timezone.utc))]\n(Background on this error at: https://sqlalche.me/e/20/dbapi)"
2026-04-09 07:44:39 [error    ] regime_store_error             error='(sqlalchemy.dialects.postgresql.asyncpg.Error) <class \'asyncpg.exceptions.DataError\'>: invalid input for query argument $1: datetime.datetime(2026, 4, 8, 23, 44, 39... (can\'t subtract offset-naive and offset-aware datetimes)\n[SQL: INSERT INTO regime_history (time, regime, risk_score, factor_scores, description) VALUES ($1::TIMESTAMP WITHOUT TIME ZONE, $2::VARCHAR, $3::NUMERIC(5, 4), $4::JSONB, $5::VARCHAR)]\n[parameters: (datetime.datetime(2026, 4, 8, 23, 44, 39, 380363, tzinfo=datetime.timezone.utc), \'NEUTRAL\', 0.5, \'{}\', "Error calculating risk score: (sqlalchemy.dialects.postgresql.asyncpg.Error) <class \'asyncpg.exceptions.DataError\'>: invalid input for query argument ... (276 characters truncated) ... IL\', datetime.datetime(2026, 4, 1, 23, 44, 39, 335732, tzinfo=datetime.timezone.utc))]\\n(Background on this error at: https://sqlalche.me/e/20/dbapi)")]\n(Background on this error at: https://sqlalche.me/e/20/dbapi)'
2026-04-09 07:44:39 [info     ] risk_assessment_complete      
2026-04-09 07:44:54 [error    ] hyperliquid_http_error         error=
2026-04-09 07:44:54 [info     ] crypto_fetch_complete         
```

## Bug 2: Data is not available

1. data is not avaible for all, 
- GOLD data
- OILD data
- BTC/ETH DATA
- 利率数据 is not available too

please find a way to get the feature data from hyperliquide