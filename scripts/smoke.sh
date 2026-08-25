#!/usr/bin/env bash
# Proves a service actually boots and does its job. Unit tests passing does not
# mean the service runs. Assert your own lex rules here, not just a happy path.
#
# Honest state (2026-08-22): no service exists yet, so there is nothing to boot.
# This script deliberately does NOT fake a passing smoke test — it says so and
# exits non-zero, because a smoke test that always "passes" for a service that
# doesn't exist is exactly the kind of fake evidence meta/lex/definition-of-done.md
# exists to prevent.
#
# Rewrite this file the day the first service exists. At minimum it should:
#   1. Start the service and poll its health endpoint until healthy (or timeout).
#   2. Send a real request against a real endpoint and assert on the response.
#   3. Assert one of THIS BRAIN'S OWN lex rules holds, not just a happy path —
#      e.g. send two identical maker+checker approval attempts from the same
#      user and assert the second is rejected (meta/lex/maker-checker-segregation.md),
#      or submit an amount through money-handling code and assert no float
#      drift across repeated operations (meta/lex/money-decimal-jod.md).
set -uo pipefail

SVC=${1:-}
if [ -z "$SVC" ]; then
  echo "  usage: smoke.sh <service>"
  exit 1
fi

echo "  smoke.sh: no service named '$SVC' exists yet — there is no codebase."
echo "  This is the honest result, not an error to suppress. See the header of"
echo "  this file for what to implement the day '$SVC' exists."
exit 1
