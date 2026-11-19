def route_human_review(state):
    decision = state.get("human_decision")

    if decision is True:
        return "proceed"

    if decision is False:
        return "reject"

    raise ValueError("Human decision is missing")