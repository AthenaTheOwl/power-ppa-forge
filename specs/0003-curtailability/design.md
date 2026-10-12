# Spec 0003 design

`scenarios/v0_1gw_3offtakers_curtail.json` is the canonical three-offtaker
scenario with harbor_cloud 0.3 curtailable over stress hours 17-20 at a
curtailment weight of 10 (notional). Its run is committed under
`runs/v0_curtail`. Each winner pays its critical value under the full
score, curtailment credit included (DEC-PPF-003). v0 prices the promise
to shed; it does not check delivery.
