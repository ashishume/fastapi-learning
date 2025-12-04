# Rate Limiter Explanation: How the Sliding Window Works

## Overview

The rate limiter uses a **sliding window** algorithm to track requests over a time period. It stores each request's timestamp in Redis and only counts requests within the current window.

## How `current_time - window_seconds` Creates a Window

### Example Scenario

- **Current time**: 1000 seconds (Unix timestamp)
- **Window size**: 60 seconds
- **Max requests**: 5

### Step-by-Step Breakdown

#### 1. Calculate Window Start

```python
current_time = 1000  # Current Unix timestamp
window_seconds = 60   # 60-second window
window_start = 1000 - 60 = 940
```

**Visual Timeline:**

```
Past                    Present
|-----------------------|-------->
940                      1000
(window_start)        (current_time)
  |<------ 60 seconds ------>|
         (the window)
```

#### 2. What This Means

- **window_start (940)**: The oldest timestamp we care about
- **current_time (1000)**: The newest timestamp (right now)
- **Window**: All timestamps between 940 and 1000 (inclusive)

Any request with timestamp < 940 is **outside the window** and should be ignored.

#### 3. How Redis Stores Data

Redis uses a **sorted set (ZSET)** where:

- **Key**: `rate_limit:foods:{client_ip}`
- **Score**: The timestamp of each request
- **Value**: The timestamp (as string)

Example Redis data:

```
Key: rate_limit:foods:192.168.1.1
Score  | Value
-------|------
945    | "945"  ← Request at time 945
960    | "960"  ← Request at time 960
975    | "975"  ← Request at time 975
990    | "990"  ← Request at time 990
995    | "995"  ← Request at time 995
```

#### 4. Cleaning Old Entries

```python
await self.redis.zremrangebyscore(key, 0, window_start)
```

This command removes all entries with scores (timestamps) between 0 and 940.

**Before cleanup:**

```
Score  | Value
-------|------
900    | "900"  ← OLD (outside window, will be deleted)
920    | "920"  ← OLD (outside window, will be deleted)
945    | "945"  ← KEEP (within window)
960    | "960"  ← KEEP (within window)
975    | "975"  ← KEEP (within window)
```

**After cleanup:**

```
Score  | Value
-------|------
945    | "945"  ← Within window (940 to 1000)
960    | "960"  ← Within window
975    | "975"  ← Within window
```

#### 5. Counting Requests

```python
request_count = await self.redis.zcard(key)  # Count remaining entries
```

After cleanup, `zcard` counts only entries within the window (940 to 1000).

#### 6. Adding New Request

```python
await self.redis.zadd(key, {str(current_time): current_time})
```

Adds the current request timestamp (1000) to the sorted set.

**After adding:**

```
Score  | Value
-------|------
945    | "945"
960    | "960"
975    | "975"
990    | "990"
995    | "995"
1000   | "1000"  ← New request
```

## Real-World Example

### Timeline of Requests

Let's say it's **10:00:00 AM** (timestamp = 1000):

```
Time    | Timestamp | Action
--------|-----------|--------
9:58:30 | 910       | Request 1 (OLD - outside window)
9:59:15 | 955       | Request 2 (KEEP - within window)
9:59:45 | 985       | Request 3 (KEEP - within window)
10:00:00| 1000      | Request 4 (NEW - checking now)
```

### Calculation at 10:00:00

1. **current_time** = 1000
2. **window_start** = 1000 - 60 = 940
3. **Cleanup**: Remove timestamps < 940
   - Request 1 (910) is removed ❌
   - Request 2 (955) is kept ✅
   - Request 3 (985) is kept ✅
4. **Count**: 2 requests in window
5. **Check**: 2 < 5 (max_requests) → **ALLOW** ✅
6. **Add**: Add timestamp 1000
7. **New count**: 3 requests in window

### What Happens 10 Seconds Later?

At **10:00:10** (timestamp = 1010):

1. **current_time** = 1010
2. **window_start** = 1010 - 60 = 950
3. **Cleanup**: Remove timestamps < 950
   - Request 2 (955) is kept ✅
   - Request 3 (985) is kept ✅
   - Request 4 (1000) is kept ✅
4. **Count**: 3 requests in window
5. **Check**: 3 < 5 → **ALLOW** ✅

## Why "Going Back in Time" Works

The formula `current_time - window_seconds` calculates the **oldest timestamp we care about**:

- If current time is 1000 and window is 60 seconds
- We only care about requests from 940 to 1000
- Anything before 940 is "too old" and doesn't count
- By subtracting 60, we're defining the **left edge** of our sliding window

## Visual Representation

```
Timeline (moving forward):
<-- Past --|-- Window (60s) --|-- Future -->

At time 1000:
[940]==========[1000]-------->
  ↑              ↑
  |              |
window_start  current_time

At time 1010 (10 seconds later):
[950]==========[1010]-------->
  ↑              ↑
  |              |
window_start  current_time
(shifted forward)
```

The window **slides forward** as time progresses, always looking at the last 60 seconds from the current moment.

## Key Points

1. **Sliding Window**: The window moves forward in time, always covering the last N seconds
2. **Subtraction Creates Boundary**: `current_time - window_seconds` defines the oldest timestamp we count
3. **Automatic Cleanup**: Old entries are removed each time we check
4. **Efficient**: Only stores timestamps, not full request data
5. **Accurate**: Counts only requests within the current window
