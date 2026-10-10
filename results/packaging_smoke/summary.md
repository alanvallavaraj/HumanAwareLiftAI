# Experiment Results Summary

## Controller Means

| controller | runs | mean_wait | p95_wait | mean_journey | failed_pickup_rate | unnecessary_stop_rate | door_crowding_rate | energy_proxy | utilisation_imbalance | special_mean_wait | fairness_disparity | stability_risk | jerk_exposure | score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_aware | 4 | 87.0291 | 189.2500 | 4.4323 | 0.0000 | 0.0342 | 0.0000 | 7.1920 | 0.7410 | 68.6036 | 0.8847 | 1.0007 | 5.2151 | 157.9347 |
| collective | 4 | 90.4424 | 185.3875 | 4.4342 | 0.0000 | 0.0287 | 0.0000 | 7.6738 | 1.1133 | 57.8429 | 1.2823 | 0.9730 | 5.6990 | 160.1495 |
| occupancy_aware | 4 | 98.8959 | 209.9125 | 4.5095 | 0.0000 | 0.0480 | 0.0000 | 7.1010 | 1.1771 | 73.0429 | 1.3098 | 0.9835 | 5.7880 | 177.6115 |

## Human-Aware Pairwise Win Rates

| baseline | matched_cases | mean_wait | p95_wait | mean_journey | failed_pickup_rate | unnecessary_stop_rate | door_crowding_rate | energy_proxy | utilisation_imbalance | special_mean_wait | fairness_disparity | stability_risk | jerk_exposure | score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| collective | 4 | 0.500 | 0.250 | 0.500 | 0.000 | 0.250 | 0.000 | 0.500 | 0.500 | 0.500 | 0.750 | 0.500 | 0.750 | 0.250 |
| occupancy_aware | 4 | 1.000 | 0.500 | 0.500 | 0.000 | 0.500 | 0.000 | 0.250 | 0.500 | 0.750 | 0.750 | 0.500 | 0.750 | 0.750 |