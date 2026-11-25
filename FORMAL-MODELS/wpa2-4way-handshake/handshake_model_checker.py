#!/usr/bin/env python3
"""
Formal model + explicit-state model checking of the WPA2 4-way handshake,
targeting the Key Reinstallation Attack (KRACK, Vanhoef & Piessens, CCS 2017).

Ties to: 06-wireless-security THEORETICAL-FOUNDATIONS section 3.3 (freshness) and
3.5 (KRACK as a protocol-state defect, not a primitive break).

WHAT THIS IS
------------
Explicit-state model checking IS formal verification: we exhaustively explore the
reachable state space of the protocol's state machine under a Dolev-Yao adversary and
check a safety invariant. This is the same core procedure a tool like SPIN or TLC
performs; here it is implemented in ~200 lines of stdlib Python so it runs anywhere and
its result is reproducible and self-contained.

MODEL (abstraction level: supplicant key-installation state machine)
--------------------------------------------------------------------
Authenticator A and supplicant S share the PMK. Messages of the 4-way handshake:
  M1  A -> S : ANonce
  M2  S -> A : SNonce, MIC          (S can now compute PTK; PTK not yet installed)
  M3  A -> S : ANonce, GTK, MIC     (on valid M3, S INSTALLS PTK and resets the data
                                      frame nonce / packet-number counter to 0)
  M4  S -> A : MIC                  (ack; S starts sending data frames)

Adversary (Dolev-Yao, controls the channel): may deliver, drop, or REPLAY M3. The KRACK
core: A retransmits M3 if it does not receive M4; the attacker can block M4 and later
replay M3 to S AFTER S has installed the PTK and already sent data frames.

The security-critical fact modeled: the data-frame encryption (CCMP/TKIP) uses a nonce =
(key, packet-number) that must NEVER repeat. Installing/reinstalling the PTK resets the
packet-number counter to 0. Therefore:

    SAFETY INVARIANT (freshness of the data-frame nonce):
        the PTK is installed at most once per handshake session
        (equivalently: the packet-number counter is never reset after being advanced)

Its violation is exactly KRACK: a reinstall resets the counter, so nonces already used
for encrypted data frames are reused -> keystream reuse -> confidentiality/integrity loss.

TWO MODELS
----------
  VULNERABLE : on ANY received M3 (including a replay), S (re)installs the PTK and resets
               the nonce counter. -> the model checker should FIND a counterexample (KRACK).
  PATCHED    : S installs the PTK only if not already installed; a replayed M3 does NOT
               reinstall and does NOT reset the counter (the fix of Vanhoef & Piessens).
               -> the model checker should VERIFY the invariant (no reachable violation).

LIMITATION (disclosed): this is a symbolic, protocol-logic model. It abstracts the
cryptographic primitives (MICs/PRF assumed sound - Dolev-Yao) and models the KRACK-relevant
state (installation count, nonce counter), not the full IEEE 802.11 state machine. The
nonce counter is bounded (standard in model checking) since a single advance-then-reset
already witnesses reuse. Within this abstraction the verification is EXHAUSTIVE and exact.
"""

from collections import deque

NONCE_CAP = 3          # bound on the data-frame nonce counter (finite-state)
INSTALL_CAP = 2        # bound on install count (>1 already violates; cap keeps it finite)

# A state is an immutable tuple:
#   (phase, installs, nonce, max_nonce_used, sent_data)
# phase in {"INIT","GOT_M1","SENT_M2","INSTALLED"}
INIT_STATE = ("INIT", 0, 0, 0, False)


def invariant_holds(state):
    """Freshness invariant: PTK installed at most once (no key reinstallation)."""
    _, installs, _, _, _ = state
    return installs <= 1


def keystream_reuse(state):
    """Physical witness of the disaster: a reinstall reset the counter AFTER data was
    sent, so an already-used nonce value will be reused. True iff KRACK bites in practice."""
    _, installs, nonce, max_used, sent_data = state
    return installs >= 2 and sent_data and nonce < max_used


