# ENHSP Wrapper

This is a simple wrapper for the ENHSP planner. For most use cases of ENHSP in Python, you should look at [unified-planning](https://github.com/aiplan4eu/unified-planning) instead. This package does not automatically stay updated with the latest version of ENHSP. The version of ENHSP used in this package is 20-0.10.0 (this number may not even be correct if I forget to update it!), and is likely out-dated when you read this file.

If, for some reason, unified-planning does not work for you, then you may find this ENHSP wrapper useful. Unlike unified-planning, this wrapper does not try to parse the problem before passing it onto ENHSP. This is likely only useful if you are using a PDDL syntax that ENHSP supports, but unified-planning does not.

In addition to just wrapping the ENHSP planner, we also provide an interface for retrieving the [disjunctive/additive landmarks](https://www.ijcai.org/proceedings/2017/0612.pdf) from ENHSP without needing CPLEX installed.
