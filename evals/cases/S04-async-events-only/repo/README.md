# Orders

The order service publishes past-tense events to a queue; subscribers project the lifecycle from the event stream. There is no `status` column — state exists only in the event log and a read model built by the projection.
