
Defining a Monitoring Algorithm
*******************************

Monitoring algorithms are the combination of three sub-algorithms :

1. A Screening algorithm, that processes the available data and outputs description parameters of this data.
2. A Triggering algorithm that analyses the description parameters and returns a binary decision, regarding the necessity to go verify the data in reported in a given reported.
3. A Supervision algorithm, that describes the concrete implementation of the monitoring in the field.

The combination of these three elements uniquely define a monitoring strategy for a program. At each steps, the facility objects are updated to include the values of the supervision paraemters, and the result of the trigger algorithm.

The Screening algorithms input can be classified along two dimentsions :

1. Longitudinal vs Transversal :
    * Longitudinal data : Using only one facility, the algorithm considers the past validated values and infers the characteristics of the next expected values.
    * Transversal data : Using a group of facilities, the algorithm compares the different facilities performances and their values.
2. Simple reports vs Validation trail :
    * Simple reports : The algorithm uses only the values previously validated in the facilities.
    * Validation trails : The algorithm uses both the reported values and the validated values.

We need to specify these two dimensions when initiating the algorithm object, to orient the pre-processing of the data. The inputed data is then processed to form an appropriate training set that can be fed in the Screening algorithm.

.. autoclass:: monitoring_algorithms.algorithms_definition.monitoring_algorithm
    :members: monitor , trigger_supervisions, make_training_set, simulate_implementation

.. autofunction:: monitor
.. autofunction:: make_training_set
.. autofunction:: trigger_supervisions
.. autofunction:: simulate_implementation
