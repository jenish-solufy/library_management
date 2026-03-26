# Library Management

Production-grade Library Management for ERPNext/Frappe, built to support both:

- schools, colleges, and universities
- independent, public, and private libraries

The app reuses ERPNext masters such as `Item`, `Customer`, `Student`, `Employee`, `User`, `Sales Invoice`, and `Payment Entry`, while adding only the library-specific doctypes needed for circulation and copy-level control.

## Architecture

### Reused ERPNext DocTypes

- `Item`: title/catalog master for books and other library materials
- `Customer`, `Contact`, `Address`, `User`: member identity and billing reuse
- `Student`, `Instructor`, `Employee`: education and staff linkage
- `Sales Invoice`, `Payment Entry`, `Journal Entry`: optional fine accounting
- `File`, `Communication`, `ToDo`, `Assignment`, `Notification`, `Workspace`, `Report`

### New DocTypes

- `Library Settings`: singleton configuration
- `Library Member Policy`: child table for category borrowing rules
- `Library Fine Rule`: child table for penalty rules
- `Library Membership Plan`: independent-library plan and fee structure
- `Library Shelf`: physical location hierarchy
- `Library Member`: unified borrower abstraction
- `Library Copy`: accession/barcode level inventory
- `Library Reservation`: title/copy-level queue and hold workflow
- `Library Transaction`: issue/return/renew/lost/damaged circulation lifecycle
- `Library Fine`: internal dues and optional accounting linkage

## Supported Modes

- `School`: student/staff/instructor-centric borrowing
- `Independent`: public/private library memberships
- `Hybrid`: both models enabled from the same app

Behavior is controlled from `Library Settings` and member-category policies.

## Key Features

- Title cataloging on top of `Item`
- Multiple copies/accessions per title
- Barcode and accession-based circulation
- Configurable borrowing limits, loan periods, grace period, and max renewals
- Title-level reservations and queue management
- Lost, damaged, under-repair, withdrawn handling
- Optional paid memberships, deposits, and accounting integration
- Reports, workspace, quick desk page, notifications, and demo data helpers

## Installation

From the bench root:

```bash
bench --site library.sahil.com install-app library_management
bench --site library.sahil.com migrate
```

ERPNext v16 already includes the Education domain, so no separate school app is required for the `Student`, `Instructor`, and `Employee` integrations used here.

## Configuration

1. Open `Library Settings`.
2. Select the operating mode: `School`, `Independent`, or `Hybrid`.
3. Configure borrowing policies by member category.
4. Enable or disable fines, deposits, paid memberships, and accounting integration.
5. Create shelves, membership plans, and library members.
6. Add library titles using `Item` and generate `Library Copy` records for each accession.

## Demo Data

Run either helper from bench:

```bash
bench --site library.sahil.com execute library_management.setup.demo.create_school_demo_data
bench --site library.sahil.com execute library_management.setup.demo.create_public_library_demo_data
```

## Tests

```bash
bench --site library.sahil.com run-tests --app library_management
```

## Notes

- Membership expiry blocks new issues but still allows returns and fine settlement.
- Reference-only materials cannot be issued.
- Renewals are blocked when another active reservation exists for the same title or copy.
- Fines can remain internal or flow into accounting depending on settings.

## License

MIT
