# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2022-06-12

### Added

- Password change endpoint.
- Version information endpoint.
- Add performance and snapshot services.
- Stocks can be added and removed to/from watchlists.
- Watchlist item target API.
- Add cash percentage calculation to current strategy endpoint.
- Add pagination to listing endpoints.

### Changed

- Change authentication method from token auth to JWT auth.
- Send latest price information instead of description in stock listing endpoint.

### Removed

- Remove `gross_capital_deployed` from portfolio indicators.

### Fixed

- Can fetch portfolio with a stock that has no price info.
- Can delete stock portfolio with attached transactions.

## [1.1.0] - 2022-04-19

### Added

- Postman API documentation.

### Changed

- Unify API format to use snake_case in query params and payload properties.

### Fixed

- The user can fetch individual portfolios for a previous date.

### Security

- General user can't fetch another user's portfolio.

## [1.0.0] - 2022-03-23

### Added

- Setup project structure and basic devops utilities.
- Role-based authorization process.
- Database models for core stock data.
- Stock related endpoints.
- Activated basic built-in login.
- Database models for raw data.
- Raw data sync endpoints.
- Database models for transactions.
- Transactions endpoints.
- Database models for asset allocation strategies.
- Asset allocation strategy endpoints.
- Portfolio indicator endpoints.
