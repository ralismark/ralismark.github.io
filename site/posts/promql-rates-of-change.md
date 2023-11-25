---
layout: post
title: Which Prometheus rate of change function to use?
excerpt: "rate, irate, delta, deriv, increase, and idelta: what do they mean?"
date: 2023-03-17
tags:
---

Prometheus has a large number of PromQL functions all of which roughly mean "rate of change".
This makes it easier to get the exact kind of rate you want, but also makes it confusing to pick between.
So I've made a table.

<!--more-->

||Counter<br>(non-decreasing)|Gauge<br>(up and down)|
|-
|**Average slope in time period**|[rate()]|[deriv()]|
|**Difference between last two samples**|[irate()]|[idelta()]|
|**Last sample minus first sample**|[increase()]|[delta()]|

[delta()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#delta
[deriv()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#deriv
[idelta()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#idelta
[increase()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#increase
[irate()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#irate
[rate()]: https://prometheus.io/docs/prometheus/latest/querying/functions/#rate

The two column correspond to the two metric types:

1. **Counters** only go up, except when your task restarts and they reset to 0.
	Functions for this account for resets, and give only non-negative values.
2. **Gauges** are a measurement of a value, and a task restart might cause a jump and might not.

And the rows correspond to what value you want:

1. **Average slope in time period** is the standard "rate of change".
	Notably, [deriv()] does a linear regression so the effect of outliers/volatility is reduced.
2. **Difference between last two samples** is essentially the instantaneous derivative for gauges, and for counters is the number of counts that happened "at this time".
	I like using this with Grafana's state timelines to plot instances of low-occurrence event.
3. **Last sample minus first sample** can be used to the actual change over a time period, such as how many counts happened in the last 24 hours.
