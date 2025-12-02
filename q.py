words = [7, 5, 16, 24, 14, 14, 22, 24, 15, 10, 29, 24, 35, 13, 16, 16, 21, 25]

# Create a dictionary that counts how often each word appears
word_count = {}
for word in words:
    word_count[word] = word_count.get(word, 0) + 1

print("Word counts:", word_count)

# Create exactly 5 pairs (10 numbers) that balance out the distribution
from collections import Counter

# Create a list with all numbers (expanding by frequency)
all_numbers = []
for num, count in word_count.items():
    all_numbers.extend([num] * count)

# Select 10 numbers to create 5 pairs, trying to balance frequencies
# Strategy: Select numbers to maximize diversity and balance frequencies
selected = []
num_selection_count = Counter()

# Select 10 numbers, trying to balance how often each unique number is selected
for _ in range(10):
    # Find the number with highest frequency that hasn't been selected too much
    best_num = None
    best_score = float('-inf')
    
    for num in word_count.keys():
        # Score: prefer numbers with high frequency but low selection count
        # to balance the distribution
        if all_numbers.count(num) > num_selection_count[num]:
            score = word_count[num] - num_selection_count[num] * 2
            if score > best_score:
                best_score = score
                best_num = num
    
    if best_num is not None:
        selected.append(best_num)
        num_selection_count[best_num] += 1

# Track how many times each number has been used in pairs
pair_usage = Counter()

# Create 5 pairs trying to balance usage
pairs = []
remaining = selected.copy()

# Pair numbers to balance distribution
for _ in range(5):
    # Sort remaining by current usage in pairs (least used first)
    remaining.sort(key=lambda x: pair_usage[x])
    
    # Take the least used number
    first = remaining.pop(0)
    
    # Find a partner that balances the distribution
    best_partner = None
    best_score = float('inf')
    
    for i, num in enumerate(remaining):
        # Score: lower is better (prioritize low usage)
        score = pair_usage[num] * 2 + abs(pair_usage[first] - pair_usage[num])
        
        if score < best_score:
            best_score = score
            best_partner = i
    
    second = remaining.pop(best_partner)
    
    pairs.append((first, second))
    pair_usage[first] += 1
    pair_usage[second] += 1

print(f"\nSelected 10 numbers for 5 pairs: {selected}")
print("\n5 Balanced pairs:")
for i, pair in enumerate(pairs, 1):
    print(f"Pair {i}: {pair}")

print("\nUsage count per number in pairs:")
print(dict(pair_usage))

# Check distribution balance
if pair_usage:
    max_usage = max(pair_usage.values())
    min_usage = min(pair_usage.values())
    print(f"\nDistribution balance: min={min_usage}, max={max_usage}, difference={max_usage-min_usage}")
