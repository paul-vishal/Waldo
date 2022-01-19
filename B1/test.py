s = ['a', 'b', 'c', 'd', 'e']
sliding_window = 2

for i, w in enumerate(s):
    left_context = s[i - sliding_window:i]
    right_context = s[i+1:i + 1 + sliding_window]
    #print(s[i + 1 + sliding_window])
    print(w, left_context, right_context)
