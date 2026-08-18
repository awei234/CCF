# Abstract

Shows that the answer format itself causes hallucination. Asking thirteen models the same unanswerable question while changing only the answer format: in free text GPT-5.5 says there is no data 98% of the time, but given a required JSON field it invents an answer 40/40 times; required fields drive fabrication to 100% in ten of thirteen models. Releases PhantomFill with deterministic scoring and two reportable numbers: Coerced Fabrication Rate and Escape Utilization Rate; the tested fix is 'one line of schema' (an explicit escape option).
