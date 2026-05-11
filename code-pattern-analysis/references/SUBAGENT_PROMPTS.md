# Subagent Prompts

Use these prompts when delegating read-only pattern analysis. Replace `<repo>` with the absolute repository root and `<scope>` with the target directory (or "entire repository" if unscoped).

## Naming & Formatting

Read `<repo>` only (scope: `<scope>`). Analyze naming and formatting conventions:

- Variable naming (camelCase, snake_case, PascalCase, SCREAMING_SNAKE)
- Function/method naming patterns
- Class/type/interface naming
- File and directory naming (kebab-case, camelCase, PascalCase, etc.)
- Constants naming
- Boolean naming (is/has/should prefixes)
- Formatting: indentation (tabs vs spaces, width), trailing commas, semicolons, quote style
- Any linter/formatter config files (.eslintrc, .prettierrc, rustfmt.toml, etc.)

For each pattern found:
- Cite file paths as examples
- Count how many files follow the pattern vs deviate
- Flag conflicts where multiple conventions coexist
- Note if a formatter/linter enforces the pattern
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.

## File & Project Structure

Read `<repo>` only (scope: `<scope>`). Analyze file and project organization:

- Directory structure philosophy (by feature, by layer, by type)
- Module boundaries and how they're enforced
- Barrel files / index re-exports
- Co-location patterns (tests next to source, styles next to components)
- Shared/common directories and their purpose
- Entry points and their organization
- Config file locations and patterns
- Generated vs authored code separation

For each pattern found:
- Cite directory paths and examples
- Note the dominant organizational philosophy
- Flag inconsistencies between directories
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.

## Imports & Dependencies

Read `<repo>` only (scope: `<scope>`). Analyze import and dependency patterns:

- Import ordering (stdlib, external, internal, relative)
- Path aliases vs relative imports
- Named vs default exports/imports
- Dependency injection patterns
- Circular dependency avoidance strategies
- External dependency management (pinning, ranges, lock files)
- Internal module boundaries (what imports what)
- Re-export patterns

For each pattern found:
- Cite file paths as examples
- Count adherence vs deviation
- Flag conflicts or inconsistencies
- Note if enforced by tooling (eslint import rules, etc.)
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.

## Error Handling & Control Flow

Read `<repo>` only (scope: `<scope>`). Analyze error handling and control flow:

- Try/catch strategies (granular vs broad, where they live)
- Error types/classes (custom errors, error codes, Result types)
- Early return / guard clause patterns
- Null/undefined handling (optional chaining, nullish coalescing, explicit checks)
- Async error handling (Promise rejection, async/await try/catch)
- Logging and error reporting patterns
- Retry/fallback patterns
- Validation approaches (where, how, what libraries)

For each pattern found:
- Cite file paths as examples
- Count adherence vs deviation
- Flag conflicts or inconsistencies
- Note if patterns differ by layer (controllers vs services vs utils)
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.

## API & Interface Design

Read `<repo>` only (scope: `<scope>`). Analyze API and interface design patterns:

- Function signature patterns (parameter count, options objects, overloads)
- Return type conventions (raw values, wrapper objects, tuples)
- Abstraction layers and their boundaries
- Public vs internal API separation
- Interface/type design (narrow vs wide, composition vs inheritance)
- Builder/factory patterns
- Configuration patterns (env vars, config objects, feature flags)
- Versioning or compatibility patterns

For each pattern found:
- Cite file paths as examples
- Count adherence vs deviation
- Flag conflicts or inconsistencies
- Note the apparent rationale where visible
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.

## State & Data Patterns

Read `<repo>` only (scope: `<scope>`). Analyze state management and data patterns:

- State management approach (global store, context, local state, signals)
- Data flow direction (unidirectional, event-driven, pub/sub)
- Immutability conventions (spread, immer, freeze, readonly types)
- Type definitions (interfaces vs types, where they live, shared vs local)
- Data transformation patterns (mappers, serializers, DTOs)
- Caching strategies
- Database access patterns (ORM, raw queries, repository pattern)
- Schema/validation libraries and where they're applied

For each pattern found:
- Cite file paths as examples
- Count adherence vs deviation
- Flag conflicts or inconsistencies
- Note if patterns differ by domain area
- Confidence level: high/medium/low

Avoid secrets. Separate observed conventions from recommendations.
