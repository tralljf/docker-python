CREATE DATABASE IF NOT EXISTS crypto;
use crypto;

CREATE TABLE IF NOT EXISTS PRICES (
    sell_rate decimal(14,2),
    buy_rate decimal(14,2),
    sell_book varchar (100),
    buy_book varchar (200),
    exchange varchar (200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
