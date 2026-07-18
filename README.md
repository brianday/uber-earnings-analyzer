# Uber Earnings Analyzer MCP Server

A Python and Model Context Protocol project that lets an AI client analyze Uber driver earnings data through structured MCP tools.

The server can answer questions such as:

- Which days generated the most earnings?
- Which clock hours produced the most earnings?
- How did the latest week compare with the previous week?
- What trends appear across recent weeks?

The project supports both a bundled fictional sample dataset and private Uber driver payment exports.

## Project Goals

This project was built as a practical introduction to:

- Python application development
- Data cleaning and analysis with pandas
- Model Context Protocol server development
- MCP tool design and structured responses
- Automated unit and integration testing
- Git branches and pull-request workflows
- Safe handling of private personal data

## Features

- Loads normalized sample earnings data
- Loads real Uber driver payment exports
- Aggregates multiple payment components into net earnings per trip
- Calculates daily earnings totals and trip counts
- Groups earnings by clock hour
- Compares the latest two Monday-to-Sunday calendar weeks
- Produces configurable multiweek earnings trends
- Exposes analysis functions as MCP tools
- Uses fictional sample data by default
- Supports private data through an environment variable
- Includes unit tests and MCP integration tests
- Keeps private exports out of Git

## MCP Tools

### `get_earnings_by_day`

Returns daily earnings totals and trip counts, ordered from highest to lowest earnings.

### `get_earnings_by_hour`

Returns earnings grouped by clock hour using a 24-hour clock.

Each result includes:

- Total earnings
- Average earnings per trip
- Trip count

This measures earnings generated during each clock hour. It does not claim to measure earnings per hour online.

### `compare_weeks`

Compares the latest Monday-to-Sunday calendar week in the dataset with the preceding week.

The result includes:

- Week boundaries
- Earnings totals
- Trip counts
- Dollar change
- Percentage change

### `get_weekly_earnings_trend`

Returns recent weekly earnings totals in chronological order.

The tool accepts an optional `weeks` argument and includes:

- Week start and end dates
- Total earnings
- Trip count
- Dollar change from the preceding returned week
- Percentage change

## Technology Stack

- Python 3.13
- pandas
- Model Context Protocol Python SDK
- FastMCP
- pytest
- uv
- Git and GitHub
- MCP Inspector

## Project Structure

```text
uber-earnings-analyzer/
|-- data/
|   |-- raw/
|   |   `-- .gitkeep
|   `-- sample/
|       `-- sample_earnings.csv
|-- src/
|   `-- uber_earnings_analyzer/
|       |-- __init__.py
|       |-- analyzer.py
|       |-- data_loader.py
|       `-- server.py
|-- tests/
|   |-- test_analyzer.py
|   |-- test_data_loader.py
|   `-- test_server.py
|-- .gitignore
|-- .python-version
|-- pyproject.toml
|-- README.md
`-- uv.lock
```

## Data Model

The normalized internal earnings table contains:

```text
trip_datetime
earnings
```

Uber stores several payment components for a single trip, potentially including fares, tips, incentives, adjustments, service fees, and commissions.

The Uber export loader groups rows by `Trip UUID` and sums every associated `Local Amount`. This produces the driver's net earnings for each trip without relying on a hard-coded list of payment classifications.

## Privacy

Private Uber files must be placed in:

```text
data/raw/
```

That directory is protected by `.gitignore`.

The public repository must never include:

- Real trip identifiers
- GPS coordinates
- IP addresses
- License plate information
- Private payment exports
- Personal account information

The bundled sample CSV contains fictional values and is safe to publish.

## Installation

### Prerequisites

Install:

- Python 3.13 or newer
- Git
- Node.js and npm
- uv

Clone the repository:

```powershell
git clone https://github.com/brianday/uber-earnings-analyzer.git
cd uber-earnings-analyzer
```

Install the project and dependencies:

```powershell
uv sync
```

## Run the Tests

```powershell
uv run pytest -v
```

The test suite covers:

- Normalized CSV loading
- Missing and malformed files
- Uber payment-component aggregation
- Currency validation
- Timestamp consistency
- Daily and hourly calculations
- Weekly comparisons
- Weekly trends
- MCP tool discovery
- MCP tool responses and input arguments

## Run with Sample Data

The server uses the bundled fictional sample dataset by default.

Launch it through an MCP-compatible client or MCP Inspector. A stdio MCP server is not an interactive terminal program and waits for JSON-RPC messages from a client.

## Test with MCP Inspector

From the project directory, run:

```powershell
npx @modelcontextprotocol/inspector uv run uber-earnings-analyzer
```

In the Inspector:

1. Connect using the STDIO transport.
2. Open the Tools section.
3. Confirm that all four tools are listed.
4. Select a tool.
5. Supply an argument when required.
6. Run the tool and inspect its structured response.

## Run with a Private Uber Export

Place the Uber driver payments CSV inside:

```text
data/raw/
```

Set the environment variable for the current PowerShell session:

```powershell
$env:UBER_EARNINGS_CSV = (
    Resolve-Path "data\raw\driver_payments-0.csv"
).Path
```

Then launch the server through MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector uv run uber-earnings-analyzer
```

Remove the environment variable to return to sample data:

```powershell
Remove-Item Env:UBER_EARNINGS_CSV -ErrorAction SilentlyContinue
```

## Data Quality Decisions

The Uber data download included payments, trips, ratings, and driver-app analytics.

The payments export was selected as the authoritative earnings source because:

- Every payment row had a trip identifier.
- Components belonging to one trip shared a consistent timestamp.
- Positive fare components and negative fees could be combined into net trip earnings.
- The data supported reliable daily, clock-hour, weekly, and trend calculations.

The project also investigated whether driver-app analytics could support earnings per online hour. After converting UTC analytics events to local time and reconstructing online sessions, those sessions covered only 64.29% of trips in the overlapping period.

Because the source was not sufficiently reliable, the project intentionally does not expose earnings per online hour. This avoids presenting an inaccurate estimate as fact.

## Testing Strategy

### Unit tests

Unit tests validate individual components such as:

- CSV loaders
- Payment aggregation
- Daily and hourly calculations
- Weekly comparisons
- Weekly trend calculations

### MCP integration tests

Integration tests create an in-memory MCP client and server session to verify that:

- Tools can be discovered
- Tools can be called through MCP
- Structured results are returned correctly
- MCP input arguments are processed correctly

The MCP tests force the public sample dataset so results remain deterministic even when a developer has configured a private export locally.

## Git Workflow

Development used:

- Feature branches
- Descriptive commits
- GitHub pull requests
- Squash merges
- Automated tests before merging

Major features were developed through pull requests for:

- Weekly comparison and private Uber export support
- Weekly earnings trend analysis

## What I Learned

Through this project, I learned how to:

- Structure a packaged Python application
- Manage Python versions and dependencies with uv
- Clean and validate CSV data with pandas
- Aggregate payment components into net trip earnings
- Build MCP tools with FastMCP
- Return structured data through an MCP server
- Test MCP tools using an in-memory client session
- Protect private data using environment variables and `.gitignore`
- Investigate data quality before implementing a metric
- Use branches and pull requests for feature development

## Future Improvements

Potential additions include:

- Date-range arguments for daily and hourly tools
- Monthly and yearly summaries
- Earnings by day of week
- Exportable reports
- Charts or a separate dashboard
- Support for additional currencies
- A validated way to combine trip distance and duration with earnings
- Continuous integration with GitHub Actions

## License

This repository is provided as a portfolio and educational project.