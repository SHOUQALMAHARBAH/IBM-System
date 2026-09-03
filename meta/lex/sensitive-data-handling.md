# Lex: Sensitive Data Handling

**Enforcement level: mandatory — no exceptions.**

## Rule

Data classified **Highly Confidential** under the organization's four-tier model (`PRIV-STD-02`; canonical, not an IBMS-specific scheme — see `meta/designs/2026-08-pcms-source-of-truth.md`) is never logged, never exported unencrypted, never emailed in plain text, and never displayed unmasked outside a justified drill-down. This tier covers: medical reports and clinical claim details, bank account/payment card data, scanned national ID images, and UBO/beneficiary data for life & health claims. Log identifiers instead: `customer.id`, `policy.id`, `claim.id`.

A file or record combining multiple classification levels is classified and protected at the **highest** level present — never averaged (`PRIV-STD-02` §6.7). A claim file containing a policy application (Confidential) and a medical report (Highly Confidential) is a Highly Confidential file, full stop.

## What triggers this rule

- Any logging call (`logger.*`, `console.log`, `print`) interpolating a national ID number, bank/payment field, medical/health field, or a raw request/response/webhook payload from claims or KYC intake
- Exception handlers and middleware logging request/response bodies on error — the exact failure mode called out in Part 10.6 and mirrored by the M08 rule that Highly Confidential data cannot use an unencrypted channel
- Any export, print, or download feature touching a Highly Confidential field without watermarking/DLP controls (Part 10.6)
- Any data share (M08 — `meta/context/pcms-privacy-modules.md`) where the picked channel is not on the approved secure-channel list for that classification
- List views showing a full national ID, full card number, or full bank account number instead of a masked value
- A free-text "note" / "detail" / "reason" field sitting next to a masked-data path being left as the *de facto* capture point for that data class. If the system holds bank/card data only as a masked reference (e.g. `PaymentChannel.accountLast4`, Process 38), a free-text field that a user could reasonably type a full account/card number into (a "change my payment details" service request, a refund reason, a claim note) must carry an input guard that rejects a full number and steers the user to the masked, governed path. The structured masked record is the capture point; the note field is not.

## What does NOT trigger this rule

- Structured fields that are IDs only
- Local development logging behind an explicit debug flag, and never against production data
- The classification tier itself appearing in logs/UI (e.g., logging that a document *is* "Highly Confidential" is fine — logging its *content* is not)
- Public and Internal tier data (marketing brochures, aggregate non-client reports)

## How it is enforced

**Hook:** `.claude/hooks/enforce-sensitive-data.sh` — `PreToolUse` on `Write|Edit`, exits 2 on a logging call interpolating a variable whose name matches `national_id|nationalId|bank_account|card_number|cvv|medical|health_report|clinical`. Tune the keyword list to the real field names in the data dictionary (`PRIV-SRS-02_Data_Dictionary_and_Entity_Model.xlsx`) once schema design starts.

**Review gate:** `@code-reviewer` is mandatory on any code touching claims documentation, KYC document capture, or payment/bank data (see `CLAUDE.md` § Agents). This review also checks that any new free-text field adjacent to a masked-data path carries the "no full account/card number" input guard described above — a regex rejecting a long digit run is the minimum, with an error message that names the governed masked path (`PaymentChannel` for payment details).

## Rationale

This is not a style preference — it is the direct system implementation of `PRIV-STD-02`'s four-tier classification and the M08 rule in `PRIV-SRS-01` that "sharing of Highly Confidential data via an unencrypted channel cannot be marked as the approved method; the system's channel picklist excludes non-secure options for that classification." A logging pipeline is exactly such an unencrypted, wide-retention, wide-access channel — Part 10.3 explicitly requires that read access to Sensitive Personal Data be logged for PDPL accountability, which only means something if the data itself never lands in the log in the first place.