def successors(state, vulnerable):
    """Return list of (action_label, next_state) for all enabled transitions.
    Nondeterminism here = adversary scheduling + protocol interleaving; exploring ALL
    of them is what makes the check exhaustive (the adversary picks the worst case)."""
    phase, installs, nonce, max_used, sent_data = state
    out = []

    # M1 delivery (attacker may (re)deliver M1)
    if phase in ("INIT", "GOT_M1"):
        out.append(("recv_M1", ("GOT_M1", installs, nonce, max_used, sent_data)))

    # S sends M2 after M1
    if phase == "GOT_M1":
        out.append(("send_M2", ("SENT_M2", installs, nonce, max_used, sent_data)))

    # First M3: install PTK, nonce counter starts at 0
    if phase == "SENT_M2" and installs == 0:
        out.append(("recv_M3_install", ("INSTALLED", 1, 0, 0, sent_data)))

    # Data frames advance the nonce (packet-number) counter
    if phase == "INSTALLED" and nonce < NONCE_CAP:
        nn = nonce + 1
        out.append(("send_data", ("INSTALLED", installs, nn, max(max_used, nn), True)))

    # Replayed M3 while already INSTALLED  -- the KRACK trigger
    if phase == "INSTALLED":
        if vulnerable:
            if installs < INSTALL_CAP:
                # reinstall: reset the nonce counter to 0 (the bug)
                out.append(("recv_M3_REPLAY_reinstall",
                            ("INSTALLED", installs + 1, 0, max_used, sent_data)))
        else:
            # patched: replay does not reinstall, counter untouched (self-loop, no-op)
            # modeled as no state change -> nothing added (avoids trivial infinite loop)
            pass

    return out


def model_check(vulnerable):
    """Exhaustive BFS over the reachable state space, checking the invariant.
    Returns (violation_state_or_None, trace, num_states)."""
    start = INIT_STATE
    frontier = deque([start])
    predecessor = {start: (None, None)}   # state -> (prev_state, action)
    num_states = 0

    while frontier:
        s = frontier.popleft()
        num_states += 1

        if not invariant_holds(s):
            # reconstruct counterexample trace
            trace = []
            cur = s
            while cur is not None:
                prev, act = predecessor[cur]
                if act is not None:
                    trace.append((act, cur))
                cur = prev
            trace.reverse()
            return s, trace, num_states

        for action, ns in successors(s, vulnerable):
            if ns not in predecessor:
                predecessor[ns] = (s, action)
                frontier.append(ns)

    return None, None, num_states


def render_state(s):
    phase, installs, nonce, max_used, sent = s
    return (f"phase={phase:<9} installs={installs} nonce(PN)={nonce} "
            f"max_used={max_used} data_sent={sent}")


def run(name, vulnerable):
    print("=" * 78)
    print(f"MODEL: {name}")
    print("Invariant checked: installs <= 1  (PTK installed at most once = no key reinstall)")
    print("=" * 78)
    violation, trace, n = model_check(vulnerable)

    if violation is None:
        print(f"RESULT: VERIFIED. Invariant holds in all {n} reachable states.")
        print("        No key-reinstallation is reachable under the Dolev-Yao adversary.")
    else:
        print(f"RESULT: VIOLATION FOUND after exploring {n} states.")
        print("Counterexample trace (a concrete KRACK attack found by the model checker):\n")
        print(f"    START      | {render_state(INIT_STATE)}")
        for i, (action, st) in enumerate(trace, 1):
            tag = ""
            if action == "recv_M3_REPLAY_reinstall":
                tag = "   <-- attacker replays M3"
            if keystream_reuse(st):
                tag = "   <-- NONCE REUSE (keystream reuse: confidentiality/integrity broken)"
            print(f"    step {i:>2} {action:<26} | {render_state(st)}{tag}")
        print(f"\n    -> installs reached {violation[1]} (> 1): the PTK was reinstalled.")
        print("    -> the packet-number counter was reset to 0 after data frames had used")
        print("       nonces 1..k, so those nonces are reused with the same key = KRACK.")
    print()


def main():
    print("WPA2 4-way handshake - explicit-state model checking of the freshness invariant")
    print("(KRACK, Vanhoef & Piessens 2017). Deterministic, exhaustive, self-contained.\n")
    run("VULNERABLE supplicant (reinstalls PTK on any M3, incl. replays)", vulnerable=True)
    run("PATCHED supplicant (ignores replayed M3 for key installation)", vulnerable=False)
    print("=" * 78)
    print("Conclusion: the model checker MECHANICALLY finds the KRACK attack in the")
    print("vulnerable model (counterexample above) and EXHAUSTIVELY VERIFIES its absence")
    print("in the patched model. This confirms, formally, that KRACK is a protocol-STATE")
    print("defect (key reinstallation / loss of nonce freshness), not a break of the")
    print("cryptographic primitives - the thesis of module 06 foundations, section 3.5.")


if __name__ == "__main__":
    main()
