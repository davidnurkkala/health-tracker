# Cadence

A personal web app for pacing indulgences on a fixed cadence, with a weight
trend underneath. `index.html` is the whole app — vanilla JS, no build step, no
network. The manifest, service worker and icons around it exist only to make it
installable; the app does not depend on them.

## Settled design decisions — don't reopen without a reason

These are the constraints the app exists to enforce. They are not visible from
the code, and several of them look like missing features until you know why they
are missing.

**It is a cooldown, not a currency.** The original idea was a token economy —
earn credit by exercising, spend it on food. That was deliberately cut. Nothing
is earned, there is no balance, and there is no way to argue your way into more.
The whole point is that the decision is made in advance, while calm, rather than
negotiated in the moment. Any feature that lets good behavior buy indulgences
reintroduces exactly the problem this design removes.

**Three tiers, not four.** Every tier boundary is a judgment call made while
hungry. Fewer boundaries, less drift.

**Round-up rule.** Anything between two tiers is charged as the bigger one.
This is the single most important line in the design — it removes the judgment
call and biases it against the user by default. It used to be printed above the
tiles; the owner removed the explanatory copy, so the rule now lives here and in
his head rather than on screen. It still governs how tiers are charged.

**Overage borrows forward.** Going over drops the balance negative and it
refills from there. There is no penalty, no streak to break, no "ruined week."
All-or-nothing rules are the failure mode being designed against, so the overage
path has to be boring and survivable.

**No carryover.** The max-held cap is the mechanism. Unused allowance evaporates
rather than accumulating, because an accumulating balance is a currency again.

**7-day trailing average is the headline number.** Daily readings render as
faint dots behind it. Day-to-day weight noise is a couple of kg on water alone
and reacting to it is how people quit.

**Recalibrate monthly, not weekly.** The "Adjust cadence" panel is intended to
be touched against the 30-day delta. Anything faster turns the cadence into a
negotiation.

**The if-then field is not decoration.** The buttons can't do anything about a
bad day. That field is where the substitute behavior gets written down in
advance.

**The UI carries no explanatory copy.** Purpose, rationale and coaching notes
were deliberately stripped — the owner built the thing and does not need it
narrated back. Labels, values and controls only. Don't reintroduce helper text.

**Nothing that awards, scores, streaks, or congratulates.**

## Deploy

Pushing to `main` deploys the repo root to GitHub Pages, at
<https://davidnurkkala.github.io/health-tracker/>.

Pages must be switched on once by hand, under **Settings → Pages → Source:
GitHub Actions**. There is no way to automate it: the Actions token is not
permitted to create a Pages site. Until it is set, every run fails at
`configure-pages` with "Get Pages site failed".
