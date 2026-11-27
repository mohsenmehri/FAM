"""Educational Python mock: no Terraform provider, network or device is invoked."""
from copy import deepcopy


def refresh_only_plan(state, observed):
    """Propose an updated state, without modifying state or observed objects."""
    return {"before": deepcopy(state), "after": deepcopy(observed)}


def refresh_only_apply(plan):
    """Return a new simulated state; do not change the observed objects."""
    return deepcopy(plan["after"])


def normal_plan(desired, observed):
    """Return field-level differences after a simplified successful refresh."""
    return {key: {"observed": observed.get(key), "desired": desired.get(key)}
            for key in sorted(desired.keys() | observed.keys())
            if observed.get(key) != desired.get(key)}


def main():
    desired = {"name": "lab", "vlan": 10}
    previous_state = {"name": "lab", "vlan": 10}
    observed = {"name": "lab", "vlan": 20}  # imagined external change
    refresh_plan = refresh_only_plan(previous_state, observed)
    refreshed_state = refresh_only_apply(refresh_plan)
    print("refresh-only proposed state:", refresh_plan["after"])
    print("state after mock apply:", refreshed_state)
    print("observed object unchanged:", observed)
    print("normal plan against desired:", normal_plan(desired, observed))


if __name__ == "__main__":
    main()
