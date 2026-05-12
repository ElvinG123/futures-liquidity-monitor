-- Total volume by instrument
SELECT instrument, SUM(size) AS total_volume
FROM trades
GROUP BY instrument
ORDER BY total_volume DESC;

-- Average spread (liquidity quality)
SELECT instrument, AVG(spread) AS avg_spread
FROM trades
GROUP BY instrument;

-- Trades per minute (activity)
SELECT minute, COUNT(*) AS trade_count
FROM trades
GROUP BY minute
ORDER BY minute;

-- Notional traded per instrument
SELECT instrument, SUM(notional) AS total_notional
FROM trades
GROUP BY instrument;

-- Top participants by volume
SELECT participant, SUM(size) AS total_volume
FROM trades
GROUP BY participant
ORDER BY total_volume DESC;
